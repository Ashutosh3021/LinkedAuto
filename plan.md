## Project Overview

### Purpose

The application focuses on **automation and reliability** rather than UI aesthetics, providing users with:
- Automated high-quality LinkedIn post generation using an LLM
- Intelligent scheduling and publishing workflows
- Professional networking discovery and connection automation
- Local storage for configuration, posts, and logs

---

## Goals

### Primary Goal

**Automatically generate high-quality, human-like LinkedIn posts** using an LLM and publish them on scheduled dates and times.

### Secondary Goal

**Assist in networking** by discovering and optionally automating LinkedIn connection requests based on user-defined filters.

---

## Technology Stack

| Component | Technologies |
|-----------|---------------|
| **Backend** | Python, Flask, APScheduler, SQLite, SQLAlchemy, Requests |
| **Browser Automation** | Playwright |
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **LLM Integration** | OpenRouter API |
| **Deployment** | Render |
| **Version Control** | Git, GitHub |

---

## High-Level Architecture

```
User
  ↓
Frontend (HTML/CSS/JS)
  ↓
Flask Backend
  ↓
Configuration Manager
  ↓
LLM Module
  ↓
Database (SQLite)
  ↓
Scheduler (APScheduler)
  ↓
LinkedIn Publisher
  ↓
LinkedIn API
```

---

## Core Modules

### 1. Authentication Module

Handles secure credential management and OAuth workflows.

**Responsibilities:**
- Store and manage OpenRouter API Key
- Store and manage LinkedIn OAuth Credentials
- Handle OAuth Authentication flow
- Refresh access tokens
- Securely save credentials to database

### 2. Configuration Wizard

Collects all user preferences through an interactive web interface.

#### Posting Configuration

| Setting | Purpose |
|---------|---------|
| API Key | OpenRouter API key for LLM access |
| Domains | Industries or domains to focus on |
| Topics | Content topics for post generation |
| Projects | Associated projects to mention |
| Target Audience | Who the posts are aimed at |
| Writing Tone | Personality and style of posts |
| Posting Start Date | When to begin publishing |
| Posting End Date | When to stop publishing |
| Posting Days | Days of the week to post |
| Posting Time | Time of day for posts |
| Posts Per Day | Number of posts daily |
| Cooldown Between Posts | Minimum gap between posts |
| Enable Auto Hashtags | Auto-generate relevant hashtags |
| Enable CTA | Include call-to-action in posts |
| Maximum Character Length | LinkedIn character limit compliance |
| Review Before Publishing | Require manual approval before posting |

#### Connection Configuration

| Setting | Purpose |
|---------|---------|
| Company | Target companies for connections |
| Role | Job titles to search for |
| Years of Experience | Experience level filter |
| Location | Geographic targeting |
| University | Educational background filter |
| Alumni Only | Restrict to alma mater graduates |
| Industry | Industry classification |
| Keywords | Custom search keywords |
| Maximum Profiles | Limit profiles to review |
| Connection Message | Custom message for requests |
| Daily Connection Limit | Max requests per day |
| Cooldown Between Requests | Gap between connection requests |

### 3. LLM Module

Generates human-like LinkedIn posts based on configuration and context.

### 4. Scheduler Module

Manages post timing and automatic publishing.

### 5. LinkedIn Publisher Module

Interfaces with the official LinkedIn API for publishing.

### 6. Connection Module

Discovers professionals and optionally sends connection requests.

---

## Database Design

### Posts Table

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer (PK) | Unique identifier |
| `topic` | String | Post topic |
| `project` | String | Associated project |
| `generated_post` | Text | Generated post content |
| `hashtags` | String | Associated hashtags |
| `scheduled_datetime` | DateTime | When to publish |
| `status` | String | `pending`, `published`, `failed` |
| `created_at` | DateTime | Creation timestamp |
| `published_at` | DateTime | Publication timestamp |

### Config Table

| Column | Type | Purpose |
|--------|------|---------|
| `key` | String (PK) | Setting name |
| `value` | Text | Setting value |
| `category` | String | `posting`, `connection`, `auth`, `prompt` |
| `updated_at` | DateTime | Last update |

### Logs Table

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer (PK) | Unique identifier |
| `action` | String | Action performed |
| `status` | String | `success`, `failed`, `pending` |
| `timestamp` | DateTime | When action occurred |
| `error` | Text | Error message if applicable |

---

## Workflows

### Posting Workflow

```
Step 1: User fills configuration
   ↓
Step 2: Configuration saved to database
   ↓
Step 3: Generate all required posts immediately
   ↓
Step 4: Store generated posts in SQLite
   ↓
Step 5: Scheduler checks every minute
   ↓
Step 6: If current time matches scheduled time
   ├─→ Publish via LinkedIn API
   └─→ Update database status to 'published'
   ↓
Step 7: If time hasn't arrived → Wait for next check
```

#### Why Generate Everything Upfront?

- **No API dependency during posting**: Reduces failure risk
- **Lower failure rate**: Posts are pre-generated and ready
- **User review capability**: Approve content before publication
- **Easy editing**: Modify generated posts before scheduling
- **Predictable schedule**: No delays from generation
- **Lower latency**: No waiting for LLM responses at publish time

### Connection Workflow

```
Step 1: Collect filter criteria from user
   ↓
Step 2: Search LinkedIn with filters
   ↓
Step 3: Display matching profiles
   ↓
Step 4: User reviews results
   ↓
Step 5: (Optional) Send connection requests
   ↓
Step 6: Log all activities
```

---

## LLM Prompt Structure

### Prompt Variables

- Topic
- Project
- Domain
- Target Audience
- Writing Tone
- Recent Context
- Previous Posts (for consistency)
- Required Hashtags
- Character Limit

### Prompt Instructions

The LLM should be instructed to:
- Sound **natural and human-like**
- Avoid AI clichés and overused phrases
- Minimize emoji usage (not eliminate)
- Avoid motivational spam
- Tell a story when contextually appropriate
- Include practical, actionable insights
- Incorporate relevant hashtags naturally
- End conclusions naturally
- Produce **unique, non-repetitive** posts
- Maintain consistent tone across all posts

---

## Scheduling Engine

### Scheduler Configuration

**Tool:** APScheduler  
**Frequency:** Runs every minute  
**Action:** Check database for posts ready to publish

### Scheduler Workflow

```
Every minute:
   ↓
Check database for pending posts
   ↓
Find posts where scheduled_datetime <= current_time
   ↓
For each post:
   ├─→ Attempt to publish via LinkedIn API
   ├─→ If success → Mark status as 'published'
   ├─→ If failure → Initiate retry policy
   └─→ Log action
```

### Retry Policy

| Attempt | Timing | Status |
|---------|--------|--------|
| Attempt 1 (Initial) | Immediate | Pending |
| Attempt 2 | 15 minutes later | Retry |
| Attempt 3 | 1 hour after initial | Retry |
| Attempt 4 | 6 hours after initial | Retry |
| After Attempt 4 | — | Marked Failed |

**Maximum Retries:** 3  
**Total wait time:** ~7 hours before final failure

---

## Frontend Structure

### Pages

| Page | Purpose |
|------|---------|
| **Home** | Landing page with quick actions |
| **Dashboard** | Overview of all metrics and status |
| **Posting Config** | Configure post generation preferences |
| **Connection Config** | Set up connection discovery filters |
| **Generated Posts** | View all AI-generated posts |
| **Scheduled Posts** | View posting calendar and timeline |
| **Publishing Logs** | Track all published posts and failures |
| **Settings** | API keys, account, preferences |

### Dashboard Widgets

- **Posts Generated** - Total posts created
- **Posts Scheduled** - Posts awaiting publication
- **Posts Published** - Successfully published count
- **Pending Posts** - Posts due to publish soon
- **Failed Posts** - Posts that failed to publish
- **Connections Sent** - Total connection requests sent
- **Success Rate** - Percentage of successful publishes

---

## Project Structure

