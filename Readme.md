## Features

### 🚀 Core Features

- **Intelligent Post Generation** - AI-powered LinkedIn post creation using OpenRouter API
- **Smart Scheduling** - Schedule posts across custom date ranges with flexible timing options
- **Automated Publishing** - APScheduler-based publishing with built-in retry logic
- **Local Storage** - All configurations, posts, and logs stored locally for reliability
- **User Review** - Optional approval workflow before posts go live
- **Professional Dashboard** - Real-time monitoring of posting activity and metrics
- **Connection Discovery** - Find professionals matching your networking criteria
- **Optional Automation** - Browser-based connection request automation (Playwright)

### ⚙️ Customization Options

- **Writing Style** - Customize tone, audience, and messaging
- **Posting Schedule** - Control frequency, time of day, and days of the week
- **Content Strategy** - Define topics, projects, domains, and hashtag preferences
- **Hashtag Generation** - Auto-generate or manually curate hashtags
- **Character Limits** - Respect LinkedIn's content constraints automatically

---

## Technology Stack

| Layer | Technologies |
|-------|---------------|
| **Backend** | Python 3.8+, Flask |
| **Automation** | APScheduler, Playwright |
| **Database** | SQLite, SQLAlchemy ORM |
| **AI/LLM** | OpenRouter API |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Deployment** | Render (recommended) |
| **Version Control** | Git, GitHub |

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed on your system
- **Git** for version control
- **OpenRouter API Key** (free or paid account at [openrouter.io](https://openrouter.io))
- **LinkedIn Account** with access to LinkedIn's Developer Console
- **LinkedIn OAuth Credentials** (Client ID and Secret from LinkedIn Developer Portal)

### Optional

- **Render Account** (for deployment)
- **GitHub Account** (for version control and deployment)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/linkedin-automation.git
cd linkedin-automation
```

### 2. Create a Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# LLM Configuration
OPENROUTER_API_KEY=your-openrouter-api-key

# LinkedIn OAuth (obtain from LinkedIn Developer Console)
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/callback

# Database
DATABASE_URL=sqlite:///database/app.db

# Scheduler
SCHEDULER_TIMEZONE=UTC
```

### 5. Initialize the Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

---

## Quick Start

### 1. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

### 2. Authenticate

- Click **Settings** → **Connect LinkedIn**
- Complete OAuth authentication with your LinkedIn account
- Enter your OpenRouter API key

### 3. Configure Posting Preferences

Go to **Posting Configuration** and set up:

```
Topics: Write the topics you want to post about
Tone: Define your writing style (professional, casual, humorous, etc.)
Posting Schedule: Set start/end dates and times
Posts Per Day: Choose 1-3 posts daily
Enable Review: Optionally require approval before publishing
```

### 4. Generate Posts

1. Click **Generate** to create posts based on your configuration
2. Review generated posts in the **Generated Posts** tab
3. Edit any posts if needed
4. Click **Schedule** to add them to the publishing queue

### 5. Monitor Publishing

- Check the **Dashboard** for real-time metrics
- View **Scheduled Posts** to see upcoming publications
- Monitor **Publishing Logs** for success/failure details

### 6. Connection Discovery (Optional)

1. Go to **Connection Configuration**
2. Set filters (company, role, location, etc.)
3. Click **Search** to find matching profiles
4. Review results and optionally send connection requests
5. Track results in the **Logs** section

---

## Configuration Guide

### Posting Configuration

| Setting | Example | Purpose |
|---------|---------|---------|
| **API Key** | `sk-or-xxx...` | OpenRouter API key for LLM access |
| **Domains** | `SaaS, DevOps, Cloud` | Industries to focus on |
| **Topics** | `AI trends, productivity hacks` | Content themes |
| **Projects** | `MyStartup, OpenSource` | Projects to mention |
| **Target Audience** | `Engineers, Founders` | Who to target |
| **Tone** | `Thoughtful, Educational` | Writing personality |
| **Posting Days** | `Mon, Wed, Fri` | Days to post |
| **Posting Time** | `09:00 AM` | Time of day |
| **Posts Per Day** | `2` | Daily frequency |
| **Cooldown** | `4 hours` | Gap between posts |
| **Max Length** | `3000` | Character limit |

### Connection Configuration

| Setting | Example | Purpose |
|---------|---------|---------|
| **Company** | `Google, Microsoft` | Target companies |
| **Role** | `Software Engineer, Product Manager` | Job titles |
| **Location** | `San Francisco, New York` | Geographic targeting |
| **Experience** | `3-7 years` | Experience level |
| **University** | `Stanford` | Educational background |
| **Keywords** | `ML, Cloud, DevOps` | Custom search terms |
| **Daily Limit** | `10` | Max requests per day |

---

## Project Structure

```
linkedin-automation/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── .env                        # Environment variables (not in git)
├── README.md                   # This file
│
├── /static/                    # Frontend assets
│   ├── /css/
│   ├── /js/
│   └── /images/
│
├── /templates/                 # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── posting.html
│   └── logs.html
│
├── /modules/                   # Core modules
│   ├── auth.py                 # Authentication logic
│   ├── generator.py            # LLM post generation
│   ├── scheduler.py            # Scheduling engine
│   ├── linkedin.py             # LinkedIn API integration
│   ├── connections.py          # Connection discovery
│   ├── storage.py              # Database operations
│   └── utils.py                # Utility functions
│
├── /prompts/                   # LLM prompt templates
│   └── linkedin_prompt.txt
│
├── /database/                  # SQLite database
│   └── app.db
│
└── /logs/                      # Application logs
    └── app.log
```

---

## REST API Endpoints

### Authentication
```
POST   /auth/linkedin          - Initiate LinkedIn OAuth
GET    /auth/callback          - OAuth callback endpoint
POST   /auth/logout            - Logout current user
```

### Configuration
```
POST   /api/config/posting     - Save posting preferences
POST   /api/config/connections - Save connection preferences
GET    /api/config/posting     - Retrieve posting config
GET    /api/config/connections - Retrieve connection config
```

### Post Management
```
POST   /api/posts/generate     - Generate new posts
GET    /api/posts              - List all posts
POST   /api/posts/{id}/edit    - Edit a post
DELETE /api/posts/{id}         - Delete a post
POST   /api/posts/{id}/schedule - Schedule a post
POST   /api/posts/{id}/publish  - Manually publish a post
```

### Dashboard & Monitoring
```
GET    /                       - Home page
GET    /dashboard              - Main dashboard
GET    /api/stats              - Dashboard metrics
GET    /api/logs               - Publishing logs
GET    /api/logs/export        - Export logs as CSV
```

### Connections
```
POST   /api/connections/search - Search for profiles
POST   /api/connections/send   - Send connection requests
GET    /api/connections/history - View connection history
```

---

## Development

### Running in Development Mode

```bash
# Set environment to development
export FLASK_ENV=development

# Run with debug mode
python app.py
```

The application will auto-reload on file changes.

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

This project follows **PEP 8** guidelines. Run linting before committing:

```bash
flake8 .
black . --line-length=100
```

### Database Migrations

If you modify database models, create a migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

---

## Deployment

### Deploy to Render

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service** on Render
3. **Configure environment variables** in Render dashboard:
   - `FLASK_ENV=production`
   - `SECRET_KEY` (generate a secure key)
   - `OPENROUTER_API_KEY`
   - `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`
   - `DATABASE_URL` (use PostgreSQL in production)

4. **Set build command:**
   ```
   pip install -r requirements.txt
   ```

5. **Set start command:**
   ```
   gunicorn app:app
   ```

6. **Deploy** - Render will automatically deploy on git push

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set secure `SECRET_KEY`
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring and error tracking
- [ ] Configure backups for database
- [ ] Test OAuth redirect URI with production URL

---

## Scheduling Guide

### How Posts Are Published

1. **Generate Phase**: Posts created immediately when you click "Generate"
2. **Schedule Phase**: Posts assigned scheduled_datetime based on your preferences
3. **Publishing Phase**: APScheduler checks every minute for posts to publish
4. **Retry Phase**: Failed posts retry at 15 mins, 1 hour, and 6 hours

### Example Schedule

If you configure:
- **Start Date**: June 29, 2026
- **End Date**: July 31, 2026
- **Days**: Monday, Wednesday, Friday
- **Time**: 9:00 AM
- **Posts Per Day**: 2
- **Cooldown**: 4 hours

The system will generate posts for every Monday, Wednesday, Friday between those dates at 9:00 AM and 1:00 PM (9 AM + 4 hour cooldown).

---

## Troubleshooting

### Issue: "Connection refused" error

**Solution**: Ensure Flask app is running and accessible at `http://localhost:5000`

```bash
python app.py
```

### Issue: LinkedIn OAuth fails

**Ensure**:
- LinkedIn Client ID and Secret are correct
- Redirect URI matches exactly in both code and LinkedIn Developer Console
- Your LinkedIn account has Developer access

### Issue: Posts not generating

**Check**:
- OpenRouter API key is valid
- Configuration form is complete
- Check `/logs/app.log` for specific errors
- Ensure you have API credits available

### Issue: Scheduler not publishing posts

**Verify**:
- Flask app is running continuously
- Database file has write permissions
- Check logs for retry attempts: `/logs/app.log`
- Ensure LinkedIn OAuth token hasn't expired

### Viewing Logs

```bash
# Real-time log monitoring
tail -f logs/app.log

# View last 50 lines
tail -50 logs/app.log
```

---

## Security Considerations

### API Keys & Credentials

- **Never** commit `.env` file to git
- Store keys in environment variables only
- Rotate API keys regularly
- Use strong `SECRET_KEY` in production

### Data Protection

- Encrypt sensitive data in database
- Implement CSRF protection on all forms
- Validate all user inputs
- Use HTTPS in production
- Implement session timeouts

### LinkedIn API

- Respect rate limiting (LinkedIn enforces strict limits)
- Don't spam connection requests
- Follow LinkedIn's Terms of Service
- Test thoroughly before automation

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Write clean, documented code
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation accordingly
- Test thoroughly before submitting PR

---

## Roadmap

### Current Version (Phase 5)
- ✅ Flask foundation
- ✅ LLM integration
- ✅ Scheduling engine
- ✅ Dashboard
- ✅ LinkedIn OAuth

### Phase 6 (In Progress)
- 🔄 Connection discovery
- 🔄 Profile filtering
- 🔄 Browser automation

### Future Enhancements
- 📋 Analytics dashboard
- 📋 Multi-platform support (Twitter, Medium, Dev.to)
- 📋 Post variations and rewriting
- 📋 Optimal posting time prediction
- 📋 Encrypted API key storage
- 📋 Bulk operations

---

## FAQ

**Q: Can I use this for other platforms?**  
A: Currently LinkedIn-focused, but multi-platform support is planned for Phase 8.

**Q: How many posts can I generate at once?**  
A: Unlimited, but we recommend starting with 10-20 to review quality.

**Q: Will LinkedIn ban my account?**  
A: If you follow best practices (no spam, natural cadence, real content) you should be fine. Always comply with LinkedIn's Terms of Service.

**Q: Can I edit posts after scheduling?**  
A: Yes! Edit posts in the "Scheduled Posts" tab until they're published.

**Q: Is there a rate limit?**  
A: LinkedIn enforces strict API rate limits. The app respects these automatically.

**Q: Can I run this 24/7?**  
A: Yes, deploy to Render or another hosting service for continuous operation.

---

## License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## Support

### Getting Help

- **Documentation**: Check the docs/ folder
- **Issues**: Open a GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: contact@example.com (update with actual contact)

### Reporting Bugs

When reporting bugs, please include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Logs from `/logs/app.log`
- Your environment (OS, Python version, etc.)

---

## Acknowledgments

- [OpenRouter](https://openrouter.io) for LLM API
- [LinkedIn Official API](https://developer.linkedin.com)
- [APScheduler](https://apscheduler.readthedocs.io) for scheduling
- [Flask](https://flask.palletsprojects.com) for web framework
- [SQLAlchemy](https://www.sqlalchemy.org) for ORM

---

## Author

**Your Name**  
GitHub: [@ashutosh3021](https://github.com/ashutosh3021)  
---

**Last Updated**: June 29, 2026  
**Current Version**: 1.0.0  
**Status**: Active Development

---

### Quick Links

- 📚 [Full Documentation](docs/)
- 🐛 [Report a Bug](https://github.com/yourusername/linkedin-automation/issues)
- 💡 [Feature Request](https://github.com/yourusername/linkedin-automation/discussions)
- 🚀 [Deployment Guide](docs/