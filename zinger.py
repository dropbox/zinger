#!/usr/bin/env python3
"""
zinger -- a small interactive CLI for the Zingtree API.

API reference : https://help.zingtree.com/hc/en-us/articles/5048766502043-Zingtree-API
API key       : https://zingtree.com/account/organizations.php  ->  `API Key`
                Store it in a `.env` file as  `ZINGTREE_API_TOKEN="..."`, or
                temporary environment variable via executing the following:
                `export ZINGTREE_API_TOKEN="..."`

This project is libre and licenced APACHE-2.0; see the COPYING file or
https://www.apache.org/licenses/LICENSE-2.0 for more details.

Copyright (c) 2019,  Dropbox, Inc.
Author: Dillon Feeney.

Created: 2019-08-20
Updated: 2020-05-07
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

try:
    from dotenv import load_dotenv
except ImportError:                       # dotenv is optional
    def load_dotenv(*_args, **_kwargs):   # noqa: D401
        return False

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

API_URL    = "https://zingtree.com/api/"
ENV_FILE   = Path(".") / ".env"
AGENT_FILE = Path("zingers.txt")
TIMEOUT    = 30
PROMPT     = "\n\n  ==> "

load_dotenv(dotenv_path=ENV_FILE)

# ----------------------------------------------------------------------------
# Domain model
# ----------------------------------------------------------------------------

class ZingtreeError(RuntimeError):
    """Raised for any expected, recoverable failure."""


@dataclass
class Agent:
    email: str
    name: str
    tags: list[str] = field(default_factory=list)


@dataclass
class ZingtreeClient:
    """Thin wrapper over the Zingtree REST endpoints.

    The API embeds the key and all arguments in the URL path, so every
    segment is percent-encoded.  Commas are preserved because tag lists are
    comma-delimited inside a single segment.
    """

    token: str
    base_url: str = API_URL
    timeout: int = TIMEOUT

    def _mask(self, url: str) -> str:
        return url.replace(self.token, self.token[:5] + "...")

    def call(self, *segments: str) -> str:
        path = "/".join(quote(str(s), safe=",") for s in segments)
        url  = self.base_url + path
        print("\nCalling URL... {}".format(self._mask(url)))
        try:
            with urlopen(url, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise ZingtreeError("HTTP {} from {}".format(exc.code, self._mask(url))) from exc
        except URLError as exc:
            raise ZingtreeError("Request failed: {}".format(exc.reason)) from exc
        print(body)
        return body


def load_agents(path: Path = AGENT_FILE) -> list[Agent]:
    """Parse `zingers.txt`.

    Each line:  email,Forename Surname,tag_0,tag_1
    """
    if not path.exists():
        raise ZingtreeError("{} not found.".format(path))

    agents: list[Agent] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        fields = [f.strip() for f in raw.split(",")]
        if len(fields) < 2:
            raise ZingtreeError("Malformed line {}: {!r}".format(lineno, raw))
        email, name, *tags = fields
        agents.append(Agent(email=email, name=name, tags=tags))

    if not agents:
        raise ZingtreeError("{} is empty.".format(path))
    return agents


def confirm_agents(agents: list[Agent], action: str) -> bool:
    for a in agents:
        print("\n    Name  : {}\n    Email : {}\n    Tags  : {}".format(a.name, a.email, a.tags))
    answer = input("\n  This will {} the above agents.  Continue? (y/N){}".format(action, PROMPT))
    return answer.strip().lower() == "y"


# ----------------------------------------------------------------------------
# Operations
# ----------------------------------------------------------------------------

def op_agent_add(client: ZingtreeClient) -> None:
    agents = load_agents()
    if not confirm_agents(agents, "ADD and TAG"):
        return
    for a in agents:
        client.call("agent_add", client.token, a.name, a.email)
        if a.tags:
            client.call("agent_tag", client.token, a.email, ",".join(a.tags))


def op_agent_add_inter(client: ZingtreeClient) -> None:
    name  = input("\nEnter agent's name..."  + PROMPT).strip()
    email = input("\nEnter agent's email..." + PROMPT).strip()
    tags  = input("\nEnter agent's tags..."  + PROMPT).strip()
    client.call("agent_add", client.token, name, email)
    if tags:
        client.call("agent_tag", client.token, email, tags)


def op_agent_tag(client: ZingtreeClient) -> None:
    agents = load_agents()
    if not confirm_agents(agents, "TAG"):
        return
    for a in agents:
        client.call("agent_tag", client.token, a.email, ",".join(a.tags))


def op_agent_remove(client: ZingtreeClient) -> None:
    agents = load_agents()
    if not confirm_agents(agents, "REMOVE"):
        return
    for a in agents:
        client.call("agent_remove", client.token, a.email)


def op_agent_remove_inter(client: ZingtreeClient) -> None:
    email = input("\nEnter agent's email..." + PROMPT).strip()
    client.call("agent_remove", client.token, email)


def op_search_trees(client: ZingtreeClient) -> None:
    query = input("\nEnter query..." + PROMPT).strip()
    client.call("tree", client.token, "search_trees", query)


def op_get_trees(client: ZingtreeClient) -> None:
    client.call("tree", client.token, "get_trees")


def op_get_tags(client: ZingtreeClient) -> None:
    client.call("tree", client.token, "get_tags")


def op_get_tree_tag_any(client: ZingtreeClient) -> None:
    tags = input("\nSearch trees by comma-separated tags..." + PROMPT).strip()
    client.call("tree", client.token, "get_tree_tag_any", tags)


def op_get_tree_tag_all(client: ZingtreeClient) -> None:
    tags = input("\nSearch trees by comma-separated tags..." + PROMPT).strip()
    client.call("tree", client.token, "get_tree_tag_all", tags)


def op_get_form_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_form_data")


def op_delete_form_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "delete_form_data")


def op_agent_sessions(client: ZingtreeClient) -> None:
    email = input("\nEnter agent email..."        + PROMPT).strip()
    start = input("\nStart date (YYYY-MM-DD)..."  + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD)..."    + PROMPT).strip()
    client.call("agent_sessions", client.token, email, start, end)


def op_tree_sessions(client: ZingtreeClient) -> None:
    tree  = input("\nEnter tree_id..."            + PROMPT).strip()
    start = input("\nStart date (YYYY-MM-DD)..."  + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD)..."    + PROMPT).strip()
    client.call("tree_sessions", client.token, tree, start, end)


def op_get_session_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_data")


def op_get_session_data_pure(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_data_pure")


def op_get_session_notes(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_notes")


def op_event_log(client: ZingtreeClient) -> None:
    start = input("\nStart date (YYYY-MM-DD)..." + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD)..."   + PROMPT).strip()
    client.call("event_log", client.token, start, end)


OPERATIONS = {
    "agent_add":             op_agent_add,
    "agent_add_inter":       op_agent_add_inter,
    "agent_tag":             op_agent_tag,
    "agent_remove":          op_agent_remove,
    "agent_remove_inter":    op_agent_remove_inter,
    "search_trees":          op_search_trees,
    "get_trees":             op_get_trees,
    "get_tags":              op_get_tags,
    "get_tree_tag_any":      op_get_tree_tag_any,
    "get_tree_tag_all":      op_get_tree_tag_all,
    "get_form_data":         op_get_form_data,
    "delete_form_data":      op_delete_form_data,
    "agent_sessions":        op_agent_sessions,
    "tree_sessions":         op_tree_sessions,
    "get_session_data":      op_get_session_data,
    "get_session_data_pure": op_get_session_data_pure,
    "get_session_notes":     op_get_session_notes,
    "event_log":             op_event_log,
}

# ----------------------------------------------------------------------------
# Menus
# ----------------------------------------------------------------------------

MAIN_ITEMS = {
    "0": ("agents",   "update agents"),
    "1": ("trees",    "get info on trees"),
    "2": ("forms",    "get or remove form data"),
    "3": ("sessions", "tree and agent session info"),
}

SUBMENUS = {
    "0": ("agents", [
        ("auto agent_add      (from file)",      "agent_add"),
        ("manual agent_add    (interactive)",    "agent_add_inter"),
        ("auto agent_tag      (from file)",      "agent_tag"),
        ("auto agent_remove   (from file)",      "agent_remove"),
        ("manual agent_remove (interactive)",    "agent_remove_inter"),
    ]),
    "1": ("trees", [
        ("search_trees     (search all trees for matching text)", "search_trees"),
        ("get_trees        (fetch all trees)",                    "get_trees"),
        ("get_tags         (fetch all tags used on trees)",       "get_tags"),
        ("get_tree_tag_any (trees matching ANY tags)",            "get_tree_tag_any"),
        ("get_tree_tag_all (trees matching ALL tags)",            "get_tree_tag_all"),
    ]),
    "2": ("forms", [
        ("get_form_data    (form values entered during a session)", "get_form_data"),
        ("delete_form_data (delete any form data)",                 "delete_form_data"),
    ]),
    "3": ("sessions", [
        ("agent_sessions        (list agent sessions)",                "agent_sessions"),
        ("tree_sessions         (list tree sessions)",                 "tree_sessions"),
        ("get_session_data      (form values entered during session)", "get_session_data"),
        ("get_session_data_pure (linear path to tree)",                "get_session_data_pure"),
        ("get_session_notes     (agent notes from session)",           "get_session_notes"),
        ("event_log             (event log for a date range)",         "event_log"),
    ]),
}

META = """
╭─────────────────────────────────────────────────╮
│  Name    :: zinger
│  Source  :: https://github.com/dropbox/zinger
│  Author  :: Dillon Feeney
│  Licence :: Apache-2.0
│  Copyright (c) 2019 Dropbox, Inc.
╰─────────────────────────────────────────────────╯
"""


def render(title: str, lines: list[str]) -> str:
    border = "═" * 70
    out = ["\n╭" + border + "╮", "│  zinger | {}".format(title), "│"]
    out.extend("│  {}".format(line) for line in lines)
    out += ["│", "│  [Q] quit", "╰" + border + "╯"]
    return "\n".join(out)


def render_main() -> str:
    lines = ["[{}] {:9s} ({})".format(k, name, desc) for k, (name, desc) in MAIN_ITEMS.items()]
    lines.append("[00] meta      (print metadata)")
    return render("main menu", lines)


def render_submenu(title: str, items: list[tuple[str, str]]) -> str:
    lines = ["[{}] {}".format(i, label) for i, (label, _) in enumerate(items)]
    return render("{} menu".format(title), lines)


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------

def run_submenu(client: ZingtreeClient, key: str) -> None:
    title, items = SUBMENUS[key]
    print(render_submenu(title, items))
    choice = input("\nSelect option..." + PROMPT).strip()
    if choice.lower() == "q":
        return
    if not choice.isdigit() or not 0 <= int(choice) < len(items):
        print("Invalid option.")
        return

    op_key = items[int(choice)][1]
    try:
        OPERATIONS[op_key](client)
    except ZingtreeError as exc:
        print("\nError: {}".format(exc))
        return
    if op_key.startswith("agent"):
        print("\nAgents list: https://zingtree.com/account/agents.php")


def main() -> None:
    clear()
    token = os.getenv("ZINGTREE_API_TOKEN")
    if not token:
        sys.exit("
    Environment variable ZINGTREE_API_TOKEN missing or empty in `.env`.  Either
    set the variable manually (`export ZINGTREE_API_TOKEN='token' or in
    the .env file -- this file is .gitignore'd)
        ")
    client = ZingtreeClient(token=token)

    while True:
        print(render_main())
        choice = input("\nSelect option..." + PROMPT).strip()

        if choice.lower() == "q":
            print("\nQuitting... Goodbye...\n")
            return
        if choice == "00":
            print(META)
            input("\nEnter to continue..." + PROMPT)
            clear()
            continue
        if choice in SUBMENUS:
            run_submenu(client, choice)
            continue
        print("Invalid option.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.\n")
        sys.exit(130)
