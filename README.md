What
=====

 This script migrates issues from trac to gitlab.

Features
--------
 * Component & Issue-Type are converted to labels
 * Milestones are ignored (or: I did not get the script to set my one single milestone, so I set it manually)
 * Comments to issues are copied over
 * Wiki Syntax in comments/descriptions is sanitized for my basic usage

How
====

 Usage: copy ```migrate.cfg.example``` to ```migrate.cfg```, configure the values and run it (```python migrate.py```). Make sure you test it on a test project prior, if you run it twice against the same project you will get duplicated issues.

Source
-------

 * ```url``` - xmlrpc url to trac, e.g. ``https://user:secret@www.example.com/projects/thisismyproject/login/xmlrpc```

Target
-------

 * ```url``` - e.g. ```https://www.exmple.com/gitlab/api/v3```
 * ```access_token``` - the access token of the user creating all the issues. Found on the account page,  e.g. ```secretsecretsecret```
 * ```project_name``` - the destination project including the paths to it. Basically the rest of the clone url minus the ".git". E.g. ```jens.neuhalfen/task-ninja```.
 * ```ssl_verify``` - set to ```yes``` to verify SSL server certificates.

Additional configuration in ```migrate.py```
--------------------------------------------

 * ```milestone_map``` - Maps milestones from trac to gitlab. Milestones have to exist in gitlab prior to running the script (_CAVE_: Assigning milestones does not work.)

License
========

 Cloned from https://github.com/neuhalje/hack-copy-track-issues-to-gitlab
 License: http://www.wtfpl.net/

Requirements
==============

 * ```Python 2.7, xmlrpclib, requests```
 * Trac with [XML-RPC plugin](http://trac-hacks.org/wiki/XmlRpcPlugin) enabled
 * Gitlab
