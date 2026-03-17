# Production Deployment Guide

> **Current Status:** Phases 1–4 complete. Real LLM integration, web search, document export,
> WordPress publishing, and URL-to-article pipelines are all operational.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Running the System](#4-running-the-system)
5. [Core Workflows](#5-core-workflows)
6. [WordPress Publishing](#6-wordpress-publishing)
7. [URL Input Mode](#7-url-input-mode)
8. [Production Hardening](#8-production-hardening)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
| ----------- | ------- | ----------- |
| Python      | 3.8     | 3.12        |
| Node.js     | 18      | 20          |
| RAM         | 512 MB  | 2 GB        |
| Disk        | 500 MB  | 2 GB        |

### API Keys Required

| Service          | Purpose                                  | Get Key                             |
| ---------------- | ---------------------------------------- | ----------------------------------- |
| Anthropic Claude | LLM (required)                           | <https://console.anthropic.com/>    |
| OpenAI GPT       | LLM alternative (optional)               | <https://platform.openai.com/>      |
| Firecrawl        | Web search + URL scraping (recommended)  | <https://firecrawl.dev/>            |
| Serper           | Google Search alternative (optional)     | <https://serper.dev/>               |

---

## 2. Installation

```bash
# Clone repository
git clone https://github.com/zoopster/content-creation-engine.git
cd content-creation-engine

# Create and activate Python virtual environment
python3.12 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install all dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## 3. Configuration

### 3.1 Environment File

```bash
cp .env.example .env
```

Edit `.env` with your actual values. The minimum required configuration depends on your use case:

#### Minimum: LLM-only (no real web search)

```bash
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-6
ENABLE_WEB_SEARCH=false
```

#### Recommended: Full production setup

```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-6

# Web search (enables real research and URL scraping)
ENABLE_WEB_SEARCH=true
FIRECRAWL_API_KEY=fc-...

# WordPress publishing
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# API server
API_HOST=127.0.0.1
API_PORT=8000
API_ENV=production
API_DEBUG=false

# Output
OUTPUT_DIR=./output
```

### 3.2 WordPress Application Password

1. Log in to WordPress Admin
2. Go to **Users → Profile** (or **Users → Edit User** for other accounts)
3. Scroll to **Application Passwords**
4. Enter a name (e.g. `Content Engine`), click **Add New Application Password**
5. Copy the generated password — paste it as-is into `WORDPRESS_APP_PASSWORD` (spaces are stripped automatically)

> **Note:** Application Passwords require WordPress 5.6+ and HTTPS on your site.

### 3.3 Model Selection

To use a different model per agent, set in `.env`:

```bash
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-6   # Best quality
# DEFAULT_MODEL=claude-3-5-haiku-20241022  # Faster, cheaper
```

Or mix providers per agent via `core/models/config.py`.

---

## 4. Running the System

### 4.1 Backend API

```bash
source venv/bin/activate

# Development (auto-reload)
uvicorn api.main:app --reload --port 8000

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 2
```

API docs available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### 4.2 Frontend

```bash
cd frontend

# Development (hot reload at :5173)
npm run dev

# Production build
npm run build
# Output in frontend/dist/ — serve with any static file server
```

### 4.3 Verify Everything Is Running

```bash
# Health check
curl http://localhost:8000/api/health

# Verify WordPress connection (if configured)
curl http://localhost:8000/api/publish/wordpress/verify

# Test LLM connectivity (runs a minimal workflow)
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"request_text": "Write a short test article about productivity", "content_types": ["article"]}'
```

### 4.4 Process Manager (Production)

To keep the API running persistently on Linux, use a systemd service:

```ini
# /etc/systemd/system/cce-api.service
[Unit]
Description=Content Creation Engine API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/content-creation-engine
EnvironmentFile=/opt/content-creation-engine/.env
ExecStart=/opt/content-creation-engine/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cce-api
sudo systemctl start cce-api
sudo systemctl status cce-api
```

---

## 5. Core Workflows

### 5.1 Topic-Based Article (Search + LLM)

The standard workflow: provide a topic and let the system research, write, and produce a document.

```bash
# Submit workflow
JOB=$(curl -s -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Write a comprehensive article about AI adoption in small businesses",
    "content_types": ["article"],
    "target_audience": "Small business owners",
    "tone": "professional",
    "word_count_min": 800,
    "word_count_max": 1500,
    "output_format": "html"
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

echo "Job ID: $JOB"

# Poll status
curl http://localhost:8000/api/workflow/status/$JOB

# Get result when completed
curl http://localhost:8000/api/workflow/result/$JOB
```

**Pipeline:** Orchestrator → Research (web search or mock) → Content Brief → Creation (LLM) → Brand Voice → Production (HTML/DOCX/PDF)

### 5.2 Python SDK (Direct)

```python
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

executor = WorkflowExecutor()
result = executor.execute(WorkflowRequest(
    request_text="Write an article about sustainable cloud computing",
    content_types=[ContentType.ARTICLE],
    additional_context={
        "target_audience": "IT decision makers",
        "output_format": "html",
    }
))

if result.success:
    draft = result.outputs["draft_content"]
    print(f"Generated {draft.word_count} words")
    print(draft.content[:500])
```

### 5.3 Output Formats

| Format         | `output_format` value | Notes                            |
| -------------- | --------------------- | -------------------------------- |
| HTML           | `html`                | Default, best for WordPress      |
| Markdown       | `markdown`            | Plain text                       |
| Word (DOCX)    | `docx`                | Requires `python-docx`           |
| PDF            | `pdf`                 | Requires `reportlab`             |
| PowerPoint     | `pptx`                | For presentation content type    |

---

## 6. WordPress Publishing

### 6.1 Publish a Completed Article

After a workflow completes, publish the content directly to WordPress:

```bash
curl -X POST http://localhost:8000/api/publish/wordpress \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Adoption in Small Businesses: A 2026 Guide",
    "content": "<h2>Introduction</h2><p>Artificial intelligence...</p>",
    "content_format": "html",
    "status": "draft",
    "category_names": ["Technology", "Business"],
    "tag_names": ["AI", "small business", "2026"]
  }'
```

Response:

```json
{
  "success": true,
  "post_id": 142,
  "post_url": "https://your-site.com/ai-adoption-small-businesses",
  "edit_url": "https://your-site.com/wp-admin/post.php?post=142&action=edit",
  "status": "draft"
}
```

Open `edit_url` to review and publish the draft in WordPress.

### 6.2 Post Status Options

| Status    | Behaviour                              |
| --------- | -------------------------------------- |
| `draft`   | Saved as draft, not visible publicly   |
| `publish` | Live immediately                       |
| `pending` | Queued for editor review               |
| `private` | Visible only to logged-in editors      |

### 6.3 Multi-Site Support

Override credentials per-request to publish to different WordPress sites:

```bash
curl -X POST http://localhost:8000/api/publish/wordpress \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Article",
    "content": "...",
    "credentials": {
      "wp_url": "https://second-site.com",
      "username": "editor",
      "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
    }
  }'
```

### 6.4 Utility Endpoints

```bash
# Test connection
curl http://localhost:8000/api/publish/wordpress/verify

# List existing categories
curl http://localhost:8000/api/publish/wordpress/categories

# List existing tags
curl http://localhost:8000/api/publish/wordpress/tags
```

Categories and tags are **auto-created** if they don't exist when you publish.

---

## 7. URL Input Mode

Feed specific URLs as primary source material instead of (or alongside) web search.

### 7.1 Single URL

```bash
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Write a comprehensive article based on this source",
    "content_types": ["article"],
    "source_urls": ["https://example.com/original-article"],
    "target_audience": "General readers",
    "output_format": "html"
  }'
```

### 7.2 Multiple URLs

Up to 10 URLs can be provided. All are scraped and used as primary sources:

```bash
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Synthesize these sources into a definitive guide",
    "content_types": ["article"],
    "source_urls": [
      "https://site-a.com/research-paper",
      "https://site-b.com/case-study",
      "https://site-c.com/industry-report"
    ],
    "tone": "authoritative",
    "word_count_min": 1200
  }'
```

### 7.3 How URL Scraping Works

1. Each URL is scraped using **Firecrawl** (if `FIRECRAWL_API_KEY` is set) for clean markdown extraction — handles JavaScript-rendered pages
2. Falls back to a basic **httpx** fetch + HTML stripping if Firecrawl is not configured
3. Scraped content is given a **credibility score of 0.9** (vs ~0.7 for web search results) so it dominates the research brief
4. With `ENABLE_WEB_SEARCH=false`, URL-only mode works — no additional search is performed

### 7.4 End-to-End: Scrape → Write → Publish

```bash
# Step 1: Submit workflow with source URLs
JOB=$(curl -s -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Rewrite this as a polished article for our blog",
    "content_types": ["article"],
    "source_urls": ["https://example.com/source"],
    "output_format": "html"
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

# Step 2: Wait for completion and get content preview
RESULT=$(curl -s http://localhost:8000/api/workflow/result/$JOB)
echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('content_preview',''))"

# Step 3: Download full HTML file and publish to WordPress
curl -o article.html http://localhost:8000/api/workflow/download/$JOB/0

curl -X POST http://localhost:8000/api/publish/wordpress \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Your Article Title\",
    \"content\": \"$(cat article.html)\",
    \"status\": \"draft\",
    \"category_names\": [\"Blog\"]
  }"
```

> **Tip:** `content_preview` is capped at 500 characters. Always use the download endpoint
> (`GET /api/workflow/download/{job_id}/0`) for the full article body.

---

## 8. Production Hardening

### 8.1 Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;  # Long timeout for LLM workflows
    }

    # Frontend
    location / {
        root /opt/content-creation-engine/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### 8.2 CORS Configuration

Update `.env` for your production frontend URL:

```bash
CORS_ORIGINS=https://your-domain.com
```

### 8.3 Persistent Job Storage

By default, workflow jobs are stored in memory and lost on restart. For persistence:

- Replace the `jobs: Dict` in [api/routers/workflow.py](api/routers/workflow.py) with Redis (`redis-py`) or a lightweight SQLite store
- The current in-memory store is fine for single-instance deployments where job loss on restart is acceptable

### 8.4 Rate Limiting

Enable rate limiting in `.env`:

```bash
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
```

### 8.5 Security Checklist

- [ ] Set `API_DEBUG=false` in production
- [ ] Use HTTPS (required for WordPress Application Passwords)
- [ ] Restrict `CORS_ORIGINS` to your actual frontend domain
- [ ] Store `.env` with `chmod 600 .env`
- [ ] Never commit `.env` to git (already in `.gitignore`)
- [ ] Run `pip audit` periodically for dependency vulnerabilities
- [ ] Rotate API keys if compromised (Anthropic, Firecrawl, WordPress App Password)

---

## 9. Troubleshooting

### LLM / API issues

**Symptom:** `AuthenticationError` or `401 Unauthorized` from Claude/OpenAI

```bash
# Verify key is loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('ANTHROPIC_API_KEY','NOT SET')[:10])"
```

**Symptom:** Workflow completes but content is mock/generic (no real LLM output)

- Check `DEFAULT_PROVIDER` and `DEFAULT_MODEL` are set in `.env`
- Verify the venv is activated when running uvicorn

---

### Web search issues

**Symptom:** Research uses mock data despite `ENABLE_WEB_SEARCH=true`

```bash
# Check provider initialisation
python3 -c "
from core.search import configure_search, get_search_provider
configure_search()
p = get_search_provider()
print('Provider:', p.name if p else 'None')
print('Available:', p.is_available() if p else False)
"
```

- Ensure `FIRECRAWL_API_KEY` starts with `fc-`
- Test the key directly: `curl -H "Authorization: Bearer fc-..." https://api.firecrawl.dev/v1/search?q=test`

---

### WordPress publish issues

**Symptom:** `HTTP 401` from publish endpoint

- Confirm Application Password was copied correctly (with or without spaces — both work)
- Verify your WordPress user has the `publish_posts` capability
- Check your site uses HTTPS (some hosts block Application Passwords on HTTP)

**Symptom:** `Could not connect` error

```bash
# Test REST API availability directly
curl https://your-site.com/wp-json/wp/v2/posts?per_page=1
```

If this returns `{"code":"rest_no_route",...}`, the WordPress REST API may be disabled by a security plugin.

---

### URL scraping issues

**Symptom:** Scraped content is empty or very short

- The target URL may require JavaScript rendering — use Firecrawl (configured via `FIRECRAWL_API_KEY`) for JS-heavy sites
- Some sites block scrapers; check if the URL loads in a browser with no cookies or extensions

**Symptom:** `Failed to scrape` warnings in logs

```bash
# Test Firecrawl scrape directly
python3 -c "
import asyncio
from core.search.firecrawl_provider import FirecrawlSearchProvider
import os; from dotenv import load_dotenv; load_dotenv()
p = FirecrawlSearchProvider(api_key=os.environ['FIRECRAWL_API_KEY'])
result = asyncio.run(p.scrape_url('https://example.com'))
print('Keys:', list(result.keys()))
print('Content length:', len(result.get('markdown','') or ''))
"
```

---

### General

**Symptom:** `ModuleNotFoundError`

```bash
# Always run from project root with venv activated
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

**Symptom:** Port 8000 already in use

```bash
lsof -i :8000 | grep LISTEN
kill -9 <PID>
```

**Symptom:** Workflow times out or hangs

- LLM workflows can take 30–120 seconds depending on model and content length
- Increase timeout: `proxy_read_timeout 300s` in nginx, or `WORKFLOW_TIMEOUT=300` in `.env`
- Check API server logs: `journalctl -u cce-api -f`

---

## Reference

### API Endpoints

| Method | Endpoint                                      | Description               |
| ------ | --------------------------------------------- | ------------------------- |
| GET    | `/api/health`                                 | Health check              |
| POST   | `/api/workflow/execute`                       | Start workflow (async)    |
| GET    | `/api/workflow/status/{job_id}`               | Poll job status           |
| GET    | `/api/workflow/result/{job_id}`               | Get completed result      |
| GET    | `/api/workflow/download/{job_id}/{file_id}`   | Download output file      |
| GET    | `/api/publish/wordpress/verify`               | Test WordPress connection |
| GET    | `/api/publish/wordpress/categories`           | List WP categories        |
| GET    | `/api/publish/wordpress/tags`                 | List WP tags              |
| POST   | `/api/publish/wordpress`                      | Publish post              |

### Key `.env` Variables

| Variable                  | Default                     | Description                    |
| ------------------------- | --------------------------- | ------------------------------ |
| `ANTHROPIC_API_KEY`       | —                           | Required for Claude            |
| `OPENAI_API_KEY`          | —                           | Optional, for GPT              |
| `DEFAULT_PROVIDER`        | `anthropic`                 | LLM provider                   |
| `DEFAULT_MODEL`           | `claude-sonnet-4-6`  | Model ID                       |
| `ENABLE_WEB_SEARCH`       | `false`                     | Enable real research           |
| `FIRECRAWL_API_KEY`       | —                           | Web search + URL scraping      |
| `WORDPRESS_URL`           | —                           | WordPress site URL             |
| `WORDPRESS_USERNAME`      | —                           | WordPress username             |
| `WORDPRESS_APP_PASSWORD`  | —                           | Application password           |
| `OUTPUT_DIR`              | `./output`                  | Generated file location        |
| `API_PORT`                | `8000`                      | API server port                |
| `CORS_ORIGINS`            | `localhost:5173,3000`       | Allowed frontend origins       |

### Phase Status

| Phase | Status | Features |
| --- | --- | --- |
| 1 | Complete | Orchestrator, Content Brief, Brand Voice |
| 2 | Complete | Research Agent, Creation Agent, End-to-End Workflows |
| 3 | Complete | Production Agent, DOCX/PDF/PPTX, LLM integration, API + Frontend |
| 4 | In Progress | Web search, URL input, WordPress publish (all done); content repurpose (pending) |
| 5 | Planned | CMS integrations, parallel processing, quality automation |
