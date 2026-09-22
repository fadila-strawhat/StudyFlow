"""Run locally to create an admin in the live database, with a private password prompt."""
import os
from pathlib import Path

if __name__ == '__main__':
    values = {}
    for line in Path('.env.local').read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    url = values.get('DATABASE_URL_UNPOOLED') or values.get('DATABASE_URL')
    if not url:
        raise SystemExit('No live database connection found in .env.local.')
    os.environ['DATABASE_URL'] = url
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyflow.settings')
    import django
    django.setup()
    from django.core.management import call_command
    print('Creating an admin in the LIVE database. Use a new admin username.')
    call_command('createsuperuser')
