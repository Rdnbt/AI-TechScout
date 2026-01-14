<h1 align="center">
  <b>AI-TechScout: AI-Powered</b><br>
  <b>Technology Scouting & Discovery 🔭</b><br>
</h1>

<p align="center">
  <b>Automated technology scouting powered by Large Language Models</b>
</p>

AI-TechScout is an automated technology scouting system that leverages Large Language Models to discover, evaluate, and report on emerging technologies. Built on the foundation of [The AI Scientist](https://github.com/SakanaAI/AI-Scientist), this system adapts the automated research capabilities for strategic technology intelligence.

## 🎯 What is Technology Scouting?

Technology scouting is the systematic process of identifying emerging technologies that could impact your organization. AI-TechScout automates this process by:

1. **Discovering** emerging technologies from academic papers, patents, and news
2. **Evaluating** technologies for maturity, strategic fit, and competitive landscape
3. **Analyzing** trends and identifying opportunities
4. **Generating** actionable reports for decision-makers

## ✨ Features

- **Multi-Source Discovery**: Searches academic papers (Semantic Scholar, OpenAlex), patents (USPTO), and news sources
- **LLM-Powered Analysis**: Uses frontier LLMs (Claude, GPT-4, etc.) for intelligent analysis
- **Maturity Assessment**: TRL-based technology readiness evaluation
- **Strategic Fit Analysis**: Evaluates technologies against your organization's priorities
- **Competitive Intelligence**: Analyzes competitive landscape and key players
- **Automated Reports**: Generates executive summaries and detailed reports
- **Domain Templates**: Pre-configured templates for AI/ML, Biotech, CleanTech, and FinTech

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-TechScout.git
cd AI-TechScout

# Create virtual environment (Python 3.10+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Set API Keys

```bash
# Required: LLM API key (choose one)
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"

# Optional: For better search results
export S2_API_KEY="your-semantic-scholar-key"  # Academic papers
export SERPAPI_KEY="your-serpapi-key"           # Patent search
export GOOGLE_NEWS_API_KEY="your-newsapi-key"   # News search
```

### Run Your First Scout

```bash
# Using a pre-built template
python launch_techscout.py --template templates/tech_scout/ai_ml

# Or specify a custom domain
python launch_techscout.py \
  --domain "Quantum Computing" \
  --focus "Quantum Hardware,Quantum Algorithms,Quantum Cryptography" \
  --output ./quantum_scouting
```

## 📁 Project Structure

```
AI-TechScout/
├── launch_techscout.py          # Main entry point for tech scouting
├── launch_scientist.py          # Original AI Scientist entry point
├── tech_scout/                  # Technology scouting modules
│   ├── __init__.py
│   ├── scout_technologies.py    # Technology discovery
│   ├── evaluate_technologies.py # Technology evaluation
│   └── generate_report.py       # Report generation
├── ai_scientist/                # Core LLM utilities (from AI Scientist)
│   ├── llm.py                   # LLM client management
│   ├── generate_ideas.py        # Idea generation (for research mode)
│   └── ...
├── templates/
│   ├── tech_scout/              # Technology scouting templates
│   │   ├── ai_ml/               # AI/ML domain template
│   │   ├── biotech/             # Biotechnology template
│   │   ├── cleantech/           # Clean technology template
│   │   └── fintech/             # Financial technology template
│   └── ...                      # Original AI Scientist templates
└── requirements.txt
```

## 🔧 Usage

### Command Line Options

```bash
python launch_techscout.py [OPTIONS]

Scouting Configuration:
  --template PATH       Path to scouting template directory
  --config PATH         Path to JSON configuration file
  --domain TEXT         Technology domain to scout
  --focus TEXT          Comma-separated focus areas
  --queries TEXT        Comma-separated search queries

Output Configuration:
  --output PATH         Output directory (default: ./scouting_results)
  --report-format       Output format: markdown, html, json

Model Configuration:
  --model TEXT          LLM model to use (default: claude-3-5-sonnet-20241022)

Execution Options:
  --skip-search         Use cached search results
  --skip-evaluation     Skip technology evaluation
  --skip-report         Skip report generation
  --num-reflections N   LLM refinement iterations (default: 3)
  --year-lookback N     Years to search back (default: 3)

Organization Context:
  --org-context PATH    Path to organization context JSON
```

### Examples

```bash
# Scout AI/ML with detailed output
python launch_techscout.py \
  --template templates/tech_scout/ai_ml \
  --output ./ai_scouting_$(date +%Y%m%d) \
  --report-format html \
  --verbose

# Scout a custom domain with organization context
python launch_techscout.py \
  --domain "Robotics" \
  --focus "Industrial Automation,Service Robots,Autonomous Vehicles" \
  --org-context my_org_context.json \
  --model gpt-4o

# Re-run analysis with cached data
python launch_techscout.py \
  --template templates/tech_scout/biotech \
  --skip-search \
  --output ./biotech_results
```

## 📊 Output Files

After running, you'll find these files in your output directory:

| File | Description |
|------|-------------|
| `scouting_results.json` | Raw discovered technologies and analysis |
| `batch_evaluation_results.json` | Detailed technology evaluations |
| `scouting_report.md` | Comprehensive markdown report |
| `executive_summary.md` | One-page executive summary |
| `search_queries.json` | Search queries used |

## 🎨 Creating Custom Templates

Create a new template by adding a directory under `templates/tech_scout/`:

```
templates/tech_scout/my_domain/
├── prompt.json              # Domain configuration
├── seed_queries.json        # Initial search queries
├── existing_technologies.json # Known technologies to skip
├── organization_context.json  # Your org's context
└── README.md                # Template documentation
```

### prompt.json Example

```json
{
    "system": "You are an expert technology scout in [DOMAIN]...",
    "domain": "My Domain",
    "task_description": "Scout for emerging technologies in...",
    "focus_areas": ["Area 1", "Area 2", "Area 3"],
    "evaluation_criteria": [
        {"name": "criterion1", "weight": 0.3, "description": "..."},
        {"name": "criterion2", "weight": 0.3, "description": "..."}
    ]
}
```

## 🤖 Supported Models

AI-TechScout supports all models from the original AI Scientist:

- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **OpenAI**: GPT-4o, GPT-4o-mini, o1, o3-mini
- **Google**: Gemini 1.5 Pro, Gemini 2.0 Flash
- **DeepSeek**: DeepSeek Chat, DeepSeek Reasoner
- **And more**: See `ai_scientist/llm.py` for full list

## 📈 Evaluation Framework

### Technology Readiness Levels (TRL)

Technologies are assessed on a 1-9 TRL scale:

| TRL | Stage | Description |
|-----|-------|-------------|
| 1-2 | Basic Research | Fundamental principles observed |
| 3-4 | Applied Research | Proof of concept demonstrated |
| 5-6 | Development | Technology validated in relevant environment |
| 7-8 | Demonstration | System prototype demonstrated |
| 9 | Market Ready | Actual system proven in operational environment |

### Strategic Fit Analysis

Each technology is evaluated against:
- Alignment with strategic priorities
- Build vs. buy recommendation
- Investment type (strategic/exploratory/defensive)
- Time sensitivity
- Competitive advantage potential

## 🔒 API Keys & Security

| API | Purpose | Required? |
|-----|---------|-----------|
| OpenAI / Anthropic | LLM analysis | **Yes** (one required) |
| Semantic Scholar | Academic papers | Recommended |
| SerpAPI | Patent search | Optional |
| NewsAPI | News articles | Optional |

## 🙏 Credits

AI-TechScout is built upon [The AI Scientist](https://github.com/SakanaAI/AI-Scientist) by Sakana AI. We thank the original authors for their groundbreaking work on automated scientific discovery.

## 📄 License

This project inherits the license from the original AI Scientist repository. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests for:
- New domain templates
- Additional data sources
- Improved analysis prompts
- Bug fixes and enhancements

---

<p align="center">
  <b>Transform your technology strategy with AI-powered scouting</b>
</p>
