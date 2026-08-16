# Event Banner Generator

A small Flask app for generating event banners (16:9 PNGs with a title and
date range baked in) from a shared template. Logged-in accounts can also
publish their own background image, which replaces the default banner for
every banner they generate from then on.

Built with Flask + Pillow. No database- accounts and generation logs live
as flat JSON in the instance folder.

## Features

- Password-protected accounts (passwords hashed with Werkzeug's PBKDF2, never stored in plaintext)
- Live PNG preview as you type a title and pick a date range
- One-click download of the final banner
- **Custom banners**: any account can upload their own background image;
  it's cropped/scaled to the standard canvas and used in place of the
  shared default banner for that account until they reset it
- A generation log (`instance/logs.json`) recording who made what, when

## Project structure

```
event-banner-generator/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # Dev/Prod config classes
│   ├── auth.py            # login/logout/session blueprint
│   ├── banners.py         # preview/download/upload blueprint
│   ├── imaging.py         # Pillow rendering + date formatting
│   ├── pages.py           # index page + /assets static route
│   ├── storage.py         # thread-safe JSON read/write helpers
│   ├── utils.py           # login_required decorator, slugify
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── assets/                # font + default banner (you supply these, see below)
├── scripts/
│   └── create_account.py  # CLI for managing accounts
├── instance/               # gitignored: accounts.json, logs.json, uploads/, output/
├── wsgi.py                 # entrypoint (dev server / gunicorn / PythonAnywhere)
├── requirements.txt
├── .env.example
└── .gitignore
```

The `instance/` folder is Flask's conventional home for anything that's
deployment-specific and shouldn't be committed — accounts, logs, uploaded
banners, and generated output all live there and are created automatically
on first run.

## Setup

1. **Clone and enter the repo**

   ```bash
   git clone https://github.com/heykodex/event-banner-generator.git
   cd event-banner-generator
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Add the two binary assets** (not tracked in git — see `assets/README.md`):

   - `assets/DelaGothicOne-Regular.ttf`
   - `assets/default_banner.webp` — any 1920x1080 image works as the fallback background

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Generate a real secret key and put it in `.env`:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Create an account** (there's no public signup — accounts are provisioned via CLI)

   ```bash
   python scripts/create_account.py add kodexdev "a-strong-password"
   ```

   Other commands:

   ```bash
   python scripts/create_account.py list
   python scripts/create_account.py remove kodexdev
   ```

6. **Run it**

   ```bash
   flask --app wsgi run --debug
   ```

   or

   ```bash
   python wsgi.py
   ```

   Visit `http://127.0.0.1:5000`.

## Publishing a custom banner

Once logged in, the "Custom Banner" section at the bottom of the generator
lets you upload a PNG/JPG/WEBP. It's cropped and scaled to match the default
canvas (1920x1080) and stored at
`instance/uploads/banners/<your-username>.png`. Every preview and download
after that uses your banner instead of the shared default. "Reset to
default" deletes it and falls back to `assets/default_banner.webp`.

## Deployment

This app is a standard Flask app — `wsgi.py` exposes `app` for any WSGI
server.

**Gunicorn**

```bash
gunicorn wsgi:app
```

**PythonAnywhere**

Point the WSGI configuration file's `application` at
`from wsgi import app as application`, set the working directory to the repo
root, and make sure `SECRET_KEY` and `FLASK_ENV=production` are set in the
web app's environment variables (or in a `.env` file in the project root).
Don't forget to create the `instance/` folder (or let the app create it on
first request) and to add your `assets/` files on the server too.

Whatever host you use, set `FLASK_ENV=production` and a real `SECRET_KEY` —
the defaults in `config.py` are for local development only.

## License

MIT — see `LICENSE`.
