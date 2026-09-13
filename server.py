"""Serve sqlite-web under gevent with a redirect-free /health endpoint.

Mirrors the upstream sqlite_wsgi entry-point (gevent WSGIServer over the
sqlite_web Flask app), plus two changes needed to run as a Railway service:

1. ``/health`` returns 200 without authentication. The stock auth handler
   redirects every unauthenticated path to ``/login/`` (and ``/login`` without
   the trailing slash redirects again), which Railway's HTTP healthcheck would
   fail on.
2. Databases are discovered by the entrypoint script and passed as arguments,
   so every ``.db`` file on the volume is browsable from one UI.
"""
import os
import sys

from gevent import monkey

monkey.patch_all()

from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from flask import flash, redirect, request, session, url_for

from sqlite_web.sqlite_web import app, configure_app

db_paths = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
data_dir = os.environ.get('DATA_DIR', '/data')

# Same argv contract as the sqlite_web console script (optparse reads sys.argv).
sys.argv = ['server.py', *db_paths,
            '-H', '0.0.0.0',
            '-p', os.environ.get('PORT', '8080'),
            '-P',                 # take the password from SQLITE_WEB_PASSWORD
            '-L',                 # allow uploading additional databases at runtime
            '-U', data_dir]       # uploads land on the volume

# configure_app() installs the stock auth handler; it must run before the
# handler list is rebuilt below.
kwargs = configure_app()


@app.route('/health')
def health():
    return 'ok'


# Rebuild the stock auth handler (installed by configure_app) with /health
# exempted; everything else keeps redirecting to /login/ when unauthorized.
originals = list(app.before_request_funcs.get(None, []))
app.before_request_funcs[None] = []
for handler in originals:
    if getattr(handler, '__name__', '') == 'check_password':

        @app.before_request
        def check_password():
            if session.get('authorized'):
                return None
            path = request.path
            public = (path in ('/login/', '/health')
                      or path.startswith(('/static/', '/favicon')))
            if public:
                return None
            flash('You must log-in to view the database browser.', 'danger')
            session['next_url'] = request.base_url
            return redirect(url_for('login'))
    else:
        app.before_request_funcs[None].append(handler)

server = WSGIServer((kwargs['host'], kwargs['port']), app, log=None,
                    spawn=Pool(50))
print('Serving on %s:%s' % (kwargs['host'], kwargs['port']), flush=True)
server.serve_forever()
