# zinger
`zinger` is a command-line utility for modifying agents, retrieving session
information, and querying trees via the
[Zingtree REST API (v1)](https://zingtree.com/api/).

## Getting started
### Config
Set up a `.env` file at root if running from script, or configure
`python-dotenv` for your own script/program.  You can copy `env_sample` and
rename it to `.env` (with a full-stop).  Fill in your API token.  Alternatively,
execute `export ZINGTREE_API_TOKEN="..."`

Requests authenticate with the `X-Api-Key` header.  You do not need to build it
yourself -- `zinger` reads `ZINGTREE_API_TOKEN` from `.env` and sets the header
on every call. The token never appears in the URL. The base URL is
`https://zingtree.com/api/v1/`.

`zingers.txt` should contain one agent config per line in the following format:
`[email@domain],[Forename Surname],[all tags separated by comma]`, example:

```
asummers@zingtree.com,Alice Summers,tag_0,tag_2
bwinters@zingtree.com,Bob Winters,tag_0,tag_1
```

### Requirements
- Python 3.9+
- `python-dotenv` (optional; only used to load `.env` -- if you don't use the
  `.env` file, you must add `ZINGTREE_API_TOKEN` to your environment variables).

### Usage
Add it to your project's `lib/` or run `python3 zinger.py`.  Make sure that you
have a text doc setup with the proper formatting. See "Config" section above.

## Supported endpoints
- `agent_add`
  - Adds a no-login agent to your organisation, so access must be through SSO
    or Google Authentication
- `agent_tag`
  - Set or update comma-separated tags for an agent in your organisation
- `agent_remove`
  - Removes an agent from your organisation
- `agent_sessions`
  - Returns a JSON structure with session information for a particular agent
    (if `*`, returns all agents) and date range in `YYYY-MM-DD` format (if
    blank, returns last 30 days)
- `delete_file_upload`
  - Deletes an uploaded file from the Zingtree servers, identified by folder
    and file name
- `delete_form_data`
  - Deletes any form data entered into Zingtree during a session
- `event_log`
  - Returns a JSON structure with the event log for your organisation in a date
    range. Start date and end date are in the form of `YYYY-MM-DD`. If blank,
    returns events for last 30 days. Dates are in PST.
- `get_form_data`
  - Outputs JSON with form variables and values entered during a session
- `get_session_data`
  - Returns a JSON structure with details about a session
- `get_session_data_pure`
  - Outputs JSON with details about a session. This is identical to
   `get_session_data`, except it eliminates the back and restart operations,
   returning a "pure" linear path through the tree
- `get_session_notes`
  - Returns a JSON structure with agent-entered notes from a session
- `get_tags`
  - Returns a JSON structure with all tags used in your organisation's trees
- `get_tree_tag_all`
  - Returns a JSON structure with trees that have ALL tags in a comma-delimited
    list
- `get_tree_tag_any`
  - Returns a JSON structure with trees that have ANY tags in a comma-delimited
    list
- `get_tree_variables`
  - Returns a JSON structure with the variables defined or used within a tree,
    by tree ID
- `search_trees`
  - Returns a JSON structure with information about all trees and nodes matching
   the query. Separate terms with `^^` for an AND search
- `session_freeze`
  - Freezes a session so it can no longer be resumed or shared. Issued as a PUT
    with a `session_id` and `project_id` (tree ID). A resume attempt afterwards
    starts a fresh session with a new ID
- `tree_sessions`
  - Returns a JSON structure with session information for a particular tree (if
    `*`, returns all trees) and date range in `YYYY-MM-DD` format (if blank,
    returns last 30 days)
  - You can also use date and time (PST) instead of date. These would be like
    YYYY-MM-DD HH:MM:SS. When calling a URL like this, replace the space
    character with %20 (YYYY-MM-DD%20HH:MM:SS)
- `tree_sessions_last_clicked`
  - As `tree_sessions`, but the date range applies to the time of the last
    click rather than session start
- `vault_files`
  - Retrieves or deletes a session Vault File by `file_uid`. A GET returns a
    `download_url` valid for 60 seconds; a DELETE removes the file

## Misc
```
| Zingtree parameter   | zinger input  |
| -------------------- | ------------- |
| X-Api-Key (header) ‡ | token (.env)  |
| {{agent login}}      | email         |
| {{agent name}}       | name          |
| {{tags}}             | tags          |
| {{tree ID}}          | tree          |
| {{session ID}}       | session       |
| {{file_uid}}         | uid           |
| {{folder}} {{file}}  | folder, file  |
| {{start date}}       | start         |
| {{end date}}         | end           |
```

‡ == required

Notes:
- The operation is selected from the menu and encoded in the endpoint path; it
  is no longer passed as an `op` parameter.
- For production sessions, append triple zeros (`000`) to the tree ID.
- There is a limit of 6000 API calls per day for each organisation.

Note: `count` returns 0 if operation runs into Schröd-zinger's agent.

---

## Licence
```
Copyright 2019  Dropbox, Inc.
Copyright 2026  Dillon Feeney.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

Made with 🧁 .
