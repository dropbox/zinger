#!/usr/bin/env python3
"""
zinger -- a small interactive CLI for the Zingtree API.

API reference : https://help.zingtree.com/hc/en-us/articles/5048766502043-Zingtree-API
API key       : https://zingtree.com/account/organizations.php  ->  `API Key`
                Store it in a `.env` file as  `ZINGTREE_API_TOKEN="..."`, or
                temporary environment variable via executing the following:
                `export ZINGTREE_API_TOKEN="..."`
Authentication is via the X-Api-Key request header.  The key is never
placed in the URL path.

This project is libre and licenced APACHE-2.0; see the COPYING file or
https://www.apache.org/licenses/LICENSE-2.0 for more details.

Copyright (c) 2019,  Dropbox, Inc.
Author: Dillon Feeney.

Created: 2019-08-20
Updated: 2020-05-07
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ImportError:                       # dotenv is optional
    def load_dotenv(*_args, **_kwargs):   # noqa: D401
        return False

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

API_URL    = "https://zingtree.com/api/v1/"
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
    """Thin wrapper over the Zingtree v1 REST endpoints.

    The key travels in the X-Api-Key header.  Path segments carry only the
    operation arguments and are percent-encoded; commas and carets are kept
    literal because tag lists are comma-delimited and search_trees uses `^^`
    as an AND separator.
    """

    token: str
    base_url: str = API_URL
    timeout: int = TIMEOUT

    def call(self, *segments: str, method: str = "GET", body: dict | None = None) -> str:
        path = "/".join(quote(str(s), safe=",^") for s in segments)
        url  = self.base_url + path

        headers = {"X-Api-Key": self.token}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        print("\n{} {}".format(method, url))
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as resp:
                status  = getattr(resp, "status", resp.getcode())
                payload = resp.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise ZingtreeError("HTTP {} -- {}".format(exc.code, detail or exc.reason)) from exc
        except URLError as exc:
            raise ZingtreeError("Request failed: {}".format(exc.reason)) from exc

        print(payload if payload else "OK ({})".format(status))
        return payload


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
        client.call("agent_add", a.name, a.email)
        if a.tags:
            client.call("agent_tag", a.email, ",".join(a.tags))


def op_agent_add_inter(client: ZingtreeClient) -> None:
    name  = input("\nEnter agent's name..."  + PROMPT).strip()
    email = input("\nEnter agent's email..." + PROMPT).strip()
    tags  = input("\nEnter agent's tags..."  + PROMPT).strip()
    client.call("agent_add", name, email)
    if tags:
        client.call("agent_tag", email, tags)


def op_agent_tag(client: ZingtreeClient) -> None:
    agents = load_agents()
    if not confirm_agents(agents, "TAG"):
        return
    for a in agents:
        client.call("agent_tag", a.email, ",".join(a.tags))


def op_agent_remove(client: ZingtreeClient) -> None:
    agents = load_agents()
    if not confirm_agents(agents, "REMOVE"):
        return
    for a in agents:
        client.call("agent_remove", a.email)


def op_agent_remove_inter(client: ZingtreeClient) -> None:
    email = input("\nEnter agent's email..." + PROMPT).strip()
    client.call("agent_remove", email)


def op_search_trees(client: ZingtreeClient) -> None:
    query = input("\nEnter query (use ^^ to AND terms)..." + PROMPT).strip()
    client.call("tree", "search_trees", query)


def op_get_tags(client: ZingtreeClient) -> None:
    client.call("tree", "get_tags")


def op_get_tree_tag_any(client: ZingtreeClient) -> None:
    tags = input("\nSearch trees by comma-separated tags..." + PROMPT).strip()
    client.call("tree", "get_tree_tag_any", tags)


def op_get_tree_tag_all(client: ZingtreeClient) -> None:
    tags = input("\nSearch trees by comma-separated tags..." + PROMPT).strip()
    client.call("tree", "get_tree_tag_all", tags)


def op_get_tree_variables(client: ZingtreeClient) -> None:
    tree = input("\nEnter tree_id (append 000 for production)..." + PROMPT).strip()
    client.call("get_tree_variables", tree)


def op_get_form_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_form_data")


def op_delete_form_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "delete_form_data")


def op_delete_file_upload(client: ZingtreeClient) -> None:
    folder = input("\nEnter folder (e.g. pdf)..." + PROMPT).strip()
    name   = input("\nEnter file name..."         + PROMPT).strip()
    client.call("delete_file_upload", folder, name)


def op_agent_sessions(client: ZingtreeClient) -> None:
    email = input("\nEnter agent email (* for all)..." + PROMPT).strip()
    start = input("\nStart date (YYYY-MM-DD, blank = 30d)..." + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD, blank = 30d)..."   + PROMPT).strip()
    client.call("agent_sessions", email, start, end)


def op_tree_sessions(client: ZingtreeClient) -> None:
    tree  = input("\nEnter tree_id (* for all)..." + PROMPT).strip()
    start = input("\nStart date (YYYY-MM-DD, blank = 30d)..." + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD, blank = 30d)..."   + PROMPT).strip()
    client.call("tree_sessions", tree, start, end)


def op_tree_sessions_last_clicked(client: ZingtreeClient) -> None:
    tree  = input("\nEnter tree_id (* for all)..." + PROMPT).strip()
    start = input("\nStart date (YYYY-MM-DD, blank = 30d)..." + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD, blank = 30d)..."   + PROMPT).strip()
    client.call("tree_sessions_last_clicked", tree, start, end)


def op_get_session_data(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_data")


def op_get_session_data_pure(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_data_pure")


def op_get_session_notes(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..." + PROMPT).strip()
    client.call("session", session, "get_session_notes")


def op_session_freeze(client: ZingtreeClient) -> None:
    session = input("\nEnter session_id..."             + PROMPT).strip()
    project = input("\nEnter project_id (tree id)..."   + PROMPT).strip()
    client.call("session_freeze", method="PUT",
                body={"session_id": session, "project_id": project})


def op_event_log(client: ZingtreeClient) -> None:
    start = input("\nStart date (YYYY-MM-DD, blank = 30d)..." + PROMPT).strip()
    end   = input("\nEnd date (YYYY-MM-DD, blank = 30d)..."   + PROMPT).strip()
    client.call("event_log", start, end)


def op_vault_get(client: ZingtreeClient) -> None:
    uid = input("\nEnter file_uid..." + PROMPT).strip()
    client.call("vault_files", uid)


def op_vault_delete(client: ZingtreeClient) -> None:
    uid = input("\nEnter file_uid..." + PROMPT).strip()
    client.call("vault_files", uid, method="DELETE")


OPERATIONS = {
    "agent_add":                  op_agent_add,
    "agent_add_inter":            op_agent_add_inter,
    "agent_tag":                  op_agent_tag,
    "agent_remove":               op_agent_remove,
    "agent_remove_inter":         op_agent_remove_inter,
    "search_trees":               op_search_trees,
    "get_tags":                   op_get_tags,
    "get_tree_tag_any":           op_get_tree_tag_any,
    "get_tree_tag_all":           op_get_tree_tag_all,
    "get_tree_variables":         op_get_tree_variables,
    "get_form_data":              op_get_form_data,
    "delete_form_data":           op_delete_form_data,
    "delete_file_upload":         op_delete_file_upload,
    "agent_sessions":             op_agent_sessions,
    "tree_sessions":              op_tree_sessions,
    "tree_sessions_last_clicked": op_tree_sessions_last_clicked,
    "get_session_data":           op_get_session_data,
    "get_session_data_pure":      op_get_session_data_pure,
    "get_session_notes":          op_get_session_notes,
    "session_freeze":             op_session_freeze,
    "event_log":                  op_event_log,
    "vault_get":                  op_vault_get,
    "vault_delete":               op_vault_delete,
}

# ----------------------------------------------------------------------------
# Menus
# ----------------------------------------------------------------------------

MAIN_ITEMS = {
    "0": ("agents",   "update agents"),
    "1": ("trees",    "get info on trees"),
    "2": ("forms",    "get or remove form data"),
    "3": ("sessions", "tree and agent session info"),
    "4": ("files",    "manage uploaded and vault files"),
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
        ("search_trees       (search all trees for matching text)", "search_trees"),
        ("get_tags           (fetch all tags used on trees)",       "get_tags"),
        ("get_tree_tag_any   (trees matching ANY tags)",            "get_tree_tag_any"),
        ("get_tree_tag_all   (trees matching ALL tags)",            "get_tree_tag_all"),
        ("get_tree_variables (variables defined within a tree)",    "get_tree_variables"),
    ]),
    "2": ("forms", [
        ("get_form_data    (form values entered during a session)", "get_form_data"),
        ("delete_form_data (delete any form data)",                 "delete_form_data"),
    ]),
    "3": ("sessions", [
        ("agent_sessions             (list agent sessions)",                "agent_sessions"),
        ("tree_sessions              (list tree sessions)",                 "tree_sessions"),
        ("tree_sessions_last_clicked (by last-click time)",                 "tree_sessions_last_clicked"),
        ("get_session_data           (form values entered during session)", "get_session_data"),
        ("get_session_data_pure      (linear path to tree)",                "get_session_data_pure"),
        ("get_session_notes          (agent notes from session)",           "get_session_notes"),
        ("session_freeze             (freeze a session)",                   "session_freeze"),
        ("event_log                  (event log for a date range)",         "event_log"),
    ]),
    "4": ("files", [
        ("delete_file_upload (delete an uploaded file)", "delete_file_upload"),
        ("vault_files get    (fetch a vault file URL)",  "vault_get"),
        ("vault_files delete (delete a vault file)",     "vault_delete"),
    ]),
}

META = """
╭─────────────────────────────────────────────────╮
│  Name    :: zinger
│  Source  :: https://github.com/dropbox/zinger
│  Author  :: Dillon Feeney
│  Licence :: Apache-2.0
│  Copyright (c) 2019 Dropbox, Inc.
│  Made with 🧁.
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
