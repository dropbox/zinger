#!/usr/bin/env python3

from dotenv  import load_dotenv
from pathlib import Path
from os.path import join

import os
import pycurl
import subprocess as subp
import sys
import time

################################################################
#
# Zingtree API:
#     https://zingtree.com/api/
#
# API token available from:
#     https://zingtree.com/account/organizations.php -> `API Key`
#     Add token to .env file as `ZINGTREE_API_TOKEN=""`
#
# This project is libre and licenced APACHE-2.0; see the COPYING file or
# https://www.apache.org/licenses/LICENSE-2.0 for more details.
#
################################################################

env_path  = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

zt_list    = "zingers.txt"
zt_api_url = "https://zingtree.com/api/"
zt_token   = os.getenv("ZINGTREE_API_TOKEN")

################################################################

def call_zt(zt_url):
    """
    makes call to Zingtree API endpoint
    """
    # only show first 8 chars of token
    zt_url_clean = zt_url.replace(zt_token, zt_token[:5] + "…")
    print("\nCalling URL... {}".format(zt_url_clean))
    pc = pycurl.Curl()
    pc.setopt(pc.URL, zt_url)
    pc.perform()
    pc.close()

################################################################

def main():
    if zt_token == "":
        print("Token null, please update ZINGTREE_API_TOKEN in `.env` file.")
        time.sleep(3)
        quit_now()
    zt_oper = ""
    menu(input_menu="main")
    input_menu = input("\nSelect Option from above: " + uil())
    if input_menu == "0":
        menu(input_menu)
        input_users = input("\nSelect Option from above: " + uil())
        if input_users == "0":
            zt_oper = "agent_add"
        elif input_users == "1":
            zt_oper = "agent_add_inter"
        elif input_users == "2":
            zt_oper = "agent_tag"
        elif input_users == "3":
            zt_oper = "agent_remove"
        elif input_users == "4":
            zt_oper = "agent_remove_inter"
        elif input_users.upper() == "Q":
            quit_now()
        else:
            main()

    elif input_menu == "1":
        menu(input_menu)
        input_trees = input("\nSelect Option from above: " + uil())
        if input_trees == "0":
            zt_oper = "search_trees"
        elif input_trees == "1":
            zt_oper = "get_trees"
        elif input_trees == "2":
            zt_oper = "get_tags"
        elif input_trees == "3":
            zt_oper = "get_tree_tag_any"
        elif input_trees == "4":
            zt_oper = "get_tree_tag_all"
        elif input_trees.upper() == "Q":
            quit_now()
        else:
            main()

    elif input_menu == "2":
        menu(input_menu)
        input_forms = input("\nSelect Option from above: " + uil())
        if input_forms == "0":
            zt_oper = "get_form_data"
        elif input_forms == "1":
            zt_oper = "delete_form_data"
        elif input_forms.upper() == "Q":
            quit_now()
        else:
            main()

    elif input_menu == "3":
        menu(input_menu)
        input_sessions = input("\nSelect Option from above: " + uil())
        if input_sessions == "0":
            zt_oper = "agent_sessions"
        elif input_sessions == "1":
            zt_oper = "tree_sessions"
        elif input_sessions == "2":
            zt_oper = "get_session_data"
        elif input_sessions == "3":
            zt_oper = "get_session_data_pure"
        elif input_sessions == "4":
            zt_oper = "get_session_notes"
        elif input_sessions == "5":
            zt_oper = "event_log"
        elif input_sessions.upper() == "Q":
            quit_now()
        else:
            main()

    elif input_menu == "00":
        headers()
        time.sleep(5)
        subp.call(["clear"])

    elif input_menu.upper() == "Q":
        quit_now()

    else:
        main()

    handle_decision(zt_oper)

################################################################

