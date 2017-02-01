What
=====

 This script migrates milestones, issues and wiki pages from trac to gitlab.

Features
--------
 * Component & Issue-Type are converted to labels
 * Comments to issues are copied over
 * Supports two modes of tansfer:
  * Using GitLab web API
  * Direct access through GitLab's database and file system
 * In direct mode, attachments are transfered and the issues and notes dates and ownership are preserved
 * In API mode, attachments are not transfered, issues and notes are owned by a single user and their dates are the current date.

How
====

Migrating a trac project to GitLab is a relatively complex process involving fours steps:

 * Create a new project
 * Migrate the repository (can just be cloning a git repository if the trac project is already using git or could involve converting from subversion using git-svn)
 * Create the users for the project
 * Migrate issues and milestones
 * Migrate wiki pages

This script takes care of the last two bullet points and provides help for the third one.

 Usage:

  1. copy ```migrate.cfg.example``` to ```migrate.cfg```
  2. configure the values
  3. run ```./collect-users.py``` to extract the user names from Trac
  4. update ```migrate.cfg``` and create the users in GitLab
  5. run (```./migrate.py```). Make sure you test it on a test project prior, if you run it twice against the same project you will get duplicated issues unless you're using direct access with overwrite set to yes.

Issues and milestones are copied to GitLab.

Wiki pages are copied to a folder on your machine and must be pushed into GitLab using wiki's git access.

GitLab versions
===============

The database model should correspond to the version of GitLab that you are using.

This repo contains models for multiple versions (gitlab_direct/model<version>.py) and the version number should be updated correspondingly in the imports in [gitlab_direct/__init__.py](gitlab_direct/__init__.py) and [gitlab_direct/Connection.py](gitlab_direct/Connection.py).

To support a new version, use pwiz.py:

```
$ pwiz.py -e postgresql -u gitlab gitlabhq_production > gitlab_direct/model<version>.py
```

Manual updates must then be applied, see for instance the [manual updates for 6.4](https://gitlab.dyomedea.com/vdv/trac-to-gitlab/commit/8a5592a7b996054849bf7ac21fd5fec267db1df9).

Configuration
=============

The configuration must be located in a file named "migrate.cfg"

Source
-------

 * ```url``` - xmlrpc url to trac, e.g. ```https://user:secret@www.example.com/projects/thisismyproject/login/xmlrpc```

Target
-------

 * ```project_name``` - the destination project including the paths to it. Basically the rest of the clone url minus the ".git". E.g. ```jens.neuhalfen/task-ninja```.
 * ```method``` - direct or api

ÄPI mode:

 * ```url``` - e.g. ```https://www.exmple.com/gitlab/api/v3```
 * ```access_token``` - the access token of the user creating all the issues. Found on the account page,  e.g. ```secretsecretsecret```
 * ```ssl_verify``` - set to ```yes``` to verify SSL server certificates.

Direct mode:

 * ```overwrite````- if set to yes, the milestones and issues are cleared for this projects and issues are recreated with their trac id (useful to preserve trac links)
 * ```db-name``` - MySQL database name
 * ```db-user``` - MySQL user name
 * ```db-password``` - MySQL password
 * ```uploads``` - GitLab uploads directory
 * ```usernames``` Comma separed list of username mappings such as: ```trac1->git1, trac2->git2```

Wiki
----

 * ```migrate``` - Should the wiki pages be converted?
 * ```target-directory``` - Directory in which the wiki pages should be written

Issues
------

 * ```migrate``` - Should we migrate issues and milestones?

Licenses
========

LGLP license version 3.0 (see the [licences directory](licences)).

History
=======

 * The main program has been cloned from https://gitlab.dyomedea.com/vdv/trac-to-gitlab which itself has been cloned from https://github.com/neuhalje/hack-copy-track-issues-to-gitlab
 * Trac2down.py (the conversion of trac wiki markup to markdown) has been cloned from https://gist.github.com/sgk/1286682 and https://gist.github.com/tcchau/4628317

Requirements
==============

 * Python 3.2, xmlrpclib, requests
 * Trac with [XML-RPC plugin](http://trac-hacks.org/wiki/XmlRpcPlugin) enabled
 * Gitlab
 
 And also, if you use the direct access to GitLab's database:
 * [peewee](https://github.com/coleifer/peewee) 
 * [PyMySQl](https://github.com/PyMySQL/PyMySQL)
