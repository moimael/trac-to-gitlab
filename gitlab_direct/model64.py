from peewee import *
from playhouse.proxy import Proxy

database_proxy = Proxy()

class UnknownFieldType(object):
    pass

class BaseModel(Model):
    class Meta(object):
        database = database_proxy

class Broadcast_Messages(BaseModel):
    alert_type = IntegerField(null=True)
    created_at = DateTimeField()
    ends_at = DateTimeField(null=True)
    message = TextField()
    starts_at = DateTimeField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'broadcast_messages'

class Deploy_Keys_Projects(BaseModel):
    created_at = DateTimeField()
    deploy_key = IntegerField(db_column='deploy_key_id')
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'deploy_keys_projects'

class Events(BaseModel):
    action = IntegerField(null=True)
    author = IntegerField(null=True, db_column='author_id')
    created_at = DateTimeField()
    data = TextField(null=True)
    project = IntegerField(null=True, db_column='project_id')
    target = IntegerField(null=True, db_column='target_id')
    target_type = CharField(null=True)
    title = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'events'

class Forked_Project_Links(BaseModel):
    created_at = DateTimeField()
    forked_from_project = IntegerField(db_column='forked_from_project_id')
    forked_to_project = IntegerField(db_column='forked_to_project_id')
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'forked_project_links'

class Issues(BaseModel):
    assignee = IntegerField(null=True, db_column='assignee_id')
    author = IntegerField(null=True, db_column='author_id')
    branch_name = CharField(null=True)
    created_at = DateTimeField()
    description = TextField(null=True)
    iid = IntegerField(null=True)
    milestone = IntegerField(null=True, db_column='milestone_id')
    position = IntegerField(null=True)
    project = IntegerField(null=True, db_column='project_id')
    state = CharField(null=True)
    title = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'issues'

class Keys(BaseModel):
    created_at = DateTimeField()
    fingerprint = CharField(null=True)
    key = TextField(null=True)
    title = CharField(null=True)
    type = CharField(null=True)
    updated_at = DateTimeField()
    user = IntegerField(null=True, db_column='user_id')

    class Meta(object):
        db_table = 'keys'

class Merge_Requests(BaseModel):
    assignee = IntegerField(null=True, db_column='assignee_id')
    author = IntegerField(null=True, db_column='author_id')
    created_at = DateTimeField()
    description = TextField(null=True)
    iid = IntegerField(null=True)
    merge_status = CharField(null=True)
    milestone = IntegerField(null=True, db_column='milestone_id')
    source_branch = CharField()
    source_project = IntegerField(db_column='source_project_id')
    st_commits = TextField(null=True)
    st_diffs = TextField(null=True)
    state = CharField(null=True)
    target_branch = CharField()
    target_project = IntegerField(db_column='target_project_id')
    title = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'merge_requests'

class Milestones(BaseModel):
    created_at = DateTimeField()
    description = TextField(null=True)
    due_date = DateField(null=True)
    iid = IntegerField(null=True)
    project = IntegerField(db_column='project_id')
    state = CharField(null=True)
    title = CharField()
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'milestones'

class Namespaces(BaseModel):
    created_at = DateTimeField()
    description = CharField()
    name = CharField()
    owner = IntegerField(null=True, db_column='owner_id')
    path = CharField()
    type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'namespaces'

class Notes(BaseModel):
    attachment = CharField(null=True)
    author = IntegerField(null=True, db_column='author_id')
    commit = CharField(null=True, db_column='commit_id')
    created_at = DateTimeField()
    line_code = CharField(null=True)
    note = TextField(null=True)
    noteable = IntegerField(null=True, db_column='noteable_id')
    noteable_type = CharField(null=True)
    project = IntegerField(null=True, db_column='project_id')
    st_diff = TextField(null=True)
    system = IntegerField()
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'notes'

class Projects(BaseModel):
    archived = IntegerField()
    created_at = DateTimeField()
    creator = IntegerField(null=True, db_column='creator_id')
    description = TextField(null=True)
    import_url = CharField(null=True)
    imported = IntegerField()
    issues_enabled = IntegerField()
    issues_tracker = CharField()
    issues_tracker = CharField(null=True, db_column='issues_tracker_id')
    last_activity_at = DateTimeField(null=True)
    merge_requests_enabled = IntegerField()
    name = CharField(null=True)
    namespace = ForeignKeyField(Namespaces, db_column='namespace_id')
    path = CharField(null=True)
    snippets_enabled = IntegerField()
    updated_at = DateTimeField()
    visibility_level = IntegerField()
    wall_enabled = IntegerField()
    wiki_enabled = IntegerField()

    class Meta(object):
        db_table = 'projects'

class Protected_Branches(BaseModel):
    created_at = DateTimeField()
    name = CharField()
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'protected_branches'

class Schema_Migrations(BaseModel):
    version = CharField()

    class Meta(object):
        db_table = 'schema_migrations'

class Services(BaseModel):
    active = IntegerField()
    created_at = DateTimeField()
    project = IntegerField(db_column='project_id')
    project_url = CharField(null=True)
    recipients = TextField(null=True)
    room = CharField(null=True)
    subdomain = CharField(null=True)
    title = CharField(null=True)
    token = CharField(null=True)
    type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'services'

class Snippets(BaseModel):
    author = IntegerField(db_column='author_id')
    content = TextField(null=True)
    created_at = DateTimeField()
    expires_at = DateTimeField(null=True)
    file_name = CharField(null=True)
    private = IntegerField()
    project = IntegerField(null=True, db_column='project_id')
    title = CharField(null=True)
    type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta(object):
        db_table = 'snippets'

class Taggings(BaseModel):
    context = CharField(null=True)
    created_at = DateTimeField(null=True)
    tag = IntegerField(null=True, db_column='tag_id')
    taggable = IntegerField(null=True, db_column='taggable_id')
    taggable_type = CharField(null=True)
    tagger = IntegerField(null=True, db_column='tagger_id')
    tagger_type = CharField(null=True)

    class Meta(object):
        db_table = 'taggings'

class Tags(BaseModel):
    name = CharField(null=True)

    class Meta(object):
        db_table = 'tags'

class Users(BaseModel):
    admin = IntegerField()
    authentication_token = CharField(null=True)
    avatar = CharField(null=True)
    bio = CharField(null=True)
    can_create_group = IntegerField()
    can_create_team = IntegerField()
    color_scheme = IntegerField(db_column='color_scheme_id')
    confirmation_sent_at = DateTimeField(null=True)
    confirmation_token = CharField(null=True)
    confirmed_at = DateTimeField(null=True)
    created_at = DateTimeField()
    created_by = IntegerField(null=True, db_column='created_by_id')
    current_sign_in_at = DateTimeField(null=True)
    current_sign_in_ip = CharField(null=True)
    email = CharField()
    encrypted_password = CharField()
    extern_uid = CharField(null=True)
    failed_attempts = IntegerField(null=True)
    hide_no_ssh_key = IntegerField(null=True)
    last_sign_in_at = DateTimeField(null=True)
    last_sign_in_ip = CharField(null=True)
    linkedin = CharField()
    locked_at = DateTimeField(null=True)
    name = CharField(null=True)
    notification_level = IntegerField()
    password_expires_at = DateTimeField(null=True)
    projects_limit = IntegerField(null=True)
    provider = CharField(null=True)
    remember_created_at = DateTimeField(null=True)
    reset_password_sent_at = DateTimeField(null=True)
    reset_password_token = CharField(null=True)
    sign_in_count = IntegerField(null=True)
    skype = CharField()
    state = CharField(null=True)
    theme = IntegerField(db_column='theme_id')
    twitter = CharField()
    unconfirmed_email = CharField(null=True)
    updated_at = DateTimeField()
    username = CharField(null=True)

    class Meta(object):
        db_table = 'users'

class Users_Groups(BaseModel):
    created_at = DateTimeField()
    group_access = IntegerField()
    group = IntegerField(db_column='group_id')
    notification_level = IntegerField()
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta(object):
        db_table = 'users_groups'

class Users_Projects(BaseModel):
    created_at = DateTimeField()
    notification_level = IntegerField()
    project_access = IntegerField()
    project = IntegerField(db_column='project_id')
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta(object):
        db_table = 'users_projects'

class Web_Hooks(BaseModel):
    created_at = DateTimeField()
    issues_events = IntegerField()
    merge_requests_events = IntegerField()
    project = IntegerField(null=True, db_column='project_id')
    push_events = IntegerField()
    service = IntegerField(null=True, db_column='service_id')
    type = CharField(null=True)
    updated_at = DateTimeField()
    url = CharField(null=True)

    class Meta(object):
        db_table = 'web_hooks'

