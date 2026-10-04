"""Enforce public GET routes, pinned public addresses, and collection budgets."""

import hashlib
import http.client
import ipaddress
import json
import signal
import socket
import ssl
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, urlsplit

from .records import SourceError

MAX_BYTES = 100_000_000
MAX_REQUESTS = 500
MAX_SECONDS = 1800
MAX_PAGE_BYTES = 12_000_000


def safe_addresses(host, resolver=socket.getaddrinfo):
    """Reject nonpublic address sets before establishing a connection."""
    addresses = list(dict.fromkeys(row[4][0] for row in resolver(host, 443)))
    if not addresses or any(not ipaddress.ip_address(address).is_global
                            or ipaddress.ip_address(address).is_multicast
                            for address in addresses):
        raise SourceError("nonpublic network destination")
    return sorted(addresses, key=lambda value: ":" in value)


class PinnedHTTPS(http.client.HTTPSConnection):
    """Connect to one checked address while verifying the original hostname."""

    def __init__(self, host, address, timeout):
        self.tls_context = ssl.create_default_context()
        super().__init__(host, port=443, timeout=timeout, context=self.tls_context)
        self.address = address

    def connect(self):
        self.sock = socket.create_connection((self.address, 443), self.timeout)
        self.sock = self.tls_context.wrap_socket(self.sock, server_hostname=self.host)


@contextmanager
def deadline_guard(seconds):
    """Bound DNS lookup, TLS setup, and body reads on Linux."""
    previous = signal.getsignal(signal.SIGALRM)

    def expired(*args):
        raise SourceError("deadline_limit")

    signal.signal(signal.SIGALRM, expired)
    prior_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, *prior_timer)
        signal.signal(signal.SIGALRM, previous)


def network_get(url, timeout, limit):
    """Send one credential-free GET without proxying or following redirects."""
    parsed = urlsplit(url)
    addresses = safe_addresses(parsed.hostname)
    connection = PinnedHTTPS(parsed.hostname, addresses[0], timeout)
    try:
        path = parsed.path + ("?" + parsed.query if parsed.query else "")
        connection.request("GET", path, headers={
            "Accept": "application/json", "Accept-Encoding": "identity",
            "User-Agent": "SwarmForensics-PrivatePilot/0.1 (bounded public GET research)"})
        response = connection.getresponse()
        headers = {key.lower(): value for key, value in response.getheaders()
                   if key.lower().startswith("ratelimit")
                   or key.lower() in ("retry-after", "content-type", "content-length")}
        declared = headers.get("content-length")
        if declared and int(declared) > limit:
            raise SourceError("byte_limit")
        return response.status, headers, response.read(limit)
    finally:
        connection.close()


class Reader:
    """Permit only approved account reads within hard pilot budgets."""

    def __init__(self, dids, *, max_requests=MAX_REQUESTS, max_bytes=MAX_BYTES,
                 total_seconds=MAX_SECONDS, clock=time.monotonic, sleep=time.sleep,
                 network=network_get, wall_clock=time.time):
        if (not 1 <= max_requests <= MAX_REQUESTS or not 1 <= max_bytes <= MAX_BYTES
                or not 0 < total_seconds <= MAX_SECONDS):
            raise SourceError("invalid network budget")
        self.dids = set(dids)
        self.max_requests = max_requests
        self.max_bytes = max_bytes
        self.deadline = clock() + total_seconds
        self.clock, self.sleep, self.network, self.wall_clock = clock, sleep, network, wall_clock
        self.next_request = clock()
        self.requests = 0
        self.body_bytes = 0
        self.history = []

    def validate_url(self, url):
        """Reject credentials, private routes, and unrelated collections."""
        try:
            parsed = urlsplit(url)
            params = parse_qs(parsed.query, strict_parsing=True)
            if (parsed.scheme != "https" or not parsed.hostname
                    or parsed.username is not None or parsed.password is not None
                    or parsed.port not in (None, 443) or parsed.fragment
                    or any(len(value) != 1 for value in params.values())):
                raise SourceError("unsafe request origin")
            if parsed.hostname == "plc.directory":
                valid = not params and parsed.path.removeprefix("/") in self.dids
            elif parsed.hostname == "api.delve.town":
                valid = (parsed.path == "/xrpc/town.delve.actor.getProfile"
                         and set(params) == {"actor"} and params["actor"][0] in self.dids)
            else:
                valid = (parsed.path == "/xrpc/com.atproto.repo.listRecords"
                         and set(params) in ({"repo", "collection", "limit"},
                                             {"repo", "collection", "limit", "cursor"})
                         and params.get("repo", [None])[0] in self.dids
                         and params.get("collection") == ["town.delve.feed.post"]
                         and params.get("limit") == ["100"])
            if not valid:
                raise SourceError("request outside approved routes")
        except ValueError:
            raise SourceError("invalid request URL") from None

    def get(self, url):
        """Read bounded JSON and retain request-level provenance."""
        self.validate_url(url)
        for attempt in range(3):
            if self.requests >= self.max_requests:
                raise SourceError("request_limit")
            if self.body_bytes >= self.max_bytes:
                raise SourceError("byte_limit")
            delay = max(0, self.next_request - self.clock())
            if self.clock() + delay >= self.deadline:
                raise SourceError("deadline_limit")
            self.sleep(delay)
            remaining = self.deadline - self.clock()
            if remaining <= 0:
                raise SourceError("deadline_limit")
            self.requests += 1
            self.next_request = self.clock() + 1
            limit = min(MAX_PAGE_BYTES + 1, self.max_bytes - self.body_bytes)
            metadata = {"url": url, "method": "GET", "status": None,
                        "received_at": datetime.now(timezone.utc).isoformat(),
                        "body_bytes": 0, "body_sha256": None, "headers": {}}
            try:
                with deadline_guard(min(15, remaining)):
                    status, headers, raw = self.network(url, min(15, remaining), limit)
                self.body_bytes += len(raw)
                metadata.update(status=status, headers=headers, body_bytes=len(raw),
                                body_sha256=hashlib.sha256(raw).hexdigest(),
                                received_at=datetime.now(timezone.utc).isoformat())
                self.history.append(metadata)
                if len(raw) > MAX_PAGE_BYTES or self.body_bytes >= self.max_bytes:
                    raise SourceError("byte_limit")
                retry_after = headers.get("retry-after")
                wait = 0
                if retry_after:
                    try:
                        wait = max(0, float(retry_after))
                    except ValueError:
                        wait = max(0, parsedate_to_datetime(retry_after).timestamp()
                                   - self.wall_clock())
                if headers.get("ratelimit-remaining") == "0":
                    wait = max(wait, float(headers.get("ratelimit-reset", self.wall_clock()))
                               - self.wall_clock())
                if status in (429, 503):
                    wait = max(wait, 60 if not retry_after else 1)
                self.next_request = max(self.next_request, self.clock() + wait)
                if status in (429, 503) and attempt < 2:
                    continue
                if status != 200:
                    raise SourceError(f"source_HTTP_{status}")
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise SourceError("source JSON must be an object")
                json.dumps(body, allow_nan=False)
                return body, metadata
            except SourceError:
                if metadata not in self.history:
                    self.history.append(metadata)
                raise
            except (OSError, ValueError, http.client.HTTPException):
                if metadata not in self.history:
                    self.history.append(metadata)
                raise SourceError("source_transport_or_JSON_failure") from None
        raise SourceError("source_retry_failure")
