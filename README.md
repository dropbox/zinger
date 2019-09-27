# zinger
`zinger` is a command-line utility for modifying agents and retrieving session
information via the [Zingtree RESTful API](http://www.zingtree.com/api/).

## Getting started
### Config
Set up `.env` file at root if running from script, or configure `python-dotenv`
for your own script/program.

`zingers.txt` should contain one agent config per line in the following format:
```
[email@domain],[Forename Surname],[all tags separated by comma]
bwinters@zingtree.com,Bob Winters,tag_0,tag_1
```

### Usage
Add it to your project's `lib/` or run `python3 zinger.py`. Make sure that you
have a text doc setup with the proper formatting. See "Config" section above.

## Supported endpoints
- `agent_add`
  - Adds a no-login agent to your organisation, so access must be through SSO
- `agent_tag`
  - Set or update comma-separated tags for an agent in your organisation
- `agent_remove`
  - Removes an agent from your organisation
- `agent_sessions`
  - Returns a JSON structure with session information for a particular agent
    (if `-`, returns all agents) and date range in ISO-8601 format (if `null`,
    returns last 30 days)
- `delete_form_data`
  - Deletes any form data entered into Zingtree during a session
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
  - Returns a JSON structure with all tags used in your organisation's trees.
- `get_trees`
  - Returns a JSON structure with information about all trees
- `get_tree_tag_all`
  - Returns a JSON structure with trees that have ALL tags in CSV-format
- `get_tree_tag_any`
  - Returns a JSON structure with trees that have ANY tags in CSV-format
- `search_trees`
  - Returns a JSON structure with information about all trees and nodes matching
   query
- `tree_sessions`
  - Returns a JSON structure with session information for a particular tree and
    date range in ISO-8601 format (if `null`, returns last 30 days)
  - You can also use date and time (PST) instead of date. These would be like
    YYYY-MM-DD HH:MM:SS. When calling a URL like this, replace the space
    character with %20 (YYYY-MM-DD%20HH:MM:SS)

## Misc
```
| Zingtree parameter | Zinger variable |
| ------------------ | --------------- |
| {{op}}           ‡ | zt_oper         |
| {{apikey}}       ‡ | zt_token        |
| {{agent login}}    | zt_email        |
| {{agent name}}     | zt_name         |
| {{tags}}           | zt_tags         |
| {{start date}}     | zt_start        |
| {{end date}}       | zt_end          |
| {{session ID}}     | zt_session      |
```

‡ == required

Note: `count` returns 0 if operation runs into Schröd-zinger's agent

---

## Licence
```
This project is libre and licenced APACHE-2.0; see the COPYING file or
https://www.apache.org/licenses/LICENSE-2.0 for more details.
```

---

Made with 🧁  at ◇⁵.
