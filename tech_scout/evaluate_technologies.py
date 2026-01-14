"""
Technology Evaluation Module

This module handles the evaluation and assessment of discovered technologies,
including maturity assessment, strategic fit analysis, and competitive landscape analysis.
"""

import json
import os
import os.path as osp
from typing import List, Dict, Optional
from datetime import datetime

from ai_scientist.llm import get_response_from_llm, extract_json_between_markers

# =============================================================================
# EVALUATION PROMPTS
# =============================================================================

maturity_assessment_prompt = """You are a technology maturity analyst. Assess the maturity of the following technology using the Technology Readiness Level (TRL) framework:

<technology>
{technology}
</technology>

<evidence>
Papers: {papers_count} academic papers found
Patents: {patents_count} patents filed
News: {news_count} news articles
Key Players: {key_players}
</evidence>

Provide a detailed maturity assessment.

Respond in the following format:

ASSESSMENT:
<ASSESSMENT>

MATURITY JSON:
```json
<JSON>
```

In <JSON>, provide:
- "trl_level": Technology Readiness Level (1-9)
- "trl_description": Description of the TRL level
- "maturity_stage": One of ["basic_research", "applied_research", "development", "demonstration", "commercialization", "market_ready"]
- "evidence_strength": Rating 1-10 for how strong the evidence is
- "key_milestones_achieved": List of milestones the technology has achieved
- "remaining_challenges": List of challenges before wider adoption
- "estimated_years_to_market": Estimate years until market ready (0 if already there)
- "confidence": Rating 1-10 for confidence in this assessment
- "rationale": Brief explanation of the assessment
"""

strategic_fit_prompt = """You are a strategic technology analyst. Evaluate how well the following technology fits with an organization's strategic objectives.

<technology>
{technology}
</technology>

<organization_context>
Industry: {industry}
Current Capabilities: {current_capabilities}
Strategic Priorities: {strategic_priorities}
Risk Tolerance: {risk_tolerance}
Investment Horizon: {investment_horizon}
</organization_context>

Evaluate the strategic fit of this technology.

Respond in the following format:

ANALYSIS:
<ANALYSIS>

FIT JSON:
```json
<JSON>
```

In <JSON>, provide:
- "overall_fit_score": Rating 1-10
- "alignment_with_priorities": Dict mapping each priority to a score (1-10)
- "capability_gaps": List of capabilities the org would need to develop
- "build_vs_buy_recommendation": One of ["build_internal", "partner", "acquire", "license", "avoid"]
- "investment_type": One of ["strategic", "exploratory", "defensive", "opportunistic"]
- "recommended_investment_level": One of ["significant", "moderate", "minimal", "none"]
- "key_risks": List of main risks of pursuing this technology
- "key_opportunities": List of main opportunities
- "competitive_advantage_potential": Rating 1-10
- "time_sensitivity": One of ["urgent", "important", "can_wait", "not_time_sensitive"]
- "recommended_actions": List of specific recommended actions
"""

competitive_landscape_prompt = """You are a competitive intelligence analyst. Analyze the competitive landscape for the following technology:

<technology>
{technology}
</technology>

<market_data>
Key Players: {key_players}
Recent Patents by Company: {patent_data}
Academic Leaders: {academic_leaders}
Recent Funding/M&A: {funding_data}
</market_data>

Analyze the competitive landscape.

Respond in the following format:

ANALYSIS:
<ANALYSIS>

LANDSCAPE JSON:
```json
<JSON>
```

In <JSON>, provide:
- "market_leaders": List of top 3-5 companies with brief descriptions
- "emerging_challengers": List of startups or new entrants to watch
- "academic_hubs": Top universities/research institutions
- "geographic_concentration": Where is development concentrated
- "ip_landscape": Assessment of patent landscape (open, fragmented, consolidated)
- "barriers_to_entry": List of main barriers
- "partnership_opportunities": Potential partners to consider
- "acquisition_targets": Potential acquisition targets
- "competitive_intensity": Rating 1-10
- "market_timing": One of ["early", "growth", "mature", "declining"]
- "white_space_opportunities": Areas not well covered by competitors
"""

technology_comparison_prompt = """You are a technology analyst. Compare the following technologies for strategic decision making:

<technologies>
{technologies}
</technologies>

<evaluation_criteria>
{criteria}
</evaluation_criteria>

Provide a comparative analysis.

Respond in the following format:

COMPARISON:
<COMPARISON>

RANKING JSON:
```json
<JSON>
```

In <JSON>, provide:
- "rankings": List of technologies ranked by overall score, each with:
  - "name": Technology name
  - "overall_score": Weighted score 1-100
  - "scores_by_criteria": Dict mapping each criterion to score
  - "key_strengths": Top 2-3 strengths
  - "key_weaknesses": Top 2-3 weaknesses
- "recommended_portfolio": List of technologies to pursue (can be multiple)
- "prioritization_rationale": Explanation of the prioritization
- "resource_allocation_suggestion": How to allocate resources across top picks
"""

# =============================================================================
# EVALUATION FUNCTIONS
# =============================================================================

def assess_maturity(
    client,
    model: str,
    technology: Dict,
    evidence: Optional[Dict] = None,
) -> Dict:
    """
    Assess the maturity level of a technology using TRL framework.
    
    Args:
        client: LLM client
        model: LLM model name
        technology: Technology dictionary with name, description, etc.
        evidence: Optional evidence data (paper counts, patents, etc.)
    
    Returns:
        Maturity assessment dictionary
    """
    if evidence is None:
        evidence = {
            "papers_count": 0,
            "patents_count": 0,
            "news_count": 0,
            "key_players": [],
        }
    
    text, _ = get_response_from_llm(
        maturity_assessment_prompt.format(
            technology=json.dumps(technology, indent=2),
            papers_count=evidence.get("papers_count", 0),
            patents_count=evidence.get("patents_count", 0),
            news_count=evidence.get("news_count", 0),
            key_players=", ".join(evidence.get("key_players", [])),
        ),
        client=client,
        model=model,
        system_message="You are an expert at assessing technology maturity and readiness levels.",
        msg_history=[],
    )
    
    return extract_json_between_markers(text)


def evaluate_strategic_fit(
    client,
    model: str,
    technology: Dict,
    organization_context: Dict,
) -> Dict:
    """
    Evaluate how well a technology fits with an organization's strategy.
    
    Args:
        client: LLM client
        model: LLM model name
        technology: Technology dictionary
        organization_context: Dict with industry, capabilities, priorities, etc.
    
    Returns:
        Strategic fit assessment dictionary
    """
    text, _ = get_response_from_llm(
        strategic_fit_prompt.format(
            technology=json.dumps(technology, indent=2),
            industry=organization_context.get("industry", "Not specified"),
            current_capabilities=json.dumps(organization_context.get("current_capabilities", [])),
            strategic_priorities=json.dumps(organization_context.get("strategic_priorities", [])),
            risk_tolerance=organization_context.get("risk_tolerance", "moderate"),
            investment_horizon=organization_context.get("investment_horizon", "3-5 years"),
        ),
        client=client,
        model=model,
        system_message="You are a strategic technology advisor helping organizations make technology investment decisions.",
        msg_history=[],
    )
    
    return extract_json_between_markers(text)


def analyze_competitive_landscape(
    client,
    model: str,
    technology: Dict,
    market_data: Optional[Dict] = None,
) -> Dict:
    """
    Analyze the competitive landscape for a technology.
    
    Args:
        client: LLM client
        model: LLM model name
        technology: Technology dictionary
        market_data: Optional market intelligence data
    
    Returns:
        Competitive landscape analysis dictionary
    """
    if market_data is None:
        market_data = {
            "key_players": technology.get("key_players", []),
            "patent_data": {},
            "academic_leaders": [],
            "funding_data": [],
        }
    
    text, _ = get_response_from_llm(
        competitive_landscape_prompt.format(
            technology=json.dumps(technology, indent=2),
            key_players=json.dumps(market_data.get("key_players", [])),
            patent_data=json.dumps(market_data.get("patent_data", {})),
            academic_leaders=json.dumps(market_data.get("academic_leaders", [])),
            funding_data=json.dumps(market_data.get("funding_data", [])),
        ),
        client=client,
        model=model,
        system_message="You are a competitive intelligence analyst specializing in emerging technologies.",
        msg_history=[],
    )
    
    return extract_json_between_markers(text)


def compare_technologies(
    client,
    model: str,
    technologies: List[Dict],
    evaluation_criteria: List[Dict],
) -> Dict:
    """
    Compare multiple technologies against evaluation criteria.
    
    Args:
        client: LLM client
        model: LLM model name
        technologies: List of technology dictionaries
        evaluation_criteria: List of criteria with names and weights
    
    Returns:
        Comparison and ranking dictionary
    """
    text, _ = get_response_from_llm(
        technology_comparison_prompt.format(
            technologies=json.dumps(technologies, indent=2),
            criteria=json.dumps(evaluation_criteria, indent=2),
        ),
        client=client,
        model=model,
        system_message="You are a technology portfolio analyst helping organizations prioritize technology investments.",
        msg_history=[],
    )
    
    return extract_json_between_markers(text)


def evaluate_technology(
    base_dir: str,
    client,
    model: str,
    technology: Dict,
    organization_context: Optional[Dict] = None,
    save_results: bool = True,
) -> Dict:
    """
    Comprehensive evaluation of a single technology.
    
    Args:
        base_dir: Directory to save results
        client: LLM client
        model: LLM model name
        technology: Technology dictionary to evaluate
        organization_context: Organization context for strategic fit
        save_results: Whether to save results to file
    
    Returns:
        Complete evaluation dictionary
    """
    print(f"Evaluating technology: {technology.get('name', 'Unknown')}")
    
    # Default organization context
    if organization_context is None:
        org_context_file = osp.join(base_dir, "organization_context.json")
        if osp.exists(org_context_file):
            with open(org_context_file, "r") as f:
                organization_context = json.load(f)
        else:
            organization_context = {
                "industry": "Technology",
                "current_capabilities": [],
                "strategic_priorities": ["Innovation", "Growth", "Efficiency"],
                "risk_tolerance": "moderate",
                "investment_horizon": "3-5 years",
            }
    
    # Collect evidence
    evidence = {
        "papers_count": len(technology.get("key_references", [])),
        "patents_count": 0,
        "news_count": 0,
        "key_players": technology.get("key_players", []),
    }
    
    # Run all evaluations
    print("  Assessing maturity...")
    maturity = assess_maturity(client, model, technology, evidence)
    
    print("  Evaluating strategic fit...")
    strategic_fit = evaluate_strategic_fit(client, model, technology, organization_context)
    
    print("  Analyzing competitive landscape...")
    competitive = analyze_competitive_landscape(client, model, technology)
    
    # Compile evaluation
    evaluation = {
        "technology": technology,
        "evaluation_date": datetime.now().isoformat(),
        "maturity_assessment": maturity,
        "strategic_fit": strategic_fit,
        "competitive_landscape": competitive,
        "overall_recommendation": generate_recommendation(maturity, strategic_fit, competitive),
    }
    
    # Save if requested
    if save_results:
        os.makedirs(base_dir, exist_ok=True)
        tech_name = technology.get("name", "unknown").replace(" ", "_")
        eval_file = osp.join(base_dir, f"evaluation_{tech_name}.json")
        with open(eval_file, "w") as f:
            json.dump(evaluation, f, indent=2)
        print(f"  Evaluation saved to: {eval_file}")
    
    return evaluation


def generate_recommendation(
    maturity: Dict,
    strategic_fit: Dict,
    competitive: Dict,
) -> Dict:
    """
    Generate an overall recommendation based on all evaluations.
    """
    # Calculate overall scores
    maturity_score = maturity.get("evidence_strength", 5) if maturity else 5
    fit_score = strategic_fit.get("overall_fit_score", 5) if strategic_fit else 5
    competitive_score = 10 - competitive.get("competitive_intensity", 5) if competitive else 5
    
    overall_score = (maturity_score * 0.3 + fit_score * 0.5 + competitive_score * 0.2)
    
    # Determine recommendation
    if overall_score >= 7.5:
        action = "pursue_actively"
        priority = "high"
    elif overall_score >= 5.5:
        action = "monitor_and_pilot"
        priority = "medium"
    elif overall_score >= 3.5:
        action = "watch"
        priority = "low"
    else:
        action = "deprioritize"
        priority = "none"
    
    return {
        "overall_score": round(overall_score, 2),
        "recommended_action": action,
        "priority": priority,
        "investment_recommendation": strategic_fit.get("build_vs_buy_recommendation", "evaluate") if strategic_fit else "evaluate",
        "time_sensitivity": strategic_fit.get("time_sensitivity", "can_wait") if strategic_fit else "can_wait",
    }


def batch_evaluate_technologies(
    base_dir: str,
    client,
    model: str,
    technologies: List[Dict],
    organization_context: Optional[Dict] = None,
    evaluation_criteria: Optional[List[Dict]] = None,
) -> Dict:
    """
    Evaluate and compare multiple technologies.
    
    Args:
        base_dir: Directory to save results
        client: LLM client
        model: LLM model name
        technologies: List of technology dictionaries
        organization_context: Organization context for all evaluations
        evaluation_criteria: Criteria for comparison
    
    Returns:
        Batch evaluation with comparisons
    """
    print(f"Batch evaluating {len(technologies)} technologies...")
    
    # Default criteria
    if evaluation_criteria is None:
        evaluation_criteria = [
            {"name": "strategic_fit", "weight": 0.3, "description": "Alignment with strategic priorities"},
            {"name": "maturity", "weight": 0.2, "description": "Technology readiness level"},
            {"name": "market_potential", "weight": 0.2, "description": "Market size and growth potential"},
            {"name": "competitive_position", "weight": 0.15, "description": "Ability to achieve competitive advantage"},
            {"name": "implementation_feasibility", "weight": 0.15, "description": "Ease of implementation"},
        ]
    
    # Evaluate each technology
    evaluations = []
    for tech in technologies:
        eval_result = evaluate_technology(
            base_dir, client, model, tech, organization_context, save_results=False
        )
        evaluations.append(eval_result)
    
    # Compare technologies
    print("\nComparing technologies...")
    comparison = compare_technologies(client, model, technologies, evaluation_criteria)
    
    # Compile batch results
    batch_results = {
        "evaluation_date": datetime.now().isoformat(),
        "technologies_evaluated": len(technologies),
        "evaluation_criteria": evaluation_criteria,
        "individual_evaluations": evaluations,
        "comparison": comparison,
    }
    
    # Save results
    os.makedirs(base_dir, exist_ok=True)
    results_file = osp.join(base_dir, "batch_evaluation_results.json")
    with open(results_file, "w") as f:
        json.dump(batch_results, f, indent=2)
    
    print(f"\nBatch evaluation complete. Results saved to: {results_file}")
    
    return batch_results


if __name__ == "__main__":
    print("Technology Evaluation Module")
    print("Use evaluate_technology() or batch_evaluate_technologies() to evaluate technologies.")
