from peewee import *

database = PostgresqlDatabase('gitlabhq_production', **{'user': 'gitlab'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class BroadcastMessages(BaseModel):
    alert_type = IntegerField(null=True)
    color = CharField(max_length=255, null=True)
    created_at = DateTimeField(null=True)
    ends_at = DateTimeField(null=True)
    font = CharField(max_length=255, null=True)
    message = TextField()
    starts_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'broadcast_messages'

class DeployKeysProjects(BaseModel):
    created_at = DateTimeField(null=True)
    deploy_key = IntegerField(db_column='deploy_key_id')
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'deploy_keys_projects'

class Emails(BaseModel):
    created_at = DateTimeField(null=True)
    email = CharField(max_length=255)
    updated_at = DateTimeField(null=True)
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'emails'

class Events(BaseModel):
    action = IntegerField(null=True)
    author = IntegerField(db_column='author_id', null=True)
    created_at = DateTimeField(null=True)
    data = TextField(null=True)
    project = IntegerField(db_column='project_id', null=True)
    target = IntegerField(db_column='target_id', null=True)
    target_type = CharField(max_length=255, null=True)
    title = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'events'

class ForkedProjectLinks(BaseModel):
    created_at = DateTimeField(null=True)
    forked_from_project = IntegerField(db_column='forked_from_project_id')
    forked_to_project = IntegerField(db_column='forked_to_project_id')
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'forked_project_links'

class Issues(BaseModel):
    assignee = IntegerField(db_column='assignee_id', null=True)
    author = IntegerField(db_column='author_id', null=True)
    branch_name = CharField(max_length=255, null=True)
    created_at = DateTimeField(null=True)
    description = TextField(null=True)
    iid = IntegerField(null=True)
    milestone = IntegerField(db_column='milestone_id', null=True)
    position = IntegerField(null=True)
    project = IntegerField(db_column='project_id', null=True)
    state = CharField(max_length=255, null=True)
    title = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'issues'

class Keys(BaseModel):
    created_at = DateTimeField(null=True)
    fingerprint = CharField(max_length=255, null=True)
    key = TextField(null=True)
    title = CharField(max_length=255, null=True)
    type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)
    user = IntegerField(db_column='user_id', null=True)

    class Meta:
        db_table = 'keys'

class LabelLinks(BaseModel):
    created_at = DateTimeField(null=True)
    label = IntegerField(db_column='label_id', null=True)
    target = IntegerField(db_column='target_id', null=True)
    target_type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'label_links'

class Labels(BaseModel):
    color = CharField(max_length=255, null=True)
    created_at = DateTimeField(null=True)
    project = IntegerField(db_column='project_id', null=True)
    title = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'labels'

class MergeRequestDiffs(BaseModel):
    created_at = DateTimeField(null=True)
    merge_request = IntegerField(db_column='merge_request_id')
    st_commits = TextField(null=True)
    st_diffs = TextField(null=True)
    state = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'merge_request_diffs'

class MergeRequests(BaseModel):
    assignee = IntegerField(db_column='assignee_id', null=True)
    author = IntegerField(db_column='author_id', null=True)
    created_at = DateTimeField(null=True)
    description = TextField(null=True)
    iid = IntegerField(null=True)
    merge_status = CharField(max_length=255, null=True)
    milestone = IntegerField(db_column='milestone_id', null=True)
    position = IntegerField(null=True)
    source_branch = CharField(max_length=255)
    source_project = IntegerField(db_column='source_project_id')
    state = CharField(max_length=255, null=True)
    target_branch = CharField(max_length=255)
    target_project = IntegerField(db_column='target_project_id')
    title = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'merge_requests'

class Milestones(BaseModel):
    created_at = DateTimeField(null=True)
    description = TextField(null=True)
    due_date = DateField(null=True)
    iid = IntegerField(null=True)
    project = IntegerField(db_column='project_id')
    state = CharField(max_length=255, null=True)
    title = CharField(max_length=255)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'milestones'

class Namespaces(BaseModel):
    avatar = CharField(max_length=255, null=True)
    created_at = DateTimeField(null=True)
    description = CharField(max_length=255)
    name = CharField(max_length=255)
    owner = IntegerField(db_column='owner_id', null=True)
    path = CharField(max_length=255)
    type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'namespaces'

class Notes(BaseModel):
    attachment = CharField(max_length=255, null=True)
    author = IntegerField(db_column='author_id', null=True)
    commit = CharField(db_column='commit_id', max_length=255, null=True)
    created_at = DateTimeField(null=True)
    line_code = CharField(max_length=255, null=True)
    note = TextField(null=True)
    noteable = IntegerField(db_column='noteable_id', null=True)
    noteable_type = CharField(max_length=255, null=True)
    project = IntegerField(db_column='project_id', null=True)
    st_diff = TextField(null=True)
    system = BooleanField()
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'notes'

class Projects(BaseModel):
    archived = BooleanField()
    created_at = DateTimeField(null=True)
    creator = IntegerField(db_column='creator_id', null=True)
    description = TextField(null=True)
    import_status = CharField(max_length=255, null=True)
    import_url = CharField(max_length=255, null=True)
    issues_enabled = BooleanField()
    issues_tracker = CharField(max_length=255)
    issues_tracker = CharField(db_column='issues_tracker_id', max_length=255, null=True)
    last_activity_at = DateTimeField(null=True)
    merge_requests_enabled = BooleanField()
    name = CharField(max_length=255, null=True)
    namespace = IntegerField(db_column='namespace_id', null=True)
    path = CharField(max_length=255, null=True)
    repository_size = FloatField(null=True)
    snippets_enabled = BooleanField()
    star_count = IntegerField()
    updated_at = DateTimeField(null=True)
    visibility_level = IntegerField()
    wall_enabled = BooleanField()
    wiki_enabled = BooleanField()

    class Meta:
        db_table = 'projects'

class ProtectedBranches(BaseModel):
    created_at = DateTimeField(null=True)
    name = CharField(max_length=255)
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'protected_branches'

class SchemaMigrations(BaseModel):
    version = CharField(max_length=255)

    class Meta:
        db_table = 'schema_migrations'

class Services(BaseModel):
    active = BooleanField()
    created_at = DateTimeField(null=True)
    project = IntegerField(db_column='project_id')
    properties = TextField(null=True)
    title = CharField(max_length=255, null=True)
    type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'services'

class Snippets(BaseModel):
    author = IntegerField(db_column='author_id')
    content = TextField(null=True)
    created_at = DateTimeField(null=True)
    expires_at = DateTimeField(null=True)
    file_name = CharField(max_length=255, null=True)
    private = BooleanField()
    project = IntegerField(db_column='project_id', null=True)
    title = CharField(max_length=255, null=True)
    type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'snippets'

class Taggings(BaseModel):
    context = CharField(max_length=255, null=True)
    created_at = DateTimeField(null=True)
    tag = IntegerField(db_column='tag_id', null=True)
    taggable = IntegerField(db_column='taggable_id', null=True)
    taggable_type = CharField(max_length=255, null=True)
    tagger = IntegerField(db_column='tagger_id', null=True)
    tagger_type = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'taggings'

class Tags(BaseModel):
    name = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'tags'

class Users(BaseModel):
    admin = BooleanField()
    authentication_token = CharField(max_length=255, null=True)
    avatar = CharField(max_length=255, null=True)
    bio = CharField(max_length=255, null=True)
    can_create_group = BooleanField()
    can_create_team = BooleanField()
    color_scheme = IntegerField(db_column='color_scheme_id')
    confirmation_sent_at = DateTimeField(null=True)
    confirmation_token = CharField(max_length=255, null=True)
    confirmed_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    created_by = IntegerField(db_column='created_by_id', null=True)
    current_sign_in_at = DateTimeField(null=True)
    current_sign_in_ip = CharField(max_length=255, null=True)
    email = CharField(max_length=255)
    encrypted_password = CharField(max_length=255)
    extern_uid = CharField(max_length=255, null=True)
    failed_attempts = IntegerField(null=True)
    hide_no_ssh_key = BooleanField(null=True)
    last_credential_check_at = DateTimeField(null=True)
    last_sign_in_at = DateTimeField(null=True)
    last_sign_in_ip = CharField(max_length=255, null=True)
    linkedin = CharField(max_length=255)
    locked_at = DateTimeField(null=True)
    name = CharField(max_length=255, null=True)
    notification_level = IntegerField()
    password_expires_at = DateTimeField(null=True)
    projects_limit = IntegerField(null=True)
    provider = CharField(max_length=255, null=True)
    remember_created_at = DateTimeField(null=True)
    reset_password_sent_at = DateTimeField(null=True)
    reset_password_token = CharField(max_length=255, null=True)
    sign_in_count = IntegerField(null=True)
    skype = CharField(max_length=255)
    state = CharField(max_length=255, null=True)
    theme = IntegerField(db_column='theme_id')
    twitter = CharField(max_length=255)
    unconfirmed_email = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)
    username = CharField(max_length=255, null=True)
    website_url = CharField(max_length=255)

    class Meta:
        db_table = 'users'

class UsersGroups(BaseModel):
    created_at = DateTimeField(null=True)
    group_access = IntegerField()
    group = IntegerField(db_column='group_id')
    notification_level = IntegerField()
    updated_at = DateTimeField(null=True)
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'users_groups'

class UsersProjects(BaseModel):
    created_at = DateTimeField(null=True)
    notification_level = IntegerField()
    project_access = IntegerField()
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField(null=True)
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'users_projects'

class UsersStarProjects(BaseModel):
    created_at = DateTimeField(null=True)
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField(null=True)
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'users_star_projects'

class WebHooks(BaseModel):
    created_at = DateTimeField(null=True)
    issues_events = BooleanField()
    merge_requests_events = BooleanField()
    project = IntegerField(db_column='project_id', null=True)
    push_events = BooleanField()
    service = IntegerField(db_column='service_id', null=True)
    tag_push_events = BooleanField(null=True)
    type = CharField(max_length=255, null=True)
    updated_at = DateTimeField(null=True)
    url = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'web_hooks'