def menu(input_menu):
    length_border = "=" * 80
    top_border    = "\n" + "╭╭" + length_border + "╮╮\n||"
    bottom_border = "\n||\n╰╰" + length_border + "╯╯"

    if input_menu == "main":
        print(top_border + """
||    zinger | main menu\n||
||    ================\n||
||    [0]  agents   (updates agents)
||    [1]  trees    (get info on trees)
||    [2]  forms    (get or remove form info entered on trees)
||    [3]  sessions (tree and agent session info)\n||
||    [00] μετά     (prints meta)\n||
||    ================\n||
||    [Q]  Q to quit""" + bottom_border)

    elif input_menu == "0":
        print(top_border + """
||    zinger | agents menu\n||
||    ================\n||
||    [0] auto `agent_add`      (from file)
||    [1] manual `agent_add`    (interactive)
||    [2] auto `agent_tag`      (from file)
||    [3] auto `agent_remove`   (removes agents)
||    [4] manual `agent_remove` (interactive)\n||
||    ================\n||
||    zingers.txt doc should be formatted like:\n||
||        `bwinters@zingtree.com,Bob Winters,tag_0,tag_1`\n||
||    ================\n||
||    [Q]  Q to quit""" + bottom_border)

    elif input_menu == "1":
        print(top_border + """
||    zinger | trees menu\n||
||    ================\n||
||    [0] `search_trees`     (search all trees for matching text)
||    [1] `get_trees`        (fetches all trees)
||    [2] `get_tags`         (fetches all tags used on trees)
||    [3] `get_tree_tag_any` (gets trees matching \x1B[3mANY\x1B[23m tags)
||    [4] `get_tree_tag_all` (gets trees matching \033[1mALL\033[0m tags)\n||
||    ================\n||
||    [Q]  Q to quit""" + bottom_border)

    elif input_menu == "2":
        print(top_border + """
||    zinger | forms menu\n||
||    ================\n||
||    [0] `get_form_data`    (form values entered during a session)
||    [1] `delete_form_data` (deletes any form data)\n||
||    ================\n||
||    [Q]  Q to quit""" + bottom_border)

    elif input_menu == "3":
        print(top_border + """
||    zinger | sessions menu\n||
||    ================\n||
||    [0] `agent_sessions`        (lists agent sessions)
||    [1] `tree_sessions`         (lists tree sessions)
||    [2] `get_session_data`      (returns form values entered during session)
||    [3] `get_session_data_pure` (`get_session_data`, with linear path to tree)
||    [4] `get_session_notes`     (returns agent notes from session)
||    [5] `event_log`             (returns event log for date range)\n||
||    ================\n||
||    [Q]  Q to quit""" + bottom_border)

################################################################

def uil():
    """
    user_input_line():
    """
    user_input = "\n\n  ==> "
    return user_input

def input_agent_info():
    zt_name  = input('\nEnter agent\'s name...' + uil())
    zt_email = input('\nEnter agent\'s email...' + uil())
    zt_tags  = input('\nEnter agent\'s tags...' + uil())
    return zt_name, zt_email, zt_tags

def input_agent_email():
    zt_email = input('\nEnter agent\'s email...' + uil())
    return zt_email

def quit_now():
    """
    quits application nicely
    """
    print("\nQuitting... Goodbye...\n")
    time.sleep(0.3)
    sys.exit(0)

def exit_now():
    """
    quits applications not nicely
    """
    print("\nExiting, bad input...\n")
    sys.exit(1)

################################################################

def headers():
    __copyright__  = ""
    print("""
╭╭===================================================╮╮\n||
||  Name    :: zinger
||  Source  :: https://github.com/dropbox/zinger
||  Contact :: dillon. <dillon@dropbox.com>
||  Licence :: Apache-2.0\n||
||  Copyright © 2019 Dropbox, Inc.\n||
||  Made with 🧁  at ◇⁵.\n||
╰╰===================================================╯╯
    """)

def print_doc(zt_oper_en, lines):
    for line in lines:
        line = line.split(",")
        print("""
    Name  : {}
    Email : {}
    Tags  : {}
        """.format(line[1], line[0], line[2:]))
    # Italicise and embolden action to be taken
    confirm = input("""   This will \033[1m\x1B[3m{}\x1B[23m\033[0m the above agents...\n
    Continue? (Y/n)""".format(zt_oper_en) + uil())
    return confirm

