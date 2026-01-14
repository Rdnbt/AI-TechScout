# AI/ML Technology Scouting Template

This template is configured for scouting emerging technologies in Artificial Intelligence and Machine Learning.

## Focus Areas

1. **Large Language Models and Generative AI** - Next-generation LLMs, prompt engineering, and generative applications
2. **Computer Vision and Multimodal AI** - Image, video, and multimodal understanding
3. **AI Infrastructure and MLOps** - Tools and platforms for deploying AI at scale
4. **Edge AI and Embedded ML** - Running AI on devices and edge infrastructure
5. **AI Safety and Alignment** - Ensuring AI systems are safe and aligned with human values
6. **Autonomous Systems** - AI-powered robotics and autonomous agents

## Usage

```bash
# Run scouting with this template
python launch_techscout.py --template templates/tech_scout/ai_ml

# Or with custom output directory
python launch_techscout.py --template templates/tech_scout/ai_ml --output ./ai_ml_scouting_results
```

## Files

- `prompt.json` - System prompt and domain configuration
- `seed_queries.json` - Initial search queries for data collection
- `existing_technologies.json` - Technologies already known/deployed (to avoid rediscovery)
- `organization_context.json` - Organization context for strategic fit analysis

## Customization

Edit `organization_context.json` to match your organization's:
- Industry and company size
- Current technical capabilities
- Strategic priorities
- Risk tolerance and investment horizon
- Constraints and budget range

## Expected Outputs

After running, you'll find in the output directory:
- `scouting_results.json` - Raw scouting data and discovered technologies
- `batch_evaluation_results.json` - Detailed technology evaluations
- `scouting_report.md` - Comprehensive markdown report
- `executive_summary.md` - One-page executive summary
