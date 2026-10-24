"""Verify the configured database and migrate without logging connection secrets."""
import contextlib
import io
import logging
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

def main():
    import environ
    # django-environ logs malformed lines verbatim. Suppress its logger before
    # parsing, and repair a pasted bare URI without ever printing the line.
    logging.getLogger('environ.environ').disabled = True
    env_path = ROOT / '.env'
    if env_path.exists():
        lines = env_path.read_text(encoding='utf-8').splitlines()
        repaired = ['DATABASE_URL=' + line.strip() if line.strip().startswith(('postgresql://', 'postgres://')) else line for line in lines]
        if repaired != lines:
            env_path.write_text('\n'.join(repaired) + '\n', encoding='utf-8')
            print('Corrected a bare database URI to a DATABASE_URL assignment; value hidden.')
    environ.Env.read_env(env_path)
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        print('BLOCKED: DATABASE_URL is missing from the environment or .env.')
        return 1
    # Encode literal reserved credential characters without printing or changing
    # their decoded values. Already encoded characters are normalized once.
    from urllib.parse import quote, unquote
    corrected = url
    if '://' in url and '@' in url:
        scheme, remainder = url.split('://', 1)
        credentials, server = remainder.rsplit('@', 1)
        if ':' in credentials:
            username, password = credentials.split(':', 1)
            decoded_password = unquote(password)
            corrected = scheme + '://' + quote(unquote(username), safe='') + ':' + quote(decoded_password, safe='') + '@' + server
    corrected = re.sub(r'@\[([A-Za-z0-9.-]+)\](?=[:/])', r'@\1', corrected)
    if corrected != url:
        path = ROOT / '.env'
        lines = path.read_text(encoding='utf-8').splitlines()
        lines = ['DATABASE_URL=' + corrected if line.startswith('DATABASE_URL=') else line for line in lines]
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        os.environ['DATABASE_URL'] = corrected
        print('Normalized URI encoding without exposing credentials.')
    try:
        from urllib.parse import urlsplit, unquote
        parts = urlsplit(corrected)
        if parts.scheme not in ('postgres', 'postgresql'):
            print('BLOCKED: DATABASE_URL must be a PostgreSQL connection URI.')
            return 1
        if not parts.password or any(token in unquote(parts.password).upper() for token in ['YOUR-PASSWORD', 'YOUR_PASSWORD', 'PLACEHOLDER']):
            print('BLOCKED: DATABASE_URL still needs a real database password in the ignored .env file.')
            return 1
    except Exception:
        print('BLOCKED: DATABASE_URL is not a valid URI. URL-encode reserved password characters.')
        return 1
    path = ROOT / '.env'
    lines = path.read_text(encoding='utf-8').splitlines()
    lines = [line for line in lines if not line.startswith('USE_SQLITE=')]
    lines.append('USE_SQLITE=False')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    os.environ['USE_SQLITE'] = 'False'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        import django
        django.setup()
        from django.db import connection
        connection.settings_dict.setdefault('OPTIONS', {})['connect_timeout'] = 10
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            assert cursor.fetchone()[0] == 1
        if not connection.connection.pgconn.ssl_in_use:
            print('FAILED: connection did not negotiate SSL; migrations were not run.')
            return 1
        print('PASS: psycopg connected to PostgreSQL over SSL; SELECT 1 succeeded.')
    except Exception as error:
        # Deliberately omit exception text: drivers can include DSNs and identities.
        diagnostic = str(error).lower()
        reason = 'connection could not be established'
        for marker, description in [
            ('password authentication failed', 'database rejected the password'),
            ('tenant or user not found', 'pooler rejected the project/user identity'),
            ('getaddrinfo', 'database hostname could not be resolved'),
            ('could not translate host name', 'database hostname could not be resolved'),
            ('timeout', 'connection timed out'),
            ('connection refused', 'database endpoint refused the connection'),
            ('certificate', 'TLS certificate validation failed'),
            ('forbidden by its access permissions', 'network access was blocked by the execution sandbox'),
        ]:
            if marker in diagnostic:
                reason = description
                break
        print(f'BLOCKED: {reason} ({type(error).__name__}); credentials and server details suppressed.')
        return 2
    try:
        from django.core.management import call_command
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            call_command('makemigrations', interactive=False, verbosity=0)
            call_command('migrate', interactive=False, verbosity=0)
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        remaining = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if remaining:
            print('FAILED: migrations remain pending; inspect privately.')
            return 3
        print('PASS: all Django migrations applied; no pending migrations.')
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            call_command('setup_roles', verbosity=0)
        print('PASS: Reader and Author roles initialized.')
    except Exception as error:
        print(f'FAILED: migration or role initialization failed ({type(error).__name__}); details suppressed.')
        return 3
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
