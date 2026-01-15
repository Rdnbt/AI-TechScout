# Japan AI/ML Market Scouting Template (2025-2026)

This template is configured for scouting AI and machine learning technologies **specific to the Japanese market** for 2025-2026.

## 🇯🇵 Japan Market Focus

This template automatically enables Japan-specific data sources:
- **J-STAGE** - Japanese academic papers (JST database)
- **Google News Japan** - Japan-locale news coverage
- **JP Patents** - Japanese patent office filings

## Focus Areas

1. **Japanese Enterprise AI** - NEC, Fujitsu, Hitachi AI platforms for Japanese corporations
2. **Japanese LLM Development** - NTT Tsuzumi, CyberAgent CALM, ELYZA Japanese language models
3. **Manufacturing AI (Monozukuri)** - Predictive maintenance, quality inspection, factory automation
4. **Robotics AI** - FANUC, Yaskawa, collaborative robots, warehouse automation
5. **Healthcare AI for Aging Society** - Elder care, medical imaging, remote diagnosis
6. **Autonomous Driving** - Toyota Woven, Honda, Sony autonomous vehicle initiatives
7. **Society 5.0 Smart Cities** - Government-backed smart city AI applications
8. **Japanese AI Startups** - Preferred Networks, ABEJA, and emerging players

## Major Players Tracked

| Company | AI Focus Area |
|---------|---------------|
| **Preferred Networks** | Deep learning, robotics, drug discovery |
| **NTT** | Tsuzumi LLM, enterprise AI |
| **Fujitsu** | Kozuchi platform, quantum-inspired AI |
| **NEC** | Cotomi LLM, biometrics, smart cities |
| **Hitachi** | Lumada IoT/AI platform |
| **FANUC** | Factory AI, CNC, robotics |
| **Sony** | Computer vision, gaming AI, Aibo |
| **Toyota** | Woven City, autonomous driving |

## Usage

```bash
# Run Japan AI market scouting
python launch_techscout.py --template ai_ml --model claude-3-5-sonnet-20241022
```

## Files

- `prompt.json` - Japan-focused system prompt with region_focus: japan
- `seed_queries.json` - 20 Japan-specific search queries
- `existing_technologies.json` - Known Japanese AI technologies
- `organization_context.json` - Japan market entry context

## Japan Market Considerations

The template evaluates technologies based on:
- **Japan Market Fit** - Alignment with Japanese business culture
- **Enterprise Adoption** - Traction with major Japanese corporations
- **Government Alignment** - Fit with METI/MIC/Digital Agency priorities
- **Localization Depth** - Japanese language and cultural adaptation
- **Partnership Potential** - Collaboration opportunities

## Expected Outputs

- Technology landscape of Japan AI market
- Competitive analysis of Japanese AI players
- Partnership and market entry recommendations
- Regulatory and compliance considerations
