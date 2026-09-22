# Deploy StudyFlow on Render

1. Upload this project to a GitHub repository. Include `app`, `studyflow`,
   `manage.py`, `requirements.txt`, `build.sh`, and `.python-version`.
   Do not upload `.venv`, `.env`, or `db.sqlite3`.
2. In Render, create a PostgreSQL database. Choose a plan after reviewing its
   price and retention limits. Copy its Internal Database URL into Render's
   environment settings in step 4, not into a source file.
3. Create a Web Service, connect the GitHub repository, and choose Python 3.
   Use the same region as the database and leave Root Directory blank if
   `manage.py` is at the repository root.
4. Configure:

   | Setting | Value |
   | --- | --- |
   | Build Command | `bash build.sh` |
   | Start Command | `gunicorn studyflow.wsgi:application --bind 0.0.0.0:$PORT` |
   | `SECRET_KEY` environment variable | Generate a new random secret in Render |
   | `DATABASE_URL` environment variable | Your database's Internal Database URL |

   Render supplies `RENDER` and `RENDER_EXTERNAL_HOSTNAME` automatically.
5. Review the selected service plan and deploy. Open the `.onrender.com` URL
   when the deployment finishes.
6. Verify signup, logout, login, assignment creation, and that a second account
   cannot see the first account's assignments. Check the navbar styling too.

The deployed database starts empty. Existing local accounts and assignments
stay in your local SQLite database; they are not automatically transferred.
The build applies migrations and collects CSS on every deployment.
Local development still uses SQLite and `python manage.py runserver`.

Official guide: https://render.com/docs/deploy-django
