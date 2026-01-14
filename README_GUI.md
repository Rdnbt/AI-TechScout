# AI-TechScout Dashboard

This is a modern, interactive web interface for the AI-TechScout system.

## Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

And your environment variables set in a `.env` file (OPENAI_API_KEY, SERPAPI_KEY, etc.).

## Running the Dashboard

To launch the UI, run:

```bash
streamlit run streamlit_app.py
```

This will open the dashboard in your default browser (usually at http://localhost:8501).

## Features

- **Discovery Wizard**: Parameterize your scout with a friendly UI.
- **Interactive Results**: View found technologies in sortable tables.
- **Visual Analysis**: Charts and graphs for technology evaluation (Maturity vs Strategic Fit).
- **Report Generation**: One-click report generation and download.
