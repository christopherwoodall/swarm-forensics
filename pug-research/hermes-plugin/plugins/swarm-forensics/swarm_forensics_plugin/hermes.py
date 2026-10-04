"""Adapter for the Hermes runtime: host-owned model and web tools.

The plugin never holds provider keys. Model calls go through the host
LLM facade (`ctx.llm`, or `agent.plugin_llm.PluginLlm` when only the
dashboard process is running). Web search and page extraction go through
the host tool registry. Every call fails soft with HermesUnavailable so a
hunt can block with a clear reason instead of crashing.
"""

import json

from .paths import PLUGIN_ID


class HermesUnavailable(RuntimeError):
    """Raised when a Hermes capability is missing or refused."""


def _loads(text):
    try:
        return json.loads(text) if isinstance(text, str) else text
    except ValueError:
        return None


def _load_builtin_tools():
    """Make sure the built-in tools are registered in this process."""
    try:
        import model_tools  # noqa: F401  (importing registers the tools)
    except Exception:
        pass


class HermesRuntime:
    def __init__(self, ctx=None):
        self._ctx = ctx
        self._llm = None

    def attach(self, ctx):
        """Prefer the plugin context once it is known."""
        if self._ctx is None:
            self._ctx = ctx
            self._llm = None

    # -- model --------------------------------------------------------------

    def _llm_facade(self):
        if self._llm is not None:
            return self._llm
        try:
            if self._ctx is not None:
                self._llm = self._ctx.llm
            else:
                from agent.plugin_llm import PluginLlm
                self._llm = PluginLlm(plugin_id=PLUGIN_ID)
        except Exception as exc:
            raise HermesUnavailable("model facade unavailable: %s" % exc)
        return self._llm

    def complete_json(self, system, user, schema_name, settings):
        """Run one structured completion and return the parsed JSON object."""
        llm = self._llm_facade()
        kwargs = {
            "instructions": user,
            "input": [{"type": "text", "text": "Respond with one JSON object."}],
            "json_mode": True,
            "schema_name": schema_name,
            "system_prompt": system,
            "temperature": 0.2,
            "max_tokens": settings["model.max_tokens"],
            "timeout": settings["model.timeout_seconds"],
            "purpose": "swarm-forensics:" + schema_name,
        }
        if settings["model.provider"]:
            kwargs["provider"] = settings["model.provider"]
        if settings["model.name"]:
            kwargs["model"] = settings["model.name"]
        try:
            result = llm.complete_structured(**kwargs)
        except Exception as exc:
            raise HermesUnavailable("model call failed: %s" % exc)
        parsed = getattr(result, "parsed", None)
        if parsed is None:
            parsed = _loads(getattr(result, "text", ""))
        if not isinstance(parsed, dict):
            raise HermesUnavailable("model returned no JSON object")
        return parsed

    # -- tools --------------------------------------------------------------

    def _dispatch(self, name, args):
        try:
            if self._ctx is not None:
                raw = self._ctx.dispatch_tool(name, args)
            else:
                _load_builtin_tools()
                from tools.registry import registry
                raw = registry.dispatch(name, args)
        except Exception as exc:
            raise HermesUnavailable("tool %s failed: %s" % (name, exc))
        data = _loads(raw)
        if not isinstance(data, dict):
            raise HermesUnavailable("tool %s returned no data" % name)
        if data.get("error"):
            raise HermesUnavailable("tool %s: %s" % (name, data["error"]))
        return data

    def web_search(self, query, limit=10):
        """Return [{url, title, description}] from the Hermes search tool."""
        data = self._dispatch("web_search", {"query": query, "limit": limit})
        rows = (data.get("data") or {}).get("web") or data.get("results") or []
        return [{"url": r.get("url", ""), "title": r.get("title", ""),
                 "description": r.get("description", "")}
                for r in rows if isinstance(r, dict) and r.get("url")]

    def web_extract(self, urls):
        """Return [{url, title, content}] from the Hermes extract tool."""
        data = self._dispatch("web_extract", {"urls": list(urls)[:5]})
        rows = data.get("results") or (data.get("data") or {}).get("results") or []
        out = []
        for r in rows:
            if isinstance(r, dict) and not r.get("error"):
                out.append({"url": r.get("url", ""), "title": r.get("title", ""),
                            "content": r.get("content") or r.get("raw_content")
                            or r.get("markdown") or ""})
        return out

    # -- status -------------------------------------------------------------

    def capabilities(self):
        """Report which Hermes capabilities this process can reach."""
        out = {"model": False, "web_search": False, "web_extract": False,
               "detail": []}
        try:
            self._llm_facade()
            out["model"] = True
        except HermesUnavailable as exc:
            out["detail"].append(str(exc))
        try:
            _load_builtin_tools()
            from tools.registry import registry
            for tool in ("web_search", "web_extract"):
                out[tool] = registry.get_entry(tool) is not None
        except Exception as exc:
            out["detail"].append("tool registry unavailable: %s" % exc)
        return out
