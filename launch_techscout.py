#!/usr/bin/env python3
"""
AI-TechScout: Automated Technology Scouting System

This script launches the technology scouting pipeline, which:
1. Discovers emerging technologies from academic papers, patents, and news
2. Evaluates technologies for maturity, strategic fit, and competitive landscape
3. Generates comprehensive reports with actionable recommendations

Usage:
    python launch_techscout.py --domain "AI/ML" --template templates/tech_scout/ai_ml
    python launch_techscout.py --config config.json
"""

import argparse
import json
import os
import os.path as osp
import sys
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from tech_scout.llm import create_client, AVAILABLE_LLMS
from tech_scout.scout_technologies import scout_technologies, generate_search_queries
from tech_scout.evaluate_technologies import batch_evaluate_technologies
from tech_scout.generate_report import generate_scouting_report


def print_banner():
    """Print the AI-TechScout banner."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     █████╗ ██╗    ████████╗███████╗ ██████╗██╗  ██╗               ║
║    ██╔══██╗██║    ╚══██╔══╝██╔════╝██╔════╝██║  ██║               ║
║    ███████║██║       ██║   █████╗  ██║     ███████║               ║
║    ██╔══██║██║       ██║   ██╔══╝  ██║     ██╔══██║               ║
║    ██║  ██║██║       ██║   ███████╗╚██████╗██║  ██║               ║
║    ╚═╝  ╚═╝╚═╝       ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝               ║
║                                                                   ║
║    ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗                    ║
║    ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝                    ║
║    ███████╗██║     ██║   ██║██║   ██║   ██║                       ║
║    ╚════██║██║     ██║   ██║██║   ██║   ██║                       ║
║    ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║                       ║
║    ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝                       ║
║                                                                   ║
║         AI-Powered Technology Scouting & Analysis                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)


def print_time():
    """Print current timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-TechScout: Automated Technology Scouting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scout AI/ML technologies using a predefined template
  python launch_techscout.py --template templates/tech_scout/ai_ml

  # Scout a custom domain with specific focus areas
  python launch_techscout.py --domain "Biotechnology" --focus "Gene Therapy,CRISPR,mRNA"

  # Use a configuration file
  python launch_techscout.py --config my_scouting_config.json

  # Scout and evaluate with a specific model
  python launch_techscout.py --template templates/tech_scout/cleantech --model gpt-4o
        """
    )
    
    # Scouting configuration
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="Path to a scouting template directory containing prompt.json and seed configuration.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a JSON configuration file with all scouting parameters.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="Emerging Technologies",
        help="Technology domain to scout (e.g., 'AI/ML', 'Biotechnology', 'CleanTech').",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="Comma-separated list of focus areas within the domain.",
    )
    parser.add_argument(
        "--queries",
        type=str,
        default=None,
        help="Comma-separated list of search queries. If not provided, queries will be auto-generated.",
    )
    
    # Output configuration
    parser.add_argument(
        "--output",
        type=str,
        default="./scouting_results",
        help="Output directory for scouting results and reports.",
    )
    parser.add_argument(
        "--report-format",
        type=str,
        default="markdown",
        choices=["markdown", "html", "json"],
        help="Output format for the scouting report.",
    )
    
    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default="claude-3-5-sonnet-20241022",
        choices=AVAILABLE_LLMS,
        help="LLM model to use for analysis.",
    )
    
    # Execution options
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip data collection and use cached results.",
    )
    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip technology evaluation step.",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip report generation step.",
    )
    parser.add_argument(
        "--num-reflections",
        type=int,
        default=3,
        help="Number of refinement iterations for LLM analysis.",
    )
    parser.add_argument(
        "--year-lookback",
        type=int,
        default=3,
        help="Number of years to look back for papers and patents.",
    )
    
    # Organization context
    parser.add_argument(
        "--org-context",
        type=str,
        default=None,
        help="Path to organization context JSON file for strategic fit analysis.",
    )
    
    # Verbosity
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    
    return parser.parse_args()


def load_config(args):
    """Load configuration from file or command line arguments."""
    config = {
        "domain": args.domain,
        "focus_areas": [],
        "search_queries": [],
        "output_dir": args.output,
        "report_format": args.report_format,
        "model": args.model,
        "skip_search": args.skip_search,
        "skip_evaluation": args.skip_evaluation,
        "skip_report": args.skip_report,
        "num_reflections": args.num_reflections,
        "year_lookback": args.year_lookback,
        "organization_context": None,
    }
    
    # Load from config file if provided
    if args.config:
        print(f"Loading configuration from: {args.config}")
        with open(args.config, "r") as f:
            file_config = json.load(f)
        config.update(file_config)
    
    # Load from template if provided
    if args.template:
        print(f"Loading template from: {args.template}")
        template_dir = args.template
        
        # Load prompt.json
        prompt_file = osp.join(template_dir, "prompt.json")
        if osp.exists(prompt_file):
            with open(prompt_file, "r") as f:
                prompt_config = json.load(f)
            config["domain"] = prompt_config.get("domain", config["domain"])
            config["focus_areas"] = prompt_config.get("focus_areas", config["focus_areas"])
            config["system_prompt"] = prompt_config.get("system", None)
        
        # Load seed_queries.json
        queries_file = osp.join(template_dir, "seed_queries.json")
        if osp.exists(queries_file):
            with open(queries_file, "r") as f:
                config["search_queries"] = json.load(f)
        
        # Load organization_context.json
        org_file = osp.join(template_dir, "organization_context.json")
        if osp.exists(org_file):
            with open(org_file, "r") as f:
                config["organization_context"] = json.load(f)
        
        # Load existing_technologies.json
        existing_file = osp.join(template_dir, "existing_technologies.json")
        if osp.exists(existing_file):
            with open(existing_file, "r") as f:
                config["existing_technologies"] = json.load(f)
    
    # Override with command line arguments
    if args.focus:
        config["focus_areas"] = [f.strip() for f in args.focus.split(",")]
    
    if args.queries:
        config["search_queries"] = [q.strip() for q in args.queries.split(",")]
    
    if args.org_context:
        with open(args.org_context, "r") as f:
            config["organization_context"] = json.load(f)
    
    return config


def validate_config(config):
    """Validate the configuration and set defaults."""
    if not config.get("focus_areas"):
        print("Warning: No focus areas specified. Using default focus areas for the domain.")
        # Set default focus areas based on domain
        domain_defaults = {
            "AI/ML": ["Machine Learning", "Natural Language Processing", "Computer Vision", "Robotics"],
            "Biotechnology": ["Gene Therapy", "Drug Discovery", "Diagnostics", "Synthetic Biology"],
            "CleanTech": ["Renewable Energy", "Energy Storage", "Carbon Capture", "Sustainable Materials"],
            "FinTech": ["Blockchain", "Digital Payments", "InsurTech", "RegTech"],
        }
        config["focus_areas"] = domain_defaults.get(
            config["domain"], 
            ["Innovation", "Emerging Technology", "Digital Transformation"]
        )
    
    return config


def run_scouting_pipeline(config, client, model):
    """
    Run the complete technology scouting pipeline.
    
    Steps:
    1. Generate search queries (if not provided)
    2. Scout for technologies
    3. Evaluate discovered technologies
    4. Generate comprehensive report
    """
    output_dir = config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("PHASE 1: TECHNOLOGY DISCOVERY")
    print("="*60)
    print_time()
    
    # Generate search queries if not provided
    search_queries = config.get("search_queries", [])
    if not search_queries:
        print("\nGenerating search queries...")
        search_queries = generate_search_queries(
            client=client,
            model=model,
            domain=config["domain"],
            focus_areas=config["focus_areas"],
            num_queries=15,
        )
        print(f"Generated {len(search_queries)} search queries")
        
        # Save queries for reference
        with open(osp.join(output_dir, "search_queries.json"), "w") as f:
            json.dump(search_queries, f, indent=2)
    
    # Scout for technologies
    print(f"\nScouting for technologies in domain: {config['domain']}")
    print(f"Focus areas: {', '.join(config['focus_areas'])}")
    
    scouting_results = scout_technologies(
        base_dir=output_dir,
        client=client,
        model=model,
        domain=config["domain"],
        focus_areas=config["focus_areas"],
        search_queries=search_queries,
        skip_search=config.get("skip_search", False),
        num_reflections=config.get("num_reflections", 3),
        year_lookback=config.get("year_lookback", 3),
    )
    
    technologies = scouting_results.get("technologies", [])
    print(f"\nDiscovered {len(technologies)} technologies")
    
    # Phase 2: Evaluation
    evaluations = None
    if not config.get("skip_evaluation", False) and technologies:
        print("\n" + "="*60)
        print("PHASE 2: TECHNOLOGY EVALUATION")
        print("="*60)
        print_time()
        
        evaluation_results = batch_evaluate_technologies(
            base_dir=output_dir,
            client=client,
            model=model,
            technologies=technologies,
            organization_context=config.get("organization_context"),
        )
        evaluations = evaluation_results.get("individual_evaluations", [])
        print(f"\nCompleted evaluation of {len(evaluations)} technologies")
    
    # Phase 3: Report Generation
    if not config.get("skip_report", False):
        print("\n" + "="*60)
        print("PHASE 3: REPORT GENERATION")
        print("="*60)
        print_time()
        
        report_path = generate_scouting_report(
            base_dir=output_dir,
            client=client,
            model=model,
            scouting_results=scouting_results,
            evaluations=evaluations,
            output_format=config.get("report_format", "markdown"),
        )
        print(f"\nReport generated: {report_path}")
    
    # Summary
    print("\n" + "="*60)
    print("SCOUTING COMPLETE")
    print("="*60)
    print_time()
    print(f"\nResults saved to: {output_dir}")
    print(f"Technologies discovered: {len(technologies)}")
    
    if technologies:
        print("\nTop 5 Technologies by Strategic Relevance:")
        top_techs = sorted(
            technologies,
            key=lambda x: x.get("strategic_relevance", 0),
            reverse=True
        )[:5]
        for i, tech in enumerate(top_techs, 1):
            print(f"  {i}. {tech.get('title', tech.get('name', 'Unknown'))} "
                  f"(Relevance: {tech.get('strategic_relevance', 'N/A')}/10)")
    
    return scouting_results, evaluations


def main():
    """Main entry point."""
    print_banner()
    args = parse_arguments()
    
    # Load and validate configuration
    config = load_config(args)
    config = validate_config(config)
    
    if args.verbose:
        print("\nConfiguration:")
        print(json.dumps({k: v for k, v in config.items() if k != "organization_context"}, indent=2))
    
    # Create LLM client
    print(f"\nInitializing LLM client with model: {config['model']}")
    client, client_model = create_client(config["model"])
    
    # Run the scouting pipeline
    try:
        results, evaluations = run_scouting_pipeline(config, client, client_model)
        return 0
    except KeyboardInterrupt:
        print("\n\nScouting interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nError during scouting: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
