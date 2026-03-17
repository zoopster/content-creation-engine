# Quick Start Guide

Get started with the Content Creation Engine in a few minutes.

## Prerequisites

- Python 3.12+ (3.8+ supported)
- Node.js 18+ and npm (frontend only)
- API key for at least one LLM provider (Anthropic recommended)

## 1. Install

```bash
git clone https://github.com/zoopster/content-creation-engine.git
cd content-creation-engine

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required — or use OPENAI_API_KEY
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-6
```

**Optional — enable real web search:**

```bash
ENABLE_WEB_SEARCH=true
FIRECRAWL_API_KEY=fc-...        # Recommended: https://firecrawl.dev/
# SERPER_API_KEY=...            # Alternative (Google Search)
```

**Optional — WordPress publishing:**

```bash
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

> Create an Application Password at: **WordPress Admin → Users → Profile → Application Passwords**

## 3. Run

### Option A: Full Stack (API + Frontend)

```bash
# Terminal 1 — FastAPI backend
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2 — React frontend
cd frontend
npm install       # First time only
npm run dev
```

- Frontend wizard: <http://localhost:5173>
- API docs (Swagger): <http://localhost:8000/docs>

### Option B: API only

```bash
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

### Option C: Python scripts

```bash
python3 mvp_test.py             # Integration test (no API keys needed)
python3 examples/phase2_endtoend.py
python3 examples/phase3_production.py
python3 examples/web_search_example.py
```

## 4. API Usage

### Submit a workflow

```bash
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Write an article about AI in healthcare",
    "content_types": ["article"],
    "output_formats": ["docx", "pdf"]
  }'
```

Returns a `job_id`. Poll for status:

```bash
curl http://localhost:8000/api/workflow/status/{job_id}
```

Retrieve the result when `status` is `completed`:

```bash
curl http://localhost:8000/api/workflow/result/{job_id}
```

Download a generated file:

```bash
curl -O http://localhost:8000/api/workflow/download/{job_id}/0
```

### Publish to WordPress

```bash
curl -X POST http://localhost:8000/api/publish/wordpress \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Article",
    "content": "<h2>Intro</h2><p>Content here...</p>",
    "content_format": "html",
    "status": "draft",
    "category_names": ["Technology"],
    "tag_names": ["AI", "healthcare"]
  }'
```

Verify connection first:

```bash
curl http://localhost:8000/api/publish/wordpress/verify
```

## 5. API Endpoints Reference

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/health` | Health check |
| GET | `/api/output-formats` | List supported output formats |
| POST | `/api/workflow/execute` | Submit a content workflow |
| GET | `/api/workflow/status/{job_id}` | Poll workflow status |
| GET | `/api/workflow/result/{job_id}` | Get completed result |
| GET | `/api/workflow/download/{job_id}/{file_id}` | Download generated file |
| GET | `/api/workflow/jobs` | List all jobs (debug) |
| GET | `/api/content-types` | List content types |
| GET | `/api/platforms` | List supported platforms |
| GET | `/api/templates` | List document templates |
| GET | `/api/publish/wordpress/verify` | Test WordPress connection |
| GET | `/api/publish/wordpress/categories` | List WordPress categories |
| GET | `/api/publish/wordpress/tags` | List WordPress tags |
| POST | `/api/publish/wordpress` | Publish post to WordPress |

## 6. Content Types & Output Formats

**Content types:** `article`, `blog_post`, `social_post`, `whitepaper`, `email`, `newsletter`, `presentation`, `video_script`, `case_study`

**Output formats:** `markdown`, `html`, `docx`, `pdf`, `pptx`

**Tone types:** `professional`, `conversational`, `technical`, `educational`, `persuasive`, `inspirational`

## 7. Example Scripts

| Script | What it shows |
| ------ | ------------- |
| `examples/phase1_example.py` | Orchestrator planning, content brief, brand voice |
| `examples/phase2_endtoend.py` | Full article + multi-platform campaign workflow |
| `examples/phase3_production.py` | DOCX, PDF, PPTX document generation |
| `examples/web_search_example.py` | Real web search with Firecrawl/Serper |
| `examples/multi_model_example.py` | Switching between Anthropic and OpenAI models |

## Need Help?

- Architecture overview: `CLAUDE.md`
- Full documentation: `README.md`
- Agent docs: `agents/*/AGENT.md`
- Skill docs: `skills/*/SKILL.md`
- API reference (interactive): <http://localhost:8000/docs>
