from django.db import migrations

# Every table in the public schema gets row level security without policies,
# so a hosted PostgreSQL that exposes the schema through an HTTP API (Supabase's
# Data API with the anon/authenticated roles) cannot read it. Django connects
# as the table owner and is unaffected. Django's own tables are included because
# auth_user holds password hashes and django_session holds session data.
TABLES = [
    'django_migrations',
    'django_content_type',
    'django_admin_log',
    'django_session',
    'auth_permission',
    'auth_group',
    'auth_group_permissions',
    'auth_user',
    'auth_user_groups',
    'auth_user_user_permissions',
    'catalog_service',
]


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;' for table in TABLES],
            reverse_sql=[f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;' for table in TABLES],
        ),
    ]
