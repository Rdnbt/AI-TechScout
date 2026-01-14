"""
AI-TechScout: AI-powered Technology Scouting System

This module provides tools for automated technology scouting, including:
- Technology discovery from academic papers, patents, and news
- Technology evaluation and maturity assessment
- Strategic fit analysis
- Comprehensive report generation
"""

from tech_scout.scout_technologies import (
    scout_technologies,
    search_papers,
    search_patents,
    search_news,
)
from tech_scout.evaluate_technologies import (
    evaluate_technology,
    assess_maturity,
    analyze_competitive_landscape,
)
from tech_scout.generate_report import (
    generate_scouting_report,
    generate_executive_summary,
)

__version__ = "0.1.0"
__all__ = [
    "scout_technologies",
    "search_papers",
    "search_patents", 
    "search_news",
    "evaluate_technology",
    "assess_maturity",
    "analyze_competitive_landscape",
    "generate_scouting_report",
    "generate_executive_summary",
]
