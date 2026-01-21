# Getting Started

## Prerequisites

- Python 3.10+
- n8n instance (self-hosted or cloud)
- Anthropic API key

## Quick Start

1. Set up your environment variables in `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Import workflows into n8n from `/n8n-workflows/`
4. Configure customer settings in `/customer-configs/`

## Workflow Development

1. Design workflow in n8n
2. Export JSON to `/n8n-workflows/`
3. Create corresponding prompt templates in `/prompts/`
4. Add test cases in `/tests/`
5. Document in `/docs/`
