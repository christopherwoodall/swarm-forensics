"""Export hunt database to JSON and an Obsidian Markdown vault.

Streams JSON row-by-row to avoid loading large datasets into memory.
Generates structured Markdown files with wikilinks in a vault directory.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import db
from .paths import state_dir

TYPE_FOLDERS = {
    "artifact": "Artifacts",
    "agent": "Agents",
    "swarm": "Swarms",
    "campaign": "Campaigns",
    "collection": "Collections",
}

PLURALS = {
    "artifact": "Artifacts",
    "agent": "Agents",
    "swarm": "Swarms",
    "campaign": "Campaigns",
    "collection": "Collections",
}


def sanitize_filename(name: str) -> str:
    """Sanitize name for safe filesystem usage."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        cleaned = "unnamed"
    return cleaned[:120]


def _stream_table(conn, f, table, order_col="id", transform=None):
    """Stream table rows into an open JSON array."""
    f.write(f'  "{table}": [\n')
    cur = conn.execute(f"SELECT * FROM {table} ORDER BY {order_col} ASC")
    first = True
    count = 0
    while True:
        rows = cur.fetchmany(500)
        if not rows:
            break
        for row in rows:
            count += 1
            item = dict(row)
            if transform:
                item = transform(item)
            if not first:
                f.write(",\n")
            first = False
            f.write("    " + json.dumps(item, ensure_ascii=False))
    f.write("\n  ]")
    return count


