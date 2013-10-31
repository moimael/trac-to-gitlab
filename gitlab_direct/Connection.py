# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8

from peewee import MySQLDatabase
from .model62 import *


class Connection(object):
    """
    Connection to the gitlab database
    """

    def __init__(self, db_name, db_user, db_password):
        """

        :param url: "https://www.neuhalfen.name/gitlab/api/v3"
        :param access_token: "secretsecretsecret"
        """
        db = MySQLDatabase(db_name, **{'passwd': db_password, 'user': db_user})
        database_proxy.initialize(db)


    def milestone_by_name(self, project_id, milestone_name):
        for milestone in Milestones.select().where((Milestones.title == milestone_name) & (Milestones.project == project_id)):
            return milestone._data
        return None

    def project_by_name(self, project_name):
        (namespace, name) = project_name.split('/')
        print(name)
        for project in Projects.select().join(Namespaces).where((Projects.name == name) & (Namespaces.name == namespace)):
            print (project._data)
            return project._data
        return None

    def get(self, url_postfix, **keywords):
        return self._get(url_postfix, keywords)

    def _get(self, url_postfix, keywords):
        """
        :param url_postfix: e.g. "/projects/:id/issues"
        :param keywords:  map, e.g. { "id" : 5 }
        :return: json of GET
        """
        completed_url = self._complete_url(url_postfix, keywords)
        r = requests.get(completed_url, verify=self.verify)
        json = r.json()
        return json

    def put(self, url_postfix, data, **keywords):
        completed_url = self._complete_url(url_postfix, keywords)
        r = requests.put(completed_url,data= data, verify=self.verify)
        j = r.json()
        return j

    def put_json(self, url_postfix, data, **keywords):
        completed_url = self._complete_url(url_postfix, keywords)
        payload = json.dumps(data)
        r = requests.put(completed_url, data= payload, verify=self.verify)
        j = r.json()
        return j

    def post_json(self, url_postfix, data, **keywords):
        completed_url = self._complete_url(url_postfix, keywords)
        payload = json.dumps(data)
        r = requests.post(completed_url, data=data, verify=self.verify)
        j = r.json()
        return j

    def create_issue(self, dest_project_id, new_ticket):
        return self.post_json("/projects/:id/issues", new_ticket, id=dest_project_id)

    def comment_issue(self,project_id,ticket_id, body):
        new_note_data = {
            "id" : project_id,
            "issue_id" :ticket_id,
            "body" : body
        }
        self.post_json( "/projects/:project_id/issues/:issue_id/notes", new_note_data, project_id=project_id, issue_id=ticket_id)


    def set_issue_milestone(self,project_id,ticket_id,milestone_id):
        new_note_data = {"milestone" : milestone_id}
        self.put("/projects/:project_id/issues/:issue_id", new_note_data, project_id=project_id, issue_id=ticket_id)

    def close_issue(self,project_id,ticket_id):
        #new_note_data = "closed=1"
        new_note_data = {"closed": "1"}
        self.put("/projects/:project_id/issues/:issue_id", new_note_data, project_id=project_id, issue_id=ticket_id)

    def _complete_url(self, url_postfix, keywords):
        url_postfix_with_params = self._url_postfix_with_params(url_postfix, keywords)
        complete_url = "%s%s?private_token=%s" % (self.url, url_postfix_with_params, self.access_token)
        return complete_url

    def _url_postfix_with_params(self, url_postfix, keywords):
        """

        :param url_postfix:  "/projects/:id/issues"
        :param keywords:  map, e.g. { "id" : 5 }
        :return:  "/projects/5/issues"
        """

        result = url_postfix
        for key, value in keywords.items():
            k = ":" + str(key)
            v = str(value)
            result = result.replace(k, v)
        return result
