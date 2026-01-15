# Japan Materials Technology Scouting Template

This template is designed for scouting **advanced materials technologies** with a focus on **Japanese companies, research institutions, and market dynamics**.

## 🇯🇵 Japan Focus

This template automatically enables Japan-specific data sources:

### Data Sources Used
| Source | Type | Coverage |
|--------|------|----------|
| **OpenAlex** | Academic papers | Global |
| **J-STAGE** | Academic papers | Japan-specific (JST database) |
| **Google Patents** | Patents | Global + JP priority |
| **Google News Japan** | News | Japan locale + English |

### Major Japanese Materials Companies Tracked
- **Toray Industries** - Carbon fiber, films, advanced composites
- **Teijin Limited** - Carbon fiber, aramid, healthcare materials
- **Shin-Etsu Chemical** - Silicon wafers, PVC, silicones
- **AGC Inc** - Glass, chemicals, electronics materials
- **Nitto Denko** - Optical films, tapes, membranes
- **Sumitomo Chemical** - Petrochemicals, battery materials
- **Mitsui Chemicals** - Performance polymers, healthcare
- **Kuraray** - Specialty chemicals, barrier materials
- **TDK Corporation** - Electronic materials, magnetics
- **Resonac (Showa Denko)** - Specialty chemicals, SiC

### Research Institutions Monitored
- NIMS (National Institute for Materials Science)
- AIST (National Institute of Advanced Industrial Science and Technology)
- RIKEN
- University of Tokyo
- Tohoku University (materials science center)
- Kyoto University

## Usage

```bash
python launch_techscout.py --template materials_japan --model claude-3-5-sonnet-20241022
```

## Configuration Files

- `prompt.json` - System prompt emphasizing Japan expertise
- `seed_queries.json` - 20 Japan-focused search queries
- `existing_technologies.json` - Known Japanese materials technologies
- `organization_context.json` - Japan market strategic context

## Output

The scouting report will include:
- Technologies from Japanese companies
- Papers from J-STAGE and global sources
- Japan-specific market intelligence
- Strategic recommendations for Japan market entry/partnership

## API Keys (Optional but Recommended)

For best results with Japan scouting:

```env
# Optional: J-STAGE affiliate ID for better rate limits
JSTAGE_AFFILIATE_ID=your-affiliate-id

# Optional: SerpAPI for patent search (includes JP patents)
SERPAPI_KEY=your-serpapi-key
```

## Notes

- Searches include both English and Japanese contexts
- Results tagged with `region: Japan` where applicable
- Company names searched in both Japanese and English variants
