# LinkedIn Automation Tool

A personal tool that writes and schedules LinkedIn posts for you — powered by AI, so you can focus on building instead of posting.

---

## What It Does

- Generates LinkedIn posts using AI (via OpenRouter)
- Schedules them across any date range you define
- Publishes automatically — with retries if something goes wrong
- Optionally lets you review posts before they go live
- Helps you discover and connect with relevant professionals

---

## Before You Start

You'll need:
- Python 3.8+
- An [OpenRouter](https://openrouter.io) API key (free tier works)
- A LinkedIn Developer account with OAuth credentials

---

## Setup

```bash
# Clone and enter the project
git clone https://github.com/yourusername/linkedin-automation.git
cd linkedin-automation

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the root:

```env
FLASK_APP=app.py
SECRET_KEY=your-secret-key

OPENROUTER_API_KEY=your-key-here

LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/callback

DATABASE_URL=sqlite:///database/app.db
SCHEDULER_TIMEZONE=UTC
```

Then initialize the database and run:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python app.py
```

Open `http://localhost:5000` and you're in.

---

## How to Use It

1. **Connect LinkedIn** — go to Settings and complete OAuth
2. **Set your preferences** — topics, tone, posting days/times, and how many posts per day
3. **Generate posts** — the AI drafts them based on your config
4. **Review and schedule** — edit anything you want, then queue them up
5. **Watch it run** — the dashboard shows what's published, what's pending, and any errors

### Scheduling example

If you set Mon/Wed/Fri, 9 AM, 2 posts/day, 4-hour cooldown — posts go out at 9 AM and 1 PM on those days. Simple.

---

## Project Layout

```
linkedin-automation/
├── app.py              # Entry point
├── config.py
├── modules/            # Auth, scheduler, LinkedIn API, AI generator, etc.
├── templates/          # Frontend HTML
├── static/             # CSS, JS
├── prompts/            # AI prompt templates
├── database/           # SQLite
└── logs/               # app.log lives here
```

---

## Deploying

The easiest path is [Render](https://render.com):

- Connect your GitHub repo
- Add your environment variables in the dashboard
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Swap SQLite for PostgreSQL in production

---

## A Few Things to Keep in Mind

- Don't commit your `.env` — ever
- LinkedIn has rate limits; the app respects them, but don't push it
- Keep content genuine — automation works best when the posts actually sound like you
- Tokens expire; if publishing stops, re-authenticate

---

## Roadmap

- [x] Post generation + scheduling
- [x] LinkedIn OAuth
- [x] Dashboard + logs
- [ ] Connection discovery & automation
- [ ] Analytics
- [ ] Multi-platform (Twitter, Medium, Dev.to)

---

## Stack

Python · Flask · APScheduler · SQLAlchemy · OpenRouter · Playwright · Vanilla JS

---

Built by [@ashutosh3021](https://github.com/ashutosh3021) · MIT License