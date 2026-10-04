"""Schedule specs: simple intervals ("6h") and five-field cron (UTC).

Schedules live in SQLite. No OS crontab is touched. A missed run is
coalesced: the next run is computed from the current time, never replayed.
"""

import re
from datetime import datetime, timedelta, timezone

MIN_INTERVAL_SECONDS = 300
_UNITS = {"m": 60, "h": 3600, "d": 86400}
_FIELD_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]


class ScheduleError(ValueError):
    pass


def parse_interval(spec):
    m = re.fullmatch(r"\s*(\d+)\s*([mhd])\s*", str(spec).lower())
    if not m:
        raise ScheduleError("interval looks like 30m, 6h, or 1d")
    seconds = int(m.group(1)) * _UNITS[m.group(2)]
    if seconds < MIN_INTERVAL_SECONDS:
        raise ScheduleError("interval must be at least 5 minutes")
    return seconds


def _field(text, low, high):
    values = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, step_text = part.split("/", 1)
            if not step_text.isdigit() or int(step_text) < 1:
                raise ScheduleError("bad cron step")
            step = int(step_text)
        if part == "*":
            start, end = low, high
        elif "-" in part:
            a, _, b = part.partition("-")
            if not (a.isdigit() and b.isdigit()):
                raise ScheduleError("bad cron range")
            start, end = int(a), int(b)
        elif part.isdigit():
            start = int(part)
            end = high if step > 1 else start
        else:
            raise ScheduleError("bad cron field")
        if start < low or end > high or start > end:
            raise ScheduleError("cron value out of range")
        values.update(range(start, end + 1, step))
    return values


def parse_cron(spec):
    parts = str(spec).split()
    if len(parts) != 5:
        raise ScheduleError("cron needs five fields: min hour day month weekday")
    return [_field(p, lo, hi) for p, (lo, hi) in zip(parts, _FIELD_RANGES)]


def validate(kind, spec):
    if kind == "interval":
        parse_interval(spec)
    elif kind == "cron":
        parse_cron(spec)
    else:
        raise ScheduleError("kind must be interval or cron")


def next_after(kind, spec, after):
    """Return the next run time after `after` (aware datetime, UTC)."""
    if kind == "interval":
        return after + timedelta(seconds=parse_interval(spec))
    minutes, hours, days, months, weekdays = parse_cron(spec)
    probe = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = probe + timedelta(days=366)
    while probe < limit:
        # Cron weekday 0 is Sunday. Python weekday() 0 is Monday.
        if (probe.minute in minutes and probe.hour in hours
                and probe.day in days and probe.month in months
                and (probe.weekday() + 1) % 7 in weekdays):
            return probe
        probe += timedelta(minutes=1)
    raise ScheduleError("cron never fires within a year")


def utcnow():
    return datetime.now(timezone.utc)