```
linkedin-automation/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
├── README.md                       # Project documentation
├── .env                            # Environment variables
│
├── /static/
│   ├── /css/                       # Stylesheets
│   ├── /js/                        # JavaScript files
│   └── /images/                    # Images and icons
│
├── /templates/
│   ├── index.html                  # Home page
│   ├── dashboard.html              # Dashboard
│   ├── posting.html                # Posting configuration
│   ├── connections.html            # Connection configuration
│   ├── logs.html                   # Publishing logs
│   └── base.html                   # Base template
│
├── /modules/
│   ├── auth.py                     # Authentication logic
│   ├── generator.py                # LLM post generation
│   ├── scheduler.py                # Scheduling logic
│   ├── linkedin.py                 # LinkedIn API integration
│   ├── connections.py              # Connection discovery
│   ├── storage.py                  # Database operations
│   └── utils.py                    # Utility functions
│
├── /prompts/
│   ├── linkedin_prompt.txt         # LLM prompt template
│   └── connection_prompt.txt       # Connection discovery prompt
│
├── /database/
│   └── app.db                      # SQLite database
│
└── /logs/
    └── app.log                     # Application logs
```

---

## REST API Endpoints

### Configuration

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/config/posting` | POST | Save posting preferences |
| `/config/connections` | POST | Save connection preferences |

### Post Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate` | POST | Generate posts based on config |
| `/posts` | GET | Retrieve all posts |
| `/schedule` | POST | Schedule generated posts |
| `/publish` | POST | Manually publish a post |

### Connections

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/connect` | POST | Search and optionally send connection requests |

### Dashboard & Monitoring

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home page |
| `/dashboard` | GET | Main dashboard |
| `/logs` | GET | View publishing logs |

---

## Development Roadmap

### Phase 1: Project Foundation
- Flask application setup
- Frontend template structure
- Configuration form UI
- SQLite database initialization

### Phase 2: LLM Integration
- Prompt engineering and templates
- OpenRouter API integration
- Post generation logic
- Database storage and retrieval

### Phase 3: Scheduling & Publishing
- APScheduler implementation
- Publishing queue logic
- Retry policy implementation
- Error handling and logging

### Phase 4: Dashboard & Monitoring
- Dashboard UI development
- Real-time metrics widgets
- Generated posts viewer
- Publishing calendar

### Phase 5: LinkedIn API Integration
- LinkedIn OAuth authentication
- Official LinkedIn Posting API
- Token refresh logic
- Comprehensive testing

### Phase 6: Connection Discovery
- Profile search filters
- Results display UI
- Playwright-based browser automation
- Optional connection request automation

### Phase 7: Analytics & Polish
- Analytics dashboard
- Statistics and insights
- Data export functionality
- Settings management
- Final optimization and testing

---

## Future Enhancements

### AI Improvements

- Trending topic detection and suggestions
- Post rewriting and variation
- Comment generation for engagement
- Image caption generation
- Carousel and multi-slide content generation

### Scheduling Enhancements

- Recurring schedules (weekly, monthly patterns)
- Automatic holiday skipping
- Timezone support for global scheduling
- Optimal posting time prediction based on analytics

### Analytics

- Most-used hashtags tracking
- Average post length metrics
- Publishing frequency analysis
- Interactive posting calendar
- Engagement and success rate analytics

### Content Management

- Draft posts system
- Reusable templates
- Favorite topics library
- Prompt templates library
- Post preview and staging
- Bulk post generation

### Multi-Platform Support

- Twitter/X posting
- Medium integration
- Dev.to posting
- Hashnode support
- Facebook Pages integration
- Threads posting

### Security & Reliability

- Encrypted API key storage
- CSRF protection on all forms
- Input validation and sanitization
- Session management and timeouts
- Secure OAuth token refresh
- Rate limiting to prevent API abuse

---

## Final Deliverable

A lightweight, reliable Flask application that empowers LinkedIn content creators with:

✓ **Configuration System** - Simple setup wizard for all preferences  
✓ **Intelligent Generation** - AI-powered posts using OpenRouter  
✓ **Reliable Scheduling** - APScheduler-based automation with retry logic  
✓ **Automatic Publishing** - Official LinkedIn API integration  
✓ **Monitoring Dashboard** - Real-time status and metrics  
✓ **Networking Tools** - Connection discovery and optional automation  
✓ **Local Storage** - All data stored locally for reliability and future editing  

The application prioritizes **consistency, reliability, and user control** over aesthetic complexity.