#!/usr/bin/env python
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8
'''
Copyright © 2013
    Eric van der Vlist <vdv@dyomedea.com>
    Jens Neuhalfen <http://www.neuhalfen.name/>
See license information at the bottom of this file
'''

import re
import os
import ConfigParser
import ast
from datetime import datetime
from re import MULTILINE
import xmlrpclib
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

 * Python 2, xmlrpclib, requests
 * Trac with xmlrpc plugin enabled
 * Peewee (direct method)
 * GitLab

"""

default_config = {
    'ssl_verify': 'no',
    'migrate' : 'true',
    'overwrite' : 'true',
    'exclude_authors' : 'trac',
    'uploads' : ''
}

config = ConfigParser.ConfigParser(default_config)
config.read('migrate.cfg')


trac_url = config.get('source', 'url')
dest_project_name = config.get('target', 'project_name')
uploads_path = config.get('target', 'uploads')

method = config.get('target', 'method')


if (method == 'api'):
    from gitlab_api import Connection, Issues, Notes, Milestones
    print("importing api")
    gitlab_url = config.get('target', 'url')
    gitlab_access_token = config.get('target', 'access_token')
    dest_ssl_verify = config.getboolean('target', 'ssl_verify')
    overwrite = False
elif (method == 'direct'):
    print("importing direct")
    from gitlab_direct import Connection, Issues, Notes, Milestones
    db_name = config.get('target', 'db-name')
    db_password = config.get('target', 'db-password')
    db_user = config.get('target', 'db-user')
    db_path = config.get('target', 'db-path')
    overwrite = config.getboolean('target', 'overwrite')


users_map = ast.literal_eval(config.get('target', 'usernames'))
default_user = config.get('target', 'default_user')
must_convert_issues = config.getboolean('issues', 'migrate')
only_issues = None
if config.has_option('issues', 'only_issues'):
    only_issues = ast.literal_eval(config.get('issues', 'only_issues'))
blacklist_issues = None
if config.has_option('issues', 'blacklist_issues'):
    blacklist_issues = ast.literal_eval(config.get('issues', 'blacklist_issues'))
must_convert_wiki = config.getboolean('wiki', 'migrate')

pattern_changeset = r'(?sm)In \[changeset:"([^"/]+?)(?:/[^"]+)?"\]:\n\{\{\{(\n#![^\n]+)?\n(.*?)\n\}\}\}'
matcher_changeset = re.compile(pattern_changeset)

pattern_changeset2 = r'\[changeset:([a-zA-Z0-9]+)\]'
matcher_changeset2 = re.compile(pattern_changeset2)


def convert_xmlrpc_datetime(dt):
    return datetime.strptime(str(dt), "%Y%m%dT%H:%M:%S")


def format_changeset_comment(m):
    return 'In changeset ' + m.group(1) + ':\n> ' + m.group(3).replace('\n', '\n> ')


def fix_wiki_syntax(markup):
    markup = matcher_changeset.sub(format_changeset_comment, markup)
    markup = matcher_changeset2.sub(r'\1', markup)
    return markup

def get_dest_project_id(dest, dest_project_name):
    dest_project = dest.project_by_name(dest_project_name)
    if not dest_project:
        raise ValueError("Project '%s' not found" % dest_project_name)
    return dest_project["id"]

def get_dest_milestone_id(dest, dest_project_id,milestone_name):
    dest_milestone_id = dest.milestone_by_name(dest_project_id,milestone_name )
    if not dest_milestone_id:
        raise ValueError("Milestone '%s' of project '%s' not found" % (milestone_name, dest_project_name))
    return dest_milestone_id["id"]

def convert_issues(source, dest, dest_project_id, only_issues=None, blacklist_issues=None):
    if overwrite and (method == 'direct'):
        dest.clear_issues(dest_project_id)

    milestone_map_id={}
    for milestone_name in source.ticket.milestone.getAll():
        milestone = source.ticket.milestone.get(milestone_name)
        print(milestone)
        new_milestone = Milestones(
            description = trac2down.convert(fix_wiki_syntax(milestone['description']), '/milestones/', False),
            title = milestone['name'],
            state = 'active' if str(milestone['completed']) == '0'  else 'closed'
        )
        if method == 'direct':
            new_milestone.project = dest_project_id
        if milestone['due']:
            new_milestone.due_date = convert_xmlrpc_datetime(milestone['due'])
        new_milestone = dest.create_milestone(dest_project_id, new_milestone)
        milestone_map_id[milestone_name] = new_milestone.id

    get_all_tickets = xmlrpclib.MultiCall(source)

    for ticket in source.ticket.query("max=0&order=id"):
        get_all_tickets.ticket.get(ticket)

    for src_ticket in get_all_tickets():
        src_ticket_id = src_ticket[0]
        if only_issues and src_ticket_id not in only_issues:
            print("SKIP unwanted ticket #%s" % src_ticket_id)
            continue
        if blacklist_issues and src_ticket_id in blacklist_issues:
            print("SKIP blacklisted ticket #%s" % src_ticket_id)
            continue

        src_ticket_data = src_ticket[3]

        src_ticket_priority = src_ticket_data['priority']
        src_ticket_resolution = src_ticket_data['resolution']
        # src_ticket_severity = src_ticket_data['severity']
        src_ticket_status = src_ticket_data['status']
        src_ticket_component = src_ticket_data.get('component', '')

        new_labels = []
        if src_ticket_priority == 'high':
            new_labels.append('high priority')
        elif src_ticket_priority == 'medium':
            pass
        elif src_ticket_priority == 'low':
            new_labels.append('low priority')

        if src_ticket_resolution == '':
            # active ticket
            pass
        elif src_ticket_resolution == 'fixed':
            pass
        elif src_ticket_resolution == 'invalid':
            new_labels.append('invalid')
        elif src_ticket_resolution == 'wontfix':
            new_labels.append("won't fix")
        elif src_ticket_resolution == 'duplicate':
            new_labels.append('duplicate')
        elif src_ticket_resolution == 'worksforme':
            new_labels.append('works for me')

        # if src_ticket_severity == 'high':
        #     new_labels.append('critical')
        # elif src_ticket_severity == 'medium':
        #     pass
        # elif src_ticket_severity == 'low':
        #     new_labels.append("minor")

        # Current ticket types are: enhancement, defect, compilation, performance, style, scientific, task, requirement
        # new_labels.append(src_ticket_type)

        if src_ticket_component != '':
            for component in src_ticket_component.split(','):
                new_labels.append(component.strip())

        print("new labels: %s" % new_labels)

        new_state = ''
        if src_ticket_status == 'new':
            new_state = 'opened'
        elif src_ticket_status == 'assigned':
            new_state = 'opened'
        elif src_ticket_status == 'reopened':
            new_state = 'reopened'
        elif src_ticket_status == 'closed':
            new_state = 'closed'
        else:
            print("!!! unknown ticket status: %s" % src_ticket_status)

        # Minimal parameters
        new_issue = Issues(
            title=src_ticket_data['summary'],
            description=trac2down.convert(fix_wiki_syntax(src_ticket_data['description']), '/issues/', False),
            state=new_state,
            labels=",".join(new_labels)
        )

        if src_ticket_data['owner'] != '':
            try:
                new_issue.assignee = dest.get_user_id(users_map[src_ticket_data['owner']])
            except KeyError:
                new_issue.assignee = dest.get_user_id(default_user)
        # Additional parameters for direct access
        if (method == 'direct'):
            new_issue.created_at = convert_xmlrpc_datetime(src_ticket[1])
            new_issue.updated_at = convert_xmlrpc_datetime(src_ticket[2])
            new_issue.project = dest_project_id
            new_issue.state = new_state
            try:
                new_issue.author = dest.get_user_id(users_map[src_ticket_data['reporter']])
            except KeyError:
                new_issue.author = dest.get_user_id(default_user)
            if overwrite:
                new_issue.iid = src_ticket_id
            else:
                new_issue.iid = dest.get_issues_iid(dest_project_id)

        if 'milestone' in src_ticket_data:
            milestone = src_ticket_data['milestone']
            if milestone and milestone_map_id[milestone]:
                new_issue.milestone = milestone_map_id[milestone]
        new_ticket = dest.create_issue(dest_project_id, new_issue)
        # new_ticket_id  = new_ticket.id

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
                    note=trac2down.convert(fix_wiki_syntax(change[4]), '/issues/', False)
                )
                binary_attachment = None
                if (method == 'direct'):
                    note.created_at = convert_xmlrpc_datetime(change[0])
                    note.updated_at = convert_xmlrpc_datetime(change[0])
                    try:
                        note.author = dest.get_user_id(users_map[change[1]])
                    except KeyError:
                        note.author = dest.get_user_id(default_user)
                    if (is_attachment):
                        note.attachment = attachment[4]
                        binary_attachment = source.ticket.getAttachment(src_ticket_id, attachment[4].encode('utf8')).data
                dest.comment_issue(dest_project_id, new_ticket, note, binary_attachment)
                is_attachment = False

def convert_wiki(source, dest, dest_project_id):
    if overwrite and (method == 'direct'):
        dest.clear_wiki_attachments(dest_project_id)

    exclude_authors = [a.strip() for a in config.get('wiki', 'exclude_authors').split(',')]
    target_directory = config.get('wiki', 'target-directory')
    server = xmlrpclib.MultiCall(source)
    for name in source.wiki.getAllPages():
        info = source.wiki.getPageInfo(name)
        if (info['author'] not in exclude_authors):
            page = source.wiki.getPage(name)
            print("Page %s:%s" % (name, info))
            if (name == 'WikiStart'):
                name = 'home'
            converted = trac2down.convert(page, os.path.dirname('/wikis/%s' % name))
            if method == 'direct':
                for attachment in source.wiki.listAttachments(name):
                    print(attachment)
                    binary_attachment = source.wiki.getAttachment(attachment).data
                    try:
                        attachment_path = dest.create_wiki_attachment(dest_project_id, users_map[info['author']], convert_xmlrpc_datetime(info['lastModified']), attachment, binary_attachment)
                    except KeyError:
                        attachment_path = dest.create_wiki_attachment(dest_project_id, default_user, convert_xmlrpc_datetime(info['lastModified']), attachment, binary_attachment)
                    attachment_name = attachment.split('/')[-1]
                    converted = converted.replace(r'](%s)' % attachment_name, r'](%s)' % os.path.relpath(attachment_path, '/namespace/project/wiki/page'))
            trac2down.save_file(converted, name, info['version'], info['lastModified'], info['author'], target_directory)


if __name__ == "__main__":
    if method == 'api':
        dest = Connection(gitlab_url,gitlab_access_token,dest_ssl_verify)
    elif method == 'direct':
        dest = Connection(db_name, db_user, db_password, db_path, uploads_path)

    source = xmlrpclib.ServerProxy(trac_url)
    dest_project_id = get_dest_project_id(dest, dest_project_name)

    if must_convert_issues:
        convert_issues(source, dest, dest_project_id, only_issues=only_issues, blacklist_issues=blacklist_issues)

    if must_convert_wiki:
        convert_wiki(source, dest, dest_project_id)


'''
This file is part of <https://gitlab.dyomedea.com/vdv/trac-to-gitlab>.

This sotfware is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This sotfware is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this library. If not, see <http://www.gnu.org/licenses/>.
'''
