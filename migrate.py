#!/usr/bin/python3
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8
import re
import configparser
from re import MULTILINE
import xmlrpc.client
import trac2down
"""
What
=====

 This script migrates issues from trac to gitlab.

License
========

 License: http://www.wtfpl.net/

Requirements
==============

 * ```Python 2.7, xmlrpclib, requests```
 * Trac with xmlrpc plugin enabled
 * Gitlab

"""

default_config = {
    'ssl_verify': 'no',
    'migrate' : 'yes',
    'exclude_authors' : 'trac'
}

config = configparser.ConfigParser(default_config)
config.read('migrate.cfg')


trac_url = config.get('source', 'url')
dest_project_name = config.get('target', 'project_name')

method = config.get('target', 'method')

if (method == 'api'):
    from gitlab_api import Connection, Issues
    gitlab_url = config.get('target', 'url')
    gitlab_access_token = config.get('target', 'access_token')
    dest_ssl_verify = config.getboolean('target', 'ssl_verify')
elif (method == 'direct'):
    from gitlab_direct import Connection, Issues
    db_name = config.get('target', 'db-name')
    db_password = config.get('target', 'db-password')
    db_user = config.get('target', 'db-user')


must_convert_issues = config.getboolean('issues', 'migrate')
must_convert_wiki = config.getboolean('wiki', 'migrate')


milestone_map = {"1.0":"1.0", "2.0":"2.0" }
"------"

def fix_wiki_syntax(markup):
    markup = re.sub(r'#!CommitTicketReference.*\n',"",markup, flags=MULTILINE)

    # [changeset:"afsd38..2fs/taskninja"] or [changeset:"afsd38..2fs"]
    markup = re.sub(r'\[changeset:"([^"/]+?)(?:/[^"]+)?"]',r"changeset \1",markup)

    return markup


def get_dest_project_id(dest_project_name):
    dest_project = dest.project_by_name(dest_project_name)
    if not dest_project: raise ValueError("Project '%s' not found under '%s'" % (dest_project_name, gitlab_url))
    return dest_project["id"]

def get_dest_milestone_id(dest_project_id,milestone_name):
    dest_milestone_id = dest.milestone_by_name(dest_project_id,milestone_name )
    if not dest_milestone_id: raise ValueError("Milestone '%s' of project '%s' not found" % (milestone_name,dest_project_name))
    return dest_milestone_id["id"]

def convert_issues(source, dest, dest_project_id):
    milestone_map_id={}
    for mstracname, msgitlabname in milestone_map.items():
        milestone_map_id[mstracname]=get_dest_milestone_id(dest_project_id, msgitlabname)

    get_all_tickets = xmlrpc.client.MultiCall(source)

    for ticket in source.ticket.query("max=0"):
        get_all_tickets.ticket.get(ticket)

    for src_ticket in get_all_tickets():
        print (src_ticket)
        src_ticket_id = src_ticket[0]
        src_ticket_data = src_ticket[3]

        is_closed =  src_ticket_data['status'] == "closed"
        new_issue = Issues(
            title = src_ticket_data['summary'],
            description = trac2down.convert(fix_wiki_syntax( src_ticket_data['description']), '/issues/'),
            closed = 1 if is_closed else 0,
            labels = ",".join( [src_ticket_data['type'], src_ticket_data['component']] )
        )

        milestone = src_ticket_data['milestone']
        if milestone and milestone_map_id[milestone]:
            new_issue.milestone = milestone_map_id[milestone]
        new_ticket = dest.create_issue(dest_project_id, new_issue)
        new_ticket_id  = new_ticket["id"]

        changelog = source.ticket.changeLog(src_ticket_id)
        for change in changelog:
            print(change)
            change_type = change[2]
            if (change_type == "comment"):
                comment = trac2down.convert(fix_wiki_syntax( change[4]), '/issues/')
                dest.comment_issue(dest_project_id,new_ticket_id,comment)

def convert_wiki(source, dest, dest_project_id):
    exclude_authors = [a.strip() for a in config.get('wiki', 'exclude_authors').split(',')]
    target_directory = config.get('wiki', 'target_directory')
    server = xmlrpc.client.MultiCall(source)
    for name in source.wiki.getAllPages():
        info = source.wiki.getPageInfo(name)
        if (info['author'] not in exclude_authors):
            page = source.wiki.getPage(name)
            # print "Page %s:%s|%s" % (name, info, page)
            if (name == 'WikiStart'):
                name = 'home'
            trac2down.save_file(trac2down.convert(page, '/wikis/'), name, info['version'], info['lastModified'], info['author'], target_directory)
        

if __name__ == "__main__":
    if method == 'api':
        dest = Connection(gitlab_url,gitlab_access_token,dest_ssl_verify)
    elif method == 'direct':
        dest = Connection(db_name, db_user, db_password)
    
    source = xmlrpc.client.ServerProxy(trac_url)
    dest_project_id = get_dest_project_id(dest_project_name)

    if must_convert_issues:
        convert_issues(source, dest, dest_project_id)

    if must_convert_wiki:
        convert_wiki(source, dest, dest_project_id)



