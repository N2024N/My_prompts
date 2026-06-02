# AI Prompt Engineering Studio API

FastAPI backend for the AI Prompt Engineering Studio - a Notion-based prompt engineering workspace.

## Features

- **Prompt Optimization**: AI-powered prompt analysis and optimization suggestions
- **Prompt Evaluation**: Multi-dimensional scoring of prompts against test cases
- **Version Management**: Track prompt iterations and version history
- **Notion Integration**: Seamless integration with Notion for data storage
- **Activation System**: License management for paid users

## Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **AI Provider**: DeepSeek API (primary)
- **Database**: Notion (user data) + Supabase (activation codes)
- **Deployment**: Railway (Docker)
- **Authentication**: Activation code system

## Project Structure

```
prompt-studio-api/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .env.example        # Environment variables template
├── DATABASE_DESIGN.md  # Notion database schema
├── supabase_schema.sql # Supabase table definitions
└── README.md           # This file
```

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd prompt-studio-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file:

```env
# Notion Integration
NOTION_API_KEY=ntn_your_notion_integration_secret

# DeepSeek API
DEEPSEEK_API_KEY=sk_your_deepseek_api_key

# Supabase (for activation codes)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# API Base URL (for activation responses)
API_BASE_URL=https://your-app.railway.app

# Activation Code Table Name
ACTIVATION_CODE_TABLE=activation_codes
```

### 3. Set Up Databases

#### Notion Databases
1. Create 5 databases in Notion according to `DATABASE_DESIGN.md`
2. Share each database with your Notion Integration
3. Get database IDs from Notion page URLs

#### Supabase Tables
1. Create a new Supabase project at https://supabase.com
2. Run the SQL from `supabase_schema.sql` in the SQL editor
3. Get your Supabase URL and anon key from Project Settings → API

### 4. Run Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

### 5. Deploy to Railway

1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables in Railway dashboard
4. Deploy automatically

## API Endpoints

### Public Endpoints
- `GET /` - Service information
- `GET /health` - Health check
- `POST /activate` - Activate a license

### Protected Endpoints (require activation code)
- `POST /optimize` - Optimize a prompt
- `POST /evaluate` - Evaluate a prompt

### Authentication
Include activation code in header:
```
X-Activation-Code: YOUR_ACTIVATION_CODE
```

## Notion Integration

### Required Databases
1. `prompts` - Main prompts table
2. `prompt_versions` - Version history
3. `evaluations` - Evaluation records
4. `prompt_templates` - Template library

### Database IDs
After creating databases, add their IDs to environment variables:

```env
NOTION_PROMPTS_DB_ID=your_prompts_db_id
NOTION_VERSIONS_DB_ID=your_versions_db_id
NOTION_EVALUATIONS_DB_ID=your_evaluations_db_id
NOTION_TEMPLATES_DB_ID=your_templates_db_id
```

## Activation System

### Code Generation
Use the Supabase function to generate activation codes:

```sql
SELECT * FROM generate_activation_codes(10, 'standard');
```

### Activation Flow
1. User purchases on Gumroad
2. System generates unique activation code
3. User enters code in Notion template
4. Notion template calls `/activate` endpoint
5. Backend validates and marks code as used

## Development

### Adding New AI Providers
The code is structured to easily add new AI providers:

1. Add to `ModelProvider` enum in `main.py`
2. Implement provider-specific logic in `call_ai()` function
3. Update environment variables as needed

### Testing
```bash
# Run tests (to be implemented)
pytest tests/
```

## Cost Management

### Monthly Estimates
- **Railway**: $5-10/month (Hobby plan)
- **DeepSeek API**: <$5/month (1000+ calls)
- **Supabase**: Free tier
- **Total**: <$15/month

### Monitoring
- Railway provides basic metrics
- Add logging for API call tracking
- Monitor DeepSeek API usage in dashboard

## License

This project is part of the AI Prompt Engineering Studio commercial product.
For licensing information, contact the product owner.