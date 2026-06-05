#  DevFlow Agent

AI-powered GitLab CI/CD failure detection & auto-fix using Gemini AI.

## What it does
-  Automatically detects failed GitLab pipelines
-  Uses Gemini AI to diagnose root cause
-  Auto-creates GitLab issues with full analysis
-  One-click pipeline retry

## Tech Stack
- Google Gemini AI
- GitLab API + MCP
- Python + Flask
- Google Cloud

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API keys to `.env`
4. Run: `python3 app.py`

## Built for
Google Cloud Rapid Agent Hackathon — GitLab Track
