"""
Report Generation Module

This module handles the generation of comprehensive technology scouting reports,
including executive summaries, detailed analyses, and visual presentations.
"""

import json
import os
import os.path as osp
from typing import List, Dict, Optional
from datetime import datetime

from ai_scientist.llm import get_response_from_llm, extract_json_between_markers

# =============================================================================
# REPORT GENERATION PROMPTS
# =============================================================================

executive_summary_prompt = """You are a technology strategy consultant preparing an executive summary for C-suite leadership.

<scouting_results>
Domain: {domain}
Focus Areas: {focus_areas}
Technologies Discovered: {tech_count}
Date: {date}

Top Technologies:
{top_technologies}

Key Trends:
{trends}
</scouting_results>

Write a concise executive summary (300-400 words) that:
1. Highlights the most important findings
2. Identifies immediate opportunities and threats
3. Recommends top 3 priority actions
4. Notes any urgent time-sensitive opportunities

Write in a professional, direct style suitable for busy executives.

Respond with:

EXECUTIVE SUMMARY:
<SUMMARY>

HIGHLIGHTS JSON:
```json
<JSON>
```

In <JSON>, provide:
- "key_finding": Single most important finding
- "top_opportunity": Most promising opportunity
- "top_risk": Most significant risk or threat
- "recommended_actions": List of 3 priority actions
- "budget_implication": Rough estimate of investment needed (low/medium/high)
- "urgency": One of ["immediate", "near_term", "strategic"]
"""

detailed_report_prompt = """You are a technology analyst preparing a detailed scouting report.

<scouting_data>
{scouting_data}
</scouting_data>

<evaluations>
{evaluations}
</evaluations>

Generate a detailed technology scouting report in Markdown format.

The report should include:
1. Executive Summary
2. Methodology
3. Technology Landscape Overview
4. Detailed Technology Profiles (for top 5-7 technologies)
5. Trend Analysis
6. Competitive Intelligence
7. Strategic Recommendations
8. Implementation Roadmap
9. Risk Analysis
10. Appendix with Data Sources

For each technology profile, include:
- Description and key capabilities
- Maturity assessment (TRL level)
- Key players and competitive landscape
- Strategic fit analysis
- Recommended approach (build/buy/partner)
- Timeline and investment estimate

Be thorough, data-driven, and actionable in your recommendations.
"""

technology_brief_prompt = """Create a one-page technology brief for the following technology:

<technology>
{technology}
</technology>

<evaluation>
{evaluation}
</evaluation>

The brief should be suitable for sharing with business stakeholders and should include:
1. Technology Overview (2-3 sentences)
2. Key Capabilities (bullet points)
3. Current State (maturity, key players)
4. Strategic Relevance (why it matters to us)
5. Recommendation (what we should do)
6. Key Metrics (market size, adoption rate, etc.)
7. Next Steps (specific actions)

Write in clear, non-technical language where possible.
"""

comparison_table_prompt = """Create a comparison table for the following technologies:

<technologies>
{technologies}
</technologies>

<criteria>
{criteria}
</criteria>

Generate a comprehensive comparison that a decision-maker can use to compare options.
Include both quantitative scores and qualitative insights.

Format as a Markdown table with technologies as columns and criteria as rows.
Add a summary row with overall recommendations.
"""

# =============================================================================
# REPORT GENERATION FUNCTIONS
# =============================================================================

def generate_executive_summary(
    client,
    model: str,
    scouting_results: Dict,
    evaluations: Optional[List[Dict]] = None,
) -> Dict:
    """
    Generate an executive summary from scouting results.
    
    Args:
        client: LLM client
        model: LLM model name
        scouting_results: Results from scout_technologies
        evaluations: Optional evaluation results
    
    Returns:
        Executive summary dictionary with text and highlights
    """
    technologies = scouting_results.get("technologies", [])
    trends = scouting_results.get("trend_insights", {})
    
    # Get top technologies (by potential_impact * strategic_relevance)
    top_techs = sorted(
        technologies,
        key=lambda x: x.get("potential_impact", 0) * x.get("strategic_relevance", 0),
        reverse=True
    )[:5]
    
    text, _ = get_response_from_llm(
        executive_summary_prompt.format(
            domain=scouting_results.get("domain", "Technology"),
            focus_areas=", ".join(scouting_results.get("focus_areas", [])),
            tech_count=len(technologies),
            date=scouting_results.get("scouting_date", datetime.now().isoformat()),
            top_technologies=json.dumps(top_techs, indent=2),
            trends=json.dumps(trends, indent=2),
        ),
        client=client,
        model=model,
        system_message="You are a senior technology strategy consultant preparing materials for executive leadership.",
        msg_history=[],
    )
    
    # Extract the summary text (everything between EXECUTIVE SUMMARY: and HIGHLIGHTS JSON:)
    summary_text = ""
    if "EXECUTIVE SUMMARY:" in text:
        start = text.find("EXECUTIVE SUMMARY:") + len("EXECUTIVE SUMMARY:")
        end = text.find("HIGHLIGHTS JSON:") if "HIGHLIGHTS JSON:" in text else len(text)
        summary_text = text[start:end].strip()
    
    highlights = extract_json_between_markers(text) or {}
    
    return {
        "summary_text": summary_text,
        "highlights": highlights,
        "generated_date": datetime.now().isoformat(),
    }


def generate_technology_brief(
    client,
    model: str,
    technology: Dict,
    evaluation: Optional[Dict] = None,
) -> str:
    """
    Generate a one-page technology brief.
    
    Args:
        client: LLM client
        model: LLM model name
        technology: Technology dictionary
        evaluation: Optional evaluation results
    
    Returns:
        Markdown formatted technology brief
    """
    text, _ = get_response_from_llm(
        technology_brief_prompt.format(
            technology=json.dumps(technology, indent=2),
            evaluation=json.dumps(evaluation, indent=2) if evaluation else "No evaluation available",
        ),
        client=client,
        model=model,
        system_message="You are a technology analyst creating accessible briefing documents.",
        msg_history=[],
    )
    
    return text


def generate_comparison_table(
    client,
    model: str,
    technologies: List[Dict],
    criteria: List[str],
) -> str:
    """
    Generate a comparison table for multiple technologies.
    
    Args:
        client: LLM client
        model: LLM model name
        technologies: List of technology dictionaries
        criteria: List of comparison criteria
    
    Returns:
        Markdown formatted comparison table
    """
    text, _ = get_response_from_llm(
        comparison_table_prompt.format(
            technologies=json.dumps(technologies, indent=2),
            criteria=json.dumps(criteria, indent=2),
        ),
        client=client,
        model=model,
        system_message="You are a technology analyst creating decision-support materials.",
        msg_history=[],
    )
    
    return text


def generate_scouting_report(
    base_dir: str,
    client,
    model: str,
    scouting_results: Dict,
    evaluations: Optional[List[Dict]] = None,
    output_format: str = "markdown",
) -> str:
    """
    Generate a comprehensive technology scouting report.
    
    Args:
        base_dir: Directory to save the report
        client: LLM client
        model: LLM model name
        scouting_results: Results from scout_technologies
        evaluations: Optional list of evaluation results
        output_format: Output format ("markdown", "html", "json")
    
    Returns:
        Path to the generated report
    """
    print("Generating comprehensive scouting report...")
    
    # Generate executive summary first
    print("  Generating executive summary...")
    exec_summary = generate_executive_summary(client, model, scouting_results, evaluations)
    
    # Generate the detailed report
    print("  Generating detailed analysis...")
    text, _ = get_response_from_llm(
        detailed_report_prompt.format(
            scouting_data=json.dumps(scouting_results, indent=2),
            evaluations=json.dumps(evaluations, indent=2) if evaluations else "No evaluations available",
        ),
        client=client,
        model=model,
        system_message="You are a senior technology analyst preparing comprehensive scouting reports.",
        msg_history=[],
    )
    
    # Build the final report
    report_content = build_report(
        scouting_results=scouting_results,
        exec_summary=exec_summary,
        detailed_analysis=text,
        evaluations=evaluations,
        output_format=output_format,
    )
    
    # Save the report
    os.makedirs(base_dir, exist_ok=True)
    
    if output_format == "markdown":
        report_file = osp.join(base_dir, "scouting_report.md")
    elif output_format == "html":
        report_file = osp.join(base_dir, "scouting_report.html")
    else:
        report_file = osp.join(base_dir, "scouting_report.json")
    
    with open(report_file, "w") as f:
        if output_format == "json":
            json.dump(report_content, f, indent=2)
        else:
            f.write(report_content)
    
    print(f"Report saved to: {report_file}")
    
    # Also save executive summary separately
    exec_summary_file = osp.join(base_dir, "executive_summary.md")
    with open(exec_summary_file, "w") as f:
        f.write(f"# Executive Summary\n\n{exec_summary['summary_text']}\n\n")
        f.write("## Key Highlights\n\n")
        for key, value in exec_summary.get("highlights", {}).items():
            f.write(f"**{key.replace('_', ' ').title()}:** {value}\n\n")
    
    print(f"Executive summary saved to: {exec_summary_file}")
    
    return report_file


def build_report(
    scouting_results: Dict,
    exec_summary: Dict,
    detailed_analysis: str,
    evaluations: Optional[List[Dict]] = None,
    output_format: str = "markdown",
) -> str:
    """
    Build the final report from components.
    """
    if output_format == "json":
        return {
            "title": f"Technology Scouting Report: {scouting_results.get('domain', 'Technology')}",
            "date": datetime.now().isoformat(),
            "executive_summary": exec_summary,
            "scouting_results": scouting_results,
            "detailed_analysis": detailed_analysis,
            "evaluations": evaluations,
        }
    
    # Markdown format
    report = f"""# Technology Scouting Report
## {scouting_results.get('domain', 'Technology')}

**Report Date:** {datetime.now().strftime('%B %d, %Y')}  
**Focus Areas:** {', '.join(scouting_results.get('focus_areas', []))}  
**Technologies Identified:** {len(scouting_results.get('technologies', []))}

---

# Executive Summary

{exec_summary.get('summary_text', 'No summary available.')}

## Key Highlights

"""
    
    highlights = exec_summary.get("highlights", {})
    for key, value in highlights.items():
        report += f"- **{key.replace('_', ' ').title()}:** {value}\n"
    
    report += f"""
---

# Detailed Analysis

{detailed_analysis}

---

# Data Sources

- **Academic Papers:** {scouting_results.get('data_sources', {}).get('papers_count', 0)} sources analyzed
- **Patents:** {scouting_results.get('data_sources', {}).get('patents_count', 0)} patents reviewed
- **News Articles:** {scouting_results.get('data_sources', {}).get('news_count', 0)} articles analyzed

---

# Appendix: Discovered Technologies

"""
    
    for tech in scouting_results.get('technologies', []):
        report += f"""
## {tech.get('title', tech.get('name', 'Unknown'))}

**Maturity:** {tech.get('maturity_estimate', 'Unknown')}  
**Potential Impact:** {tech.get('potential_impact', 'N/A')}/10  
**Strategic Relevance:** {tech.get('strategic_relevance', 'N/A')}/10

{tech.get('description', 'No description available.')}

**Key Capabilities:**
"""
        for cap in tech.get('key_capabilities', []):
            report += f"- {cap}\n"
        
        report += f"\n**Key Players:** {', '.join(tech.get('key_players', ['Unknown']))}\n"
        report += "\n---\n"
    
    if output_format == "html":
        # Convert markdown to basic HTML
        report = markdown_to_html(report)
    
    return report


def markdown_to_html(markdown_text: str) -> str:
    """
    Basic markdown to HTML conversion.
    For production, use a proper library like markdown or markdown2.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Technology Scouting Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        h3 {{ color: #7f8c8d; }}
        hr {{ border: none; border-top: 1px solid #ecf0f1; margin: 30px 0; }}
        strong {{ color: #2c3e50; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 5px; }}
        .highlight {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
    </style>
</head>
<body>
"""
    
    # Basic conversion
    lines = markdown_text.split('\n')
    in_list = False
    
    for line in lines:
        if line.startswith('# '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith('- '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            html += f"<li>{line[2:]}</li>\n"
        elif line.startswith('---'):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += "<hr>\n"
        elif line.strip():
            if in_list:
                html += "</ul>\n"
                in_list = False
            # Handle bold text
            line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            while '**' in line:
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            html += f"<p>{line}</p>\n"
    
    if in_list:
        html += "</ul>\n"
    
    html += """
</body>
</html>
"""
    return html


def generate_presentation_outline(
    client,
    model: str,
    scouting_results: Dict,
    audience: str = "executive",
    time_minutes: int = 15,
) -> str:
    """
    Generate a presentation outline for different audiences.
    
    Args:
        client: LLM client
        model: LLM model name
        scouting_results: Results from scouting
        audience: Target audience ("executive", "technical", "board")
        time_minutes: Presentation length
    
    Returns:
        Presentation outline in markdown
    """
    prompt = f"""Create a {time_minutes}-minute presentation outline for a {audience} audience based on these technology scouting results:

<scouting_results>
{json.dumps(scouting_results, indent=2)}
</scouting_results>

The presentation should:
1. Be appropriate for the audience level
2. Fit within the time constraint
3. Include key talking points for each slide
4. Highlight actionable recommendations
5. Include suggested visuals/charts

Format as a markdown outline with slide titles and bullet points.
"""
    
    text, _ = get_response_from_llm(
        prompt,
        client=client,
        model=model,
        system_message=f"You are creating presentation materials for a {audience} audience.",
        msg_history=[],
    )
    
    return text


if __name__ == "__main__":
    print("Report Generation Module")
    print("Use generate_scouting_report() to create comprehensive reports.")