def handle_decision(zt_oper):
    """
    gets users from list of formatted lines in text doc

    `[email@domain],[Forename Surname],[comma-separated tags]`
    """

    try:
        text_doc = open(zt_list).readlines()
    except FileNotFoundError:
        print("{} doc not found.\n".format(zt_list))
        exit_now()

    lines = [line.rstrip("\n") for line in text_doc]

    if zt_oper == "main":
        main()

    elif zt_oper == "agent_add":
        # zt_api/agent_add/{{apikey}}/{{agent name}}/{{agent login}}
        zt_oper_en = "[ADD] & [TAG]"
        confirm = print_doc(zt_oper_en, lines)
        if confirm.upper() == "Y":
            print("Creating Zingtree agents...\n")
            for line in lines:
                line     = line.split(",")
                zt_email = line[0].strip()
                zt_oper = "agent_add"
                zt_name  = line[1].strip()
                zt_url   = "{}{}/{}/{}/{}".format(zt_api_url,
                                                  zt_oper,
                                                  zt_token,
                                                  zt_name,
                                                  zt_email)
                call_zt(zt_url)
                zt_oper = "agent_tag"
                zt_tags = "/" + ",".join(map(str, line[2:])).strip()
                zt_url  = "{}{}/{}/{}{}".format(zt_api_url,
                                                zt_oper,
                                                zt_token,
                                                zt_email,
                                                zt_tags)
                call_zt(zt_url)
        else:
            quit_now()

    elif zt_oper == "agent_add_inter":
        zt_oper = "agent_add"
        zt_name, zt_email, zt_tags = input_agent_info()
        zt_url  = "{}{}/{}/{}/{}".format(zt_api_url,
                                         zt_oper,
                                         zt_token,
                                         zt_name,
                                         zt_email)
        call_zt(zt_url)
        zt_oper = "agent_tag"
        zt_url  = "{}{}/{}/{}/{}".format(zt_api_url,
                                         zt_oper,
                                         zt_token,
                                         zt_email,
                                         zt_tags)
        call_zt(zt_url)

    elif zt_oper == "agent_tag":
        # zt_api/agent_tag/{{apikey}}/{{agent login}}/{{tags}}
        zt_oper_en = "[TAG]"
        confirm = print_doc(zt_oper_en, lines)
        if confirm.upper() == "Y":
            print("Updating Zingtree agents' tag(s)...\n")
            for line in lines:
                line     = line.split(",")
                zt_email = line[0].strip()
                zt_tags  = "/" + ",".join(map(str, line[2:])).strip()
                zt_url   = "{}{}/{}/{}{}".format(zt_api_url,
                                                 zt_oper,
                                                 zt_token,
                                                 zt_email,
                                                 zt_tags)
                call_zt(zt_url)
        else:
            quit_now()

    elif zt_oper == "agent_remove":
        # zt_api/agent_remove/{{apikey}}/{{agent login}}
        zt_oper_en = "[REMOVE]"
        confirm = print_doc(zt_oper_en, lines)
        if confirm.upper() == "Y":
            print("Removing Zingtree agents...\n")
            for line in lines:
                line     = line.split(",")
                zt_email = line[0].strip()
                zt_url   = "{}{}/{}/{}".format(zt_api_url,
                                               zt_oper,
                                               zt_token,
                                               zt_email)
                call_zt(zt_url)
        else:
            quit_now()

    elif zt_oper == "agent_remove_inter":
        zt_oper  = "agent_remove"
        zt_email = input_agent_email()
        zt_url   = "{}{}/{}/{}".format(zt_api_url,
                                       zt_oper,
                                       zt_token,
                                       zt_email)
        call_zt(zt_url)

    elif zt_oper == "get_tags":
        # zt_api/tree/{{apikey}}/get_tags
        print("Getting tags from tree...")
        zt_url = "{}tree/{}/{}".format(zt_api_url,
                                       zt_token,
                                       zt_oper)
        call_zt(zt_url)

    elif zt_oper == "get_trees":
        # zt_api/tree/{{apikey}}/get_trees
        print("Climbing trees...")
        zt_url = "{}tree/{}/{}".format(zt_api_url,
                                       zt_token,
                                       zt_oper)
        call_zt(zt_url)

    elif zt_oper == "get_tree_tag_all":
        # zt_api/tree/{{apikey}}/get_tree_tag_all/{{taglist}}
        print("Picking ALL tags from trees...")
        zt_tags = input("\nSearch tree by comma-separated tags..." + uil())
        zt_url  = "{}tree/{}/{}/{}".format(zt_api_url,
                                           zt_token,
                                           zt_oper,
                                           zt_tags)
        call_zt(zt_url)

    elif zt_oper == "get_tree_tag_any":
        # zt_api/tree/{{apikey}}/get_tree_tag_any/{{taglist}}
        print("Picking ANY tags from trees...")
        zt_tags = input("\nSearch tree by comma-separated tags..." + uil())
        zt_url  = "{}tree/{}/{}/{}".format(zt_api_url,
                                           zt_token,
                                           zt_oper,
                                           zt_tags)
        call_zt(zt_url)

    elif zt_oper == "search_trees":
        # zt_api/tree/{{apikey}}/search_trees/{{search text}}
        print("Scanning leaves...")
        zt_query = input("\nEnter query..." + uil())
        zt_url   = "{}tree/{}/{}/{}".format(zt_api_url,
                                            zt_token,
                                            zt_oper,
                                            zt_query)
        call_zt(zt_url)

    elif zt_oper == "get_form_data":
        # zt_api/session/{{session ID}}/get_form_data
        print("Getting form data...")
        zt_session = input("\nEnter session_id..." + uil())
        zt_url     = "{}session/{}/{}".format(zt_api_url,
                                             zt_session,
                                             zt_oper)
        call_zt(zt_url)

    elif zt_oper == "delete_form_data":
        # zt_api/session/{{session ID}}/delete_form_data
        print("Deleting form data...")
        zt_session = input("\nEnter session_id..." + uil())
        zt_url     = "{}session/{}/{}".format(zt_api_url,
                                              zt_session,
                                              zt_oper)
        call_zt(zt_url)

    elif zt_oper == "event_log":
        # zt_api/event_log/{{apikey}}/{{start date}}/{{end date}}
        print("Showing event log...")
        zt_start = input("\nStart date..." + uil())
        zt_end   = input("\nEnd date..." + uil())
        zt_url   = "{}{}/{}/{}/{}".format(zt_api_url,
                                          zt_oper,
                                          zt_token,
                                          zt_start,
                                          zt_end)
        call_zt(zt_url)

    elif zt_oper == "agent_sessions":
        # zt_api/agent_sessions/{{apikey}}/{{agent}}/{{start date}}/{{end date}}
        print("Gathering agent sessions...")
        for line in lines:
            line     = line.split(",")
            zt_email = line[0].strip()
            zt_start = input("\nStart date - {}...".format(zt_email) + uil())
            zt_end   = input("\nEnd date - {}...".format(zt_email) + uil())
            zt_url   = "{}{}/{}/{}/{}/{}".format(zt_api_url,
                                                 zt_oper,
                                                 zt_token,
                                                 zt_email,
                                                 zt_start,
                                                 zt_end)
            call_zt(zt_url)

    elif zt_oper == "tree_sessions":
        # zt_api/tree_sessions/{{apikey}}/{{tree ID}}/{{start}}/{{end}}
        print("Gathering tree sessions...")
        zt_tree  = input("\nEnter tree_id..." + uil())
        zt_start = input("\nStart date - {}...".format(zt_tree) + uil())
        zt_end   = input("\nEnd date - {}...".format(zt_tree) + uil())
        zt_url   = "{}{}/{}/{}/{}/{}".format(zt_api_url,
                                             zt_oper,
                                             zt_token,
                                             zt_tree,
                                             zt_start,
                                             zt_end)
        call_zt(zt_url)

    elif zt_oper == "get_session_data":
        # zt_api/session/{{session ID}}/get_session_data
        print("Getting session data...")
        zt_session = input("\nEnter session_id..." + uil())
        zt_url     = "{}session/{}/{}".format(zt_api_url,
                                              zt_session,
                                              zt_oper)
        call_zt(zt_url)

    elif zt_oper == "get_session_data_pure":
        # zt_api/session/{{session ID}}/get_session_data_pure
        print("Getting form data...")
        zt_session = input("\nEnter session_id..." + uil())
        zt_url     = "{}session/{}/{}".format(zt_api_url,
                                              zt_session,
                                              zt_oper)
        call_zt(zt_url)

    elif zt_oper == "get_session_notes":
        # zt_api/session/{{session ID}}/get_session_notes
        print("Getting form data...")
        zt_session = input("\nEnter session_id..." + uil())
        zt_url     = "{}session/{}/{}".format(zt_api_url,
                                              zt_session,
                                              zt_oper)
        call_zt(zt_url)

    elif zt_oper.upper() == "Q":
        quit_now()

    time.sleep(0.5)
    main()

if __name__ == "__main__":
    subp.call(["clear"])
    main()
