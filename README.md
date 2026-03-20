# My_Website

Flask website with an admin dashboard and SQLite storage.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

4. Open `http://127.0.0.1:5000`.

## Deploy and connect `ziadyakoot.me`

Your domain can point only to a public host, not your local machine. For this Flask app, a simple path is Render (or Railway/Fly.io with similar steps).

### 1) Put code on GitHub

Push this project to a GitHub repository.

### 2) Create a web service on Render

1. Create a new **Web Service** from your GitHub repo.
2. Runtime: `Python 3`.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
gunicorn app:app
```

5. Add environment variables:
	- `FLASK_SECRET_KEY` (required, strong random value)
	- `ADMIN_USERNAME` (optional)
	- `ADMIN_PASSWORD` (optional)

### 3) Add your custom domain in Render

1. In your Render service, open **Settings > Custom Domains**.
2. Add:
	- `ziadyakoot.me`
	- `www.ziadyakoot.me`
3. Render will show required DNS records.

### 4) Add DNS records at your domain provider

Use the exact values Render gives you. Typically:

- `www` as a `CNAME` to your Render hostname.
- Root (`@`) as one or more `A` records to Render IP(s), if requested.

If your provider supports ALIAS/ANAME for root, you can use that instead when instructed.

### 5) Wait for DNS propagation and verify

- DNS can take a few minutes up to 24 hours.
- Render will automatically provision HTTPS once records are correct.

## Important note about SQLite

Many cloud platforms have ephemeral filesystems. If using SQLite in production, use persistent disk storage (if your host supports it) or migrate to PostgreSQL/MySQL to avoid data loss after redeploys/restarts.