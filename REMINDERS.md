# Gmail reminders and live admin

## Live admin

In your laptop's terminal, from the StudyFlow folder, run:

```powershell
.\.venv\Scripts\python.exe live_admin.py
```

Choose a new admin username and enter your email and password when prompted.
The password is hidden as you type. This creates the account in Neon, not SQLite.
Then visit `https://YOUR-SITE.onrender.com/admin/` and sign in.
Never commit `.env.local` or paste its contents into a public message.

## Enable reminders

1. Push these code changes and wait for Render to deploy successfully. Its build
   applies migration 0005 before the reminder job can run.
2. Turn on Google two-step verification and create an app password at
   https://myaccount.google.com/apppasswords (if available for your account).
3. In the GitHub repository open Settings > Secrets and variables > Actions.
   Add these **repository secrets**, not ordinary variables:
   - `DATABASE_URL`: the Neon connection value from `.env.local`.
   - `EMAIL_HOST_USER`: the Gmail address sending reminders.
   - `EMAIL_HOST_PASSWORD`: its Google app password, without spaces; not your
     normal Google password.
4. Open GitHub Actions > Assignment email reminders > Run workflow to test it.
   Create an incomplete assignment due in 30 minutes with "1 hour before" selected
   and a real email address on your StudyFlow account. Check inbox and spam.

The schedule checks every 15 minutes and sends only unsent reminders whose chosen
time has passed but whose assignment is not yet overdue. Times use Africa/Lagos
by default. Choose "No reminder" or mark an assignment complete to stop it.
Changing its due date/time or reminder selection enables a new reminder.

The worker runs on GitHub, so Render's sleeping service and blocked SMTP ports
do not prevent sending. Public repositories use free standard hosted runners;
private repositories have monthly allowances. GitHub can delay or drop scheduled
runs, and disables public-repository schedules after 60 days without activity.
This is a best-effort reminder, not an exact-time alarm. Gmail sending limits apply.
If a process stops after Gmail accepts an email but before the database records
success, a retry may send a duplicate.

References:
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://support.google.com/mail/answer/185833
- https://render.com/docs/free