def _render_entity_note(view: dict) -> str:
    """Render an entity view to an Obsidian Markdown document."""
    lines = [
        "---",
        f"type: {view['type']}",
        f"origin: {view.get('origin', 'human')}",
        f"updated: {view.get('updated_utc', '')}",
    ]
    tags = view.get("tags") or []
    if tags:
        lines.append(f"tags: {json.dumps(tags)}")
    lines.extend([
        "---",
        f"# {view['name']}",
    ])
    if view.get("summary"):
        lines.append(f"> {view['summary']}")
    lines.append("")

    parents = view.get("parents") or {}
    parent_items = []
    for group in parents.values():
        for p in group:
            parent_items.append(f"- [[{p['name']}]]")
    if parent_items:
        lines.append("## Belongs to")
        lines.extend(parent_items)
        lines.append("")

    children = view.get("children") or {}
    for ctype, cgroup in children.items():
        if not cgroup:
            continue
        title = PLURALS.get(ctype, ctype.capitalize() + "s")
        lines.append(f"## {title}")
        for c in cgroup:
            lines.append(f"- [[{c['name']}]]")
        lines.append("")

    related = []
    seen_related = set()
    edges = (view.get("outgoing") or []) + (view.get("backlinks") or [])
    for edge in edges:
        kind = edge.get("kind")
        if kind in ("part_of", "mentions"):
            continue
        name = edge.get("name")
        key = (name, kind)
        if key not in seen_related:
            seen_related.add(key)
            related.append(f"- [[{name}]] ({kind})")
    if related:
        lines.append("## Related")
        lines.extend(related)
        lines.append("")

    notes = view.get("notes")
    if notes:
        lines.append(notes.strip())
        lines.append("")

    evidence = view.get("evidence") or []
    if evidence:
        lines.append("## Evidence")
        for ev in evidence:
            obs = ev.get("observed_utc", "")[:10]
            date_str = f" — {obs}" if obs else ""
            lines.append(f"- [{ev.get('claim_level', 'L1')}] {ev.get('url', '')}{date_str}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def export_all(service, dest_root=None) -> dict:
    """Export complete dataset to JSON bundle and Markdown vault."""
    root = Path(dest_root) if dest_root else state_dir() / "exports"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    export_dir = root / stamp
    export_dir.mkdir(parents=True, exist_ok=True)
    vault_dir = export_dir / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)

    for folder_name in TYPE_FOLDERS.values():
        (vault_dir / folder_name).mkdir(parents=True, exist_ok=True)

    json_path = export_dir / "swarm-forensics.json"
    counts = {}

    with service.db.connect() as conn:
        with open(json_path, "w", encoding="utf-8") as f:
            f.write("{\n")
            f.write('  "schema": 3,\n')
            f.write(f'  "exported_utc": {json.dumps(db.now())},\n')

            counts["iocs"] = _stream_table(conn, f, "iocs")
            f.write(",\n")

            counts["entities"] = _stream_table(
                conn, f, "entities",
                transform=lambda item: dict(item, attrs=db.loads(item.get("attrs", "{}"), {}))
            )
            f.write(",\n")

            counts["links"] = _stream_table(conn, f, "links")
            f.write(",\n")

            counts["evidence"] = _stream_table(
                conn, f, "evidence",
                transform=lambda item: dict(item, analysis=db.loads(item.get("analysis", "{}"), {}))
            )
            f.write(",\n")

            counts["hunts"] = _stream_table(
                conn, f, "hunts",
                transform=lambda item: dict(item, stats=db.loads(item.get("stats", "{}"), {}))
            )
            f.write(",\n")

            counts["urls"] = _stream_table(conn, f, "urls", order_col="url")
            f.write(",\n")

            counts["prompts"] = _stream_table(
                conn, f, "prompts", order_col="id",
                transform=lambda item: dict(
                    item, variables=db.loads(item.get("variables", "[]"), [])
                )
            )
            f.write("\n}\n")

        # Export Markdown notes for entities
        sql = "SELECT id, type, name FROM entities ORDER BY type, name"
        entity_rows = conn.execute(sql).fetchall()
        for r in entity_rows:
            view = service.graph.view(r["id"])
            if not view:
                continue
            folder = vault_dir / TYPE_FOLDERS.get(view["type"], "Artifacts")
            base_filename = sanitize_filename(view["name"])
            filename = f"{base_filename}.md"
            suffix = 2
            while (folder / filename).exists():
                filename = f"{base_filename}-{suffix}.md"
                suffix += 1
            note_content = _render_entity_note(view)
            (folder / filename).write_text(note_content, encoding="utf-8")

        # Export Markdown notes for Prompts
        prompts_dir = vault_dir / "Prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        prompt_rows = conn.execute("SELECT * FROM prompts ORDER BY id").fetchall()
        for pr in prompt_rows:
            p_lines = [
                "---",
                f"id: {pr['id']}",
                f"name: {pr['name']}",
                f"description: {pr['description']}",
                f"variables: {pr['variables']}",
                f"updated: {pr['updated_utc']}",
                "---",
                f"# Prompt: {pr['name']}",
                "",
                pr["template"],
            ]
            (prompts_dir / f"{pr['id']}.md").write_text(
                "\n".join(p_lines).strip() + "\n", encoding="utf-8"
            )

        # Export IOCs.md
        ioc_rows = conn.execute("SELECT * FROM iocs ORDER BY status, term").fetchall()
        log_rows = conn.execute("SELECT * FROM ioc_log ORDER BY ts ASC").fetchall()
        logs_by_ioc = {}
        for lr in log_rows:
            logs_by_ioc.setdefault(lr["ioc_id"], []).append(dict(lr))

        iocs_by_status = {}
        for ir in ioc_rows:
            iocs_by_status.setdefault(ir["status"], []).append(dict(ir))

        ioc_lines = ["# Indicators of Compromise\n"]
        status_order = ("active", "proposed", "inactive", "rejected", "benign")
        for st in status_order:
            group = iocs_by_status.get(st, [])
            if not group:
                continue
            ioc_lines.append(f"## {st.capitalize()}\n")
            for item in group:
                ioc_lines.append(f"### `{item['term']}`")
                ioc_lines.append(f"- Category: {item['category']}")
                ioc_lines.append(f"- Confidence: {item['confidence']}")
                ioc_lines.append(f"- Origin: {item['origin']}")
                ioc_lines.append(f"- Provenance: {item['provenance']}")
                if item.get("note"):
                    ioc_lines.append(f"- Note: {item['note']}")
                logs = logs_by_ioc.get(item["id"], [])
                if logs:
                    ioc_lines.append("- Audit Trail:")
                    for lg in logs:
                        ioc_lines.append(
                            f"  - {lg['ts']}: {lg['from_status']} -> {lg['to_status']}"
                            f" by {lg['actor']} ({lg['reason']})"
                        )
                ioc_lines.append("")

        (vault_dir / "IOCs.md").write_text("\n".join(ioc_lines).strip() + "\n", encoding="utf-8")

    return {"path": str(export_dir), "counts": counts}
