#!/usr/bin/env python
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8
'''
Copyright © 2013 
    Eric van der Vlist <vdv@dyomedea.com>
    Jens Neuhalfen <http://www.neuhalfen.name/>
See license information at the bottom of this file
'''

import ConfigParser
import ast
import xmlrpclib
import sys

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

reload(sys)
sys.setdefaultencoding('utf-8')

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
users_map = ast.literal_eval(config.get('target', 'usernames'))

method = config.get('target', 'method')

ticket_owners = set()
ticket_reporters = set()
ticket_message_posters = set()

if method == 'api':
    from gitlab_api import Connection

    gitlab_url = config.get('target', 'url')
    gitlab_access_token = config.get('target', 'access_token')
    dest_ssl_verify = config.getboolean('target', 'ssl_verify')
elif method == 'direct':
    from gitlab_direct import Connection

    db_name = config.get('target', 'db-name')
    db_password = config.get('target', 'db-password')
    db_user = config.get('target', 'db-user')


def collect_users(source):

    get_all_tickets = xmlrpclib.MultiCall(source)

    for ticket in source.ticket.query("max=0&order=id"):
        get_all_tickets.ticket.get(ticket)

    ticket_index = 0

    for src_ticket in get_all_tickets():
        src_ticket_id = src_ticket[0]
        src_ticket_data = src_ticket[3]

        print("ticket id: %s" % src_ticket_id)
        print("ticket index: %s" % ticket_index)
        print("owner: %s" % src_ticket_data['owner'])
        print("reporter: %s" % src_ticket_data['reporter'])
        ticket_owners.add(src_ticket_data['owner'])
        ticket_reporters.add(src_ticket_data['reporter'])

        try:
            changelog = source.ticket.changeLog(src_ticket_id)
            for change in changelog:
                change_type = change[2]
                if (change_type == "comment") and change[4] != '':
                    print("ticket message poster: %s" % change[1])
                    ticket_message_posters.add(change[1])
        except Exception as e:
            print("unable to parse change log for ticket id %s" % src_ticket_id)
            print >> sys.stderr, "ticket: ", src_ticket_id, e

        ticket_index += 1


if __name__ == "__main__":

    if method == 'api':
        dest = Connection(gitlab_url,gitlab_access_token,dest_ssl_verify)
    elif method == 'direct':
        dest = Connection(db_name, db_user, db_password, uploads_path, dest_project_name)
                        
    for user in set(users_map.values()):
        try:
            gitlab_user = dest.get_user_id(user)
        except:
            print("User does not exist in GitLab: %s" % user)

    source = xmlrpclib.ServerProxy(trac_url, encoding = 'UTF-8')

    collect_users(source)

    print("--------")
    print("Ticket owners:")
    print(ticket_owners)
    print("Ticket reporters:")
    print(ticket_reporters)
    print("Ticket message posters:")
    print(ticket_message_posters)

    print("")
    print("--------")
    print("")
    print("User mappings (copy-paste it into the configuration file and fill in the missing values):")
    print("")
    print("usernames = {")
    for user in ticket_owners.union(ticket_reporters).union(ticket_message_posters):
        if user in users_map.keys():
            print("    u'%s': u'%s'," % (user, users_map[user]))
        else:
            print("    u'%s': u''," % user)
    print("    }")

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
