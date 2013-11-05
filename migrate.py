#!/usr/bin/python3
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8
import re
import configparser
from datetime import datetime
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

 * ```Python 3.2, xmlrpclib, requests```
 * Trac with xmlrpc plugin enabled
 * Gitlab

"""

default_config = {
    'ssl_verify': 'no',
    'migrate' : 'yes',
    'overwrite' : 'yes',
    'exclude_authors' : 'trac',
    'uploads' : ''
}

config = configparser.ConfigParser(default_config)
config.read('migrate.cfg')


trac_url = config.get('source', 'url')
dest_project_name = config.get('target', 'project_name')
uploads_path = config.get('target', 'uploads')

method = config.get('target', 'method')

def create_users_map(usernames):
    umap = {}
    for user in usernames.split(','):
        (trac, gitlab) = user.split('->')
        umap[trac.strip()] = gitlab.strip()
    print(umap)
    return umap


if (method == 'api'):
    from gitlab_api import Connection, Issues, Notes, Milestones
    gitlab_url = config.get('target', 'url')
    gitlab_access_token = config.get('target', 'access_token')
    dest_ssl_verify = config.getboolean('target', 'ssl_verify')
    overwrite = config.getboolean('target', 'overwrite')
elif (method == 'direct'):
    from gitlab_direct import Connection, Issues, Notes, Milestones
    db_name = config.get('target', 'db-name')
    db_password = config.get('target', 'db-password')
    db_user = config.get('target', 'db-user')

users_map = create_users_map(config.get('target', 'usernames'))
must_convert_issues = config.getboolean('issues', 'migrate')
must_convert_wiki = config.getboolean('wiki', 'migrate')

def convert_xmlrpc_datetime(dt):
    return datetime.strptime(str(dt), "%Y%m%dT%H:%M:%S")

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
    
    if overwrite and (method == 'direct'):
        dest.clear_database(dest_project_id)
    
    milestone_map_id={}
    for milestone_name in source.ticket.milestone.getAll():
        milestone = source.ticket.milestone.get(milestone_name)
        new_milestone = Milestones(
            description = milestone['description'],
            title = milestone['name'],
            state = 'active' if milestone['completed'] == 0 else 'completed'
        )
        if method == 'direct':
            new_milestone.project = dest_project_id
            if overwrite:
                new_milestone.iid = milestone['id']
        if milestone['due']:
            new_milestone.due_date = convert_xmlrpc_datetime(milestone['due'])
        new_milestone = dest.create_milestone(dest_project_id, new_milestone)
        milestone_map_id[milestone_name] = new_milestone.id
            
    print(milestone_map_id)
    
    get_all_tickets = xmlrpc.client.MultiCall(source)

    for ticket in source.ticket.query("max=0"):
        get_all_tickets.ticket.get(ticket)

    for src_ticket in get_all_tickets():
        src_ticket_id = src_ticket[0]
        src_ticket_data = src_ticket[3]

        is_closed =  src_ticket_data['status'] == "closed"
        # Minimal parameters
        new_issue = Issues (
            title = src_ticket_data['summary'],
            description = trac2down.convert(fix_wiki_syntax( src_ticket_data['description']), '/issues/'),
            state = 'closed' if is_closed else 'opened',
            labels = ",".join( [src_ticket_data['type'], src_ticket_data['component'], src_ticket_data['type']] ),
            assignee = dest.get_user_id(users_map[src_ticket_data['owner']])
        )
        # Additional parameters for direct access
        if (method == 'direct'):
            new_issue.created_at = convert_xmlrpc_datetime(src_ticket[1])
            new_issue.updated_at = convert_xmlrpc_datetime(src_ticket[2])
            new_issue.project = dest_project_id
            new_issue.state = 'closed' if is_closed else 'opened'
            new_issue.author = dest.get_user_id(users_map[src_ticket_data['reporter']])
            if overwrite:
                new_issue.iid = src_ticket_id
            else:
                new_issue.iid = dest.get_issues_iid(dest_project_id)

        milestone = src_ticket_data['milestone']
        if milestone and milestone_map_id[milestone]:
            new_issue.milestone = milestone_map_id[milestone]
        new_ticket = dest.create_issue(dest_project_id, new_issue)
        new_ticket_id  = new_ticket.id

        changelog = source.ticket.changeLog(src_ticket_id)
        is_attachment = False
        for change in changelog:
            change_type = change[2]
            if change_type == "attachment":
                # The attachment will be described in the next change!
                is_attachment = True
                attachment = change
            if (change_type == "comment") and change[4] != '':
                note = Notes(
                    note = trac2down.convert(fix_wiki_syntax( change[4]), '/issues/')
                )
                binary_attachment = None
                if (method == 'direct'):
                    note.created_at = convert_xmlrpc_datetime(change[0])
                    note.updated_at = convert_xmlrpc_datetime(change[0])
                    note.author = dest.get_user_id(users_map[change[1]])
                    if (is_attachment):
                        note.attachment = attachment[4]
                        binary_attachment = source.ticket.getAttachment(src_ticket_id, attachment[4]).data
                dest.comment_issue(dest_project_id, new_ticket, note, binary_attachment)
                is_attachment = False

def convert_wiki(source, dest, dest_project_id):
    exclude_authors = [a.strip() for a in config.get('wiki', 'exclude_authors').split(',')]
    target_directory = config.get('wiki', 'target-directory')
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
        dest = Connection(db_name, db_user, db_password, uploads_path)
    
    source = xmlrpc.client.ServerProxy(trac_url)
    dest_project_id = get_dest_project_id(dest_project_name)

    if must_convert_issues:
        convert_issues(source, dest, dest_project_id)

    if must_convert_wiki:
        convert_wiki(source, dest, dest_project_id)



