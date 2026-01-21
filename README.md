# Vertical-AI-Agents

AI agent workflows for vertical-specific automation using n8n and Claude.

## Project Structure

```
Vertical-AI-Agents/
├── n8n-workflows/     # Exported n8n workflow JSONs for version control
├── prompts/           # Prompt templates for each use case
├── scripts/           # Python utilities (cost tracking, data validation)
├── customer-configs/  # Configuration files per customer
├── docs/              # Documentation and runbooks
└── tests/             # Sample data for testing prompts
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/Vertical-AI-Agents.git
cd Vertical-AI-Agents
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### n8n Workflows

Export workflows from n8n and save them in `/n8n-workflows/` for version control:

```bash
# Export via n8n CLI or API
n8n export:workflow --id=<workflow_id> --output=n8n-workflows/workflow-name.json
```

### Prompt Templates

Store prompt templates in `/prompts/` organized by use case:

```
prompts/
├── classification/
├── extraction/
├── summarization/
└── customer-specific/
```

### Cost Tracking

Run the cost tracking utility:

```bash
python scripts/cost_tracker.py
```

## Customer Configurations

Each customer has a YAML config file in `/customer-configs/`:

```yaml
customer_id: example
model: claude-sonnet-4-20250514
max_tokens: 4096
prompts:
  - classification
  - extraction
```

## Testing

Run tests with sample data:

```bash
pytest tests/
```

## Documentation

See `/docs/` for:
- Workflow runbooks
- Prompt engineering guidelines
- Customer onboarding guides
