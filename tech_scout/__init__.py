"""
AI-TechScout: AI-powered Technology Scouting System

This module provides tools for automated technology scouting, including:
- Technology discovery from academic papers, patents, and news
- Technology evaluation and maturity assessment
- Strategic fit analysis
- Comprehensive report generation
"""

from tech_scout.llm import (
    create_client,
    get_response_from_llm,
    extract_json_between_markers,
    AVAILABLE_LLMS,
)
from tech_scout.scout_technologies import (
    scout_technologies,
    search_papers,
    search_patents,
    search_news,
    generate_search_queries,
)
from tech_scout.evaluate_technologies import (
    evaluate_technology,
    assess_maturity,
    analyze_competitive_landscape,
    batch_evaluate_technologies,
)
from tech_scout.generate_report import (
    generate_scouting_report,
    generate_executive_summary,
    generate_technology_brief,
)

__version__ = "0.1.0"
__all__ = [
    # LLM utilities
    "create_client",
    "get_response_from_llm",
    "extract_json_between_markers",
    "AVAILABLE_LLMS",
    # Scouting
    "scout_technologies",
    "search_papers",
    "search_patents", 
    "search_news",
    "generate_search_queries",
    # Evaluation
    "evaluate_technology",
    "assess_maturity",
    "analyze_competitive_landscape",
    "batch_evaluate_technologies",
    # Reporting
    "generate_scouting_report",
    "generate_executive_summary",
    "generate_technology_brief",
]
