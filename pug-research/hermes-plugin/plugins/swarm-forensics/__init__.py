"""Swarm Forensics: the Hermes agent half.

Registers the `/swarm-forensics` command and the bundled skill. The hunt
engine lives in `swarm_forensics_plugin` and is shared with the desktop
API in `dashboard/plugin_api.py`, so both see one service per process.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def register(ctx):
    from swarm_forensics_plugin.agent_tools import register_tools
    from swarm_forensics_plugin.command import handle
    from swarm_forensics_plugin.hooks import register_hooks
    from swarm_forensics_plugin.service import get_service

    service = get_service(ctx)
    ctx.register_command(
        "swarm-forensics",
        handler=lambda raw_args: handle(service, raw_args),
        description="Start, stop, and review autonomous swarm hunts.",
        args_hint="start|attach|subhunt|tools|stop|pause|resume|status|"
                  "log|review|accept|reject|benign|narrow|find|settings|reset",
    )
    register_tools(ctx)
    register_hooks(ctx, service)
    skill = _HERE / "skills" / "swarm-forensics" / "SKILL.md"
    if skill.exists():
        ctx.register_skill("swarm-forensics", skill,
                           "How to run and read swarm hunts.")
