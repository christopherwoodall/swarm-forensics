"""Shared language links (rule derived, offline).

Rule `shared_rare_language`:
- Text sources: stated session goals, chat and history actions, Claude Code assistant text,
  and chat messages from agents.
- Features: quoted phrases (2 to 8 words) and rare terms (6 to 30 letters or digits).
- An inverted index maps each feature to the traces (sessions or chat episodes) that use it.
- Keep a feature only when 2 to `MAX_OWNERS_PER_TERM` traces use it AND 2 or more agents do.
  The cap stops quadratic growth. No all-pairs comparison runs.
- Score = 1 / number of traces. The score is inspectable and ranks rarer features higher.
Shared language MUST NOT be read as proof of collaboration.
"""

from __future__ import annotations

import re
import sqlite3

MAX_OWNERS_PER_TERM = 10
MIN_TERM_LEN = 6
BATCH = 20_000

_TOKEN = re.compile(rf"[a-z][a-z0-9_-]{{{MIN_TERM_LEN - 1},29}}")
_QUOTED = re.compile(r"(?<!\w)[\"“'‘]([^\"”'’\n]{8,70})[\"”'’](?!\w)")
_URL = re.compile(r"https?://\S+")
_PATH = re.compile(r"(?<!\w)(?:/[\w.\-@%+=,]+){2,}")
_HEXISH = re.compile(r"^[0-9a-f_-]{8,}$")

STOPWORDS = frozenset(
    """
    about above after again against agent agents already also always another around because
    before being below between both cannot check chat could current doing during each either
    every first following from further going have having here however into just later like
    make makes might more most much must need never next only other over please really
    right same should since some still such than that their them then there these they this
    those through today under until using very want were what when where which while will
    with within without would your yours session sessions village message messages update
    updated working work works task tasks goal goals done complete completed status help
    thanks thank click open page file files folder google document create created check
    """.split()
)


def extract_language(text: str) -> tuple[set[str], set[str]]:
    """Return (quoted phrases, rare-term candidates) from one text."""
    if not text:
        return set(), set()
    phrases: set[str] = set()
    for match in _QUOTED.finditer(text):
        phrase = " ".join(match.group(1).lower().split())
        words = phrase.split()
        letters = sum(c.isalpha() for c in phrase)
        if 2 <= len(words) <= 8 and letters >= 0.6 * len(phrase):
            phrases.add(phrase)
    body = _PATH.sub(" ", _URL.sub(" ", text)).lower()
    terms = {
        t
        for t in _TOKEN.findall(body)
        if t not in STOPWORDS and not _HEXISH.match(t) and sum(c.isdigit() for c in t) < 4
    }
    return phrases, terms


def _sources(conn: sqlite3.Connection):
    """Yield (owner_id, agent_id, text, source_table, source_id, field_path)."""
    for sid, agent, goal in conn.execute(
        "SELECT id, agent_id, goal_text FROM sessions WHERE goal_text IS NOT NULL"
    ):
        yield f"session:{sid}", agent, goal, "computer_use_sessions", sid, "session_goal"
    for sid, agent, tid, detail, path in conn.execute(
        "SELECT t.session_id, s.agent_id, t.id, t.detail, t.detail_path FROM turns t "
        "JOIN sessions s ON s.id = t.session_id "
        "WHERE t.surface IN ('chat', 'history') AND t.detail IS NOT NULL"
    ):
        yield f"session:{sid}", agent, detail, "computer_use_turns", tid, path or "agent_action"
    for sid, agent, mid, text, path in conn.execute(
        "SELECT session_id, agent_id, id, text, text_path FROM messages "
        "WHERE source_table = 'claude_code_messages' AND role = 'assistant' "
        "AND session_id IS NOT NULL AND text IS NOT NULL"
    ):
        yield f"session:{sid}", agent, text, "claude_code_messages", mid, path or "content"
    for eid, agent, mid, text in conn.execute(
        "SELECT episode_id, agent_id, id, text FROM messages "
        "WHERE source_table = 'chat_messages' AND speaker_type = 'agent' "
        "AND episode_id IS NOT NULL AND agent_id IS NOT NULL AND text IS NOT NULL"
    ):
        yield f"episode:{eid}", agent, text, "chat_messages", mid, "content"


def build_language_links(conn: sqlite3.Connection) -> dict[str, int]:
    with conn:
        conn.execute("DELETE FROM language_links")
        conn.execute("DROP TABLE IF EXISTS temp.term_post")
        conn.execute(
            "CREATE TEMP TABLE term_post (term TEXT, kind TEXT, owner TEXT, agent TEXT, "
            "src_table TEXT, src_id TEXT, path TEXT, PRIMARY KEY (term, kind, owner)) "
            "WITHOUT ROWID"
        )
    batch: list[tuple] = []
    texts = 0
    source_cur = conn.cursor()
    for owner, agent, text, table, src, path in _sources(source_cur):
        texts += 1
        phrases, terms = extract_language(text)
        batch.extend((p, "phrase", owner, agent, table, src, path) for p in phrases)
        batch.extend((t, "term", owner, agent, table, src, path) for t in terms)
        if len(batch) >= BATCH:
            conn.executemany("INSERT OR IGNORE INTO term_post VALUES (?,?,?,?,?,?,?)", batch)
            batch.clear()
    if batch:
        conn.executemany("INSERT OR IGNORE INTO term_post VALUES (?,?,?,?,?,?,?)", batch)
    with conn:
        conn.execute(
            """
            INSERT INTO language_links
            SELECT p.term, p.kind, p.owner, p.agent, k.n_owners, k.n_agents,
                   ROUND(1.0 / k.n_owners, 4), p.src_table, p.src_id, p.path
            FROM term_post p
            JOIN (SELECT term, kind, COUNT(*) AS n_owners, COUNT(DISTINCT agent) AS n_agents
                  FROM term_post GROUP BY term, kind
                  HAVING n_owners BETWEEN 2 AND ? AND n_agents >= 2) k
              ON k.term = p.term AND k.kind = p.kind
            """,
            (MAX_OWNERS_PER_TERM,),
        )
        postings = conn.execute("SELECT COUNT(*) FROM term_post").fetchone()[0]
        conn.execute("DROP TABLE temp.term_post")
    kept = conn.execute("SELECT COUNT(DISTINCT term || kind) FROM language_links").fetchone()[0]
    links = conn.execute("SELECT COUNT(*) FROM language_links").fetchone()[0]
    from db import create_indexes

    create_indexes(conn, "language_links")
    return {"texts_scanned": texts, "postings": postings, "shared_features": kept, "links": links}
