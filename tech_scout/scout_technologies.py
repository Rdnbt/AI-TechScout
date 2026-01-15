"""
Technology Scouting Module

This module handles the discovery and collection of emerging technologies
from various sources including academic papers, patents, and news.
"""

import json
import os
import os.path as osp
import time
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta

import backoff
import requests

from tech_scout.llm import get_response_from_llm, extract_json_between_markers

# API Keys from environment
S2_API_KEY = os.getenv("S2_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_NEWS_API_KEY = os.getenv("GOOGLE_NEWS_API_KEY")
JSTAGE_AFFILIATE_ID = os.getenv("JSTAGE_AFFILIATE_ID", "")  # Optional for J-STAGE

# =============================================================================
# PROMPTS FOR TECHNOLOGY SCOUTING
# =============================================================================

technology_discovery_prompt = """You are an expert technology scout analyzing emerging technologies in the domain of: {domain}

Your focus areas are:
{focus_areas}

Based on the following information sources:

<academic_papers>
{papers}
</academic_papers>

<patents>
{patents}
</patents>

<news_articles>
{news}
</news_articles>

<existing_technologies>
{existing_technologies}
</existing_technologies>

Identify and analyze the most promising emerging technologies that are NOT already in the existing technologies list.

Respond in the following format:

ANALYSIS:
<ANALYSIS>

TECHNOLOGIES JSON:
```json
<JSON>
```

In <ANALYSIS>, provide:
1. Key trends you observe across the sources
2. Technologies that appear in multiple source types (papers + patents, etc.)
3. Technologies showing rapid growth or breakthrough potential
4. Gaps in the current technology landscape

In <JSON>, provide a list of discovered technologies with the following fields:
- "name": A concise name for the technology (lowercase, underscores allowed)
- "title": A descriptive title for the technology
- "description": A 2-3 sentence description of what the technology is
- "key_capabilities": List of main capabilities or applications
- "source_types": List of source types where this was found ["paper", "patent", "news"]
- "key_players": List of companies, universities, or researchers working on this
- "maturity_estimate": One of ["emerging", "developing", "maturing", "mature"]
- "potential_impact": Rating from 1-10
- "strategic_relevance": Rating from 1-10 based on the focus areas
- "key_references": List of the most relevant source titles/identifiers
- "timeline_estimate": Estimated years until mainstream adoption

Be thorough but realistic in your assessments.
"""

technology_refinement_prompt = """Round {current_round}/{num_reflections}.

Review the technologies you identified and refine your analysis:

1. Are there any technologies that should be merged or split?
2. Are the maturity estimates accurate based on the evidence?
3. Are there any technologies you missed that appear in multiple sources?
4. Are the strategic relevance scores aligned with the focus areas?

Respond in the same format:

ANALYSIS:
<ANALYSIS>

TECHNOLOGIES JSON:
```json
<JSON>
```

If satisfied with the analysis, include "ANALYSIS COMPLETE" at the end of ANALYSIS."""

trend_analysis_prompt = """You are a technology trend analyst. Given the following technologies discovered in the {domain} domain:

<technologies>
{technologies}
</technologies>

Analyze the overarching trends and provide strategic insights.

Respond in the following format:

TREND ANALYSIS:
<ANALYSIS>

INSIGHTS JSON:
```json
<JSON>
```

In <JSON>, provide:
- "major_trends": List of 3-5 major technology trends with descriptions
- "convergence_opportunities": Technologies that could be combined for greater impact
- "disruption_risks": Technologies that could disrupt existing solutions
- "investment_priorities": Recommended priority ranking for technology investments
- "watch_list": Technologies to monitor that aren't ready for investment yet
- "recommended_actions": Specific actions for the organization
"""

# =============================================================================
# SEMANTIC SCHOLAR SEARCH
# =============================================================================

@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_tries=3
)
def search_papers(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50,
    fields_of_study: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Search for academic papers. Uses OpenAlex (free) as primary,
    falls back to Semantic Scholar if S2_API_KEY is set.
    """
    # Try OpenAlex first (free, no API key needed)
    try:
        papers = search_papers_openalex(query, year_start, year_end, limit)
        if papers:
            return papers
    except Exception as e:
        print(f"  OpenAlex search failed: {e}")
    
    # Fall back to Semantic Scholar if API key is set
    if S2_API_KEY:
        try:
            return search_papers_semantic_scholar(query, year_start, year_end, limit, fields_of_study)
        except Exception as e:
            print(f"  Semantic Scholar search failed: {e}")
    
    return []


def search_papers_semantic_scholar(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50,
    fields_of_study: Optional[List[str]] = None,
) -> List[Dict]:
    """Search using Semantic Scholar API (requires S2_API_KEY for reliable access)."""
    if year_start is None:
        year_start = datetime.now().year - 3
    if year_end is None:
        year_end = datetime.now().year
    
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": query,
        "year": f"{year_start}-{year_end}",
        "limit": min(limit, 100),
        "fields": "title,abstract,authors,year,citationCount,venue,fieldsOfStudy,publicationDate",
    }
    
    if fields_of_study:
        params["fieldsOfStudy"] = ",".join(fields_of_study)
    
    headers = {"x-api-key": S2_API_KEY} if S2_API_KEY else {}
    
    response = requests.get(base_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    papers = data.get("data", [])
    
    formatted_papers = []
    for paper in papers:
        formatted_papers.append({
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "authors": [a.get("name", "") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "citations": paper.get("citationCount", 0),
            "venue": paper.get("venue", ""),
            "fields": paper.get("fieldsOfStudy", []),
            "publication_date": paper.get("publicationDate"),
        })
    
    return formatted_papers


@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_tries=3
)
def search_papers_openalex(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50,
) -> List[Dict]:
    """
    Search for academic papers using OpenAlex API (free, no key required).
    https://docs.openalex.org/
    """
    if year_start is None:
        year_start = datetime.now().year - 3
    if year_end is None:
        year_end = datetime.now().year
    
    base_url = "https://api.openalex.org/works"
    
    # OpenAlex recommends adding email for polite pool (faster rate limits)
    headers = {"User-Agent": "AI-TechScout/1.0 (Technology Scouting Tool)"}
    
    params = {
        "search": query,
        "filter": f"publication_year:{year_start}-{year_end}",
        "per_page": min(limit, 200),
        "sort": "cited_by_count:desc",
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    papers = data.get("results", [])
    
    formatted_papers = []
    for paper in papers:
        try:
            # Convert inverted index abstract to text
            abstract = ""
            abstract_inv = paper.get("abstract_inverted_index")
            if abstract_inv and isinstance(abstract_inv, dict):
                # Reconstruct abstract from inverted index
                word_positions = []
                for word, positions in abstract_inv.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(word for _, word in word_positions)
            
            # Safely get venue with multiple null checks
            venue = ""
            primary_loc = paper.get("primary_location")
            if primary_loc and isinstance(primary_loc, dict):
                source = primary_loc.get("source")
                if source and isinstance(source, dict):
                    venue = source.get("display_name", "") or ""
            
            # Safely get authors
            authors = []
            for authorship in paper.get("authorships", []) or []:
                if authorship and isinstance(authorship, dict):
                    author = authorship.get("author")
                    if author and isinstance(author, dict):
                        name = author.get("display_name", "")
                        if name:
                            authors.append(name)
            
            formatted_papers.append({
                "title": paper.get("title", "") or "",
                "abstract": abstract,
                "authors": authors,
                "year": paper.get("publication_year"),
                "citations": paper.get("cited_by_count", 0) or 0,
                "venue": venue,
                "doi": paper.get("doi"),
                "source": "openalex",
            })
        except Exception:
            # Skip papers with malformed data
            continue
    
    return formatted_papers


# =============================================================================
# J-STAGE SEARCH (Japanese Academic Papers)
# =============================================================================

@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_tries=3
)
def search_papers_jstage(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50,
    lang: str = "en",
) -> List[Dict]:
    """
    Search for Japanese academic papers using J-STAGE API.
    J-STAGE is operated by JST (Japan Science and Technology Agency).
    
    API docs: https://www.jstage.jst.go.jp/static/pages/JstageServices/TAB3/-char/en
    Free to use, no API key required.
    
    Args:
        query: Search query (can be English or Japanese)
        year_start: Filter papers from this year
        year_end: Filter papers until this year
        limit: Maximum number of results
        lang: Language preference ("en" or "ja")
    """
    if year_start is None:
        year_start = datetime.now().year - 3
    if year_end is None:
        year_end = datetime.now().year
    
    base_url = "https://api.jstage.jst.go.jp/searchapi/do"
    
    params = {
        "service": "3",  # Full-text search
        "pubyearfrom": str(year_start),
        "pubyearto": str(year_end),
        "count": str(min(limit, 1000)),
        "keyword": query,
    }
    
    # Add affiliate ID if available (improves rate limits)
    if JSTAGE_AFFILIATE_ID:
        params["affiliate"] = JSTAGE_AFFILIATE_ID
    
    headers = {
        "User-Agent": "AI-TechScout/1.0",
        "Accept": "application/xml",
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Parse XML response
    import xml.etree.ElementTree as ET
    
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        print("  J-STAGE returned invalid XML")
        return []
    
    # J-STAGE returns OpenSearch format
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
    }
    
    formatted_papers = []
    
    for entry in root.findall('.//entry', ns) or root.findall('.//item'):
        try:
            # Try different XML structures
            title = ""
            abstract = ""
            authors = []
            year = None
            doi = ""
            journal = ""
            
            # Get title
            title_elem = entry.find('title') or entry.find('.//{http://www.w3.org/2005/Atom}title')
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            
            # Get abstract/description
            for tag in ['abstract', 'description', 'summary', 
                       '{http://prismstandard.org/namespaces/basic/2.0/}abstract',
                       '{http://www.w3.org/2005/Atom}summary']:
                elem = entry.find(tag)
                if elem is not None and elem.text:
                    abstract = elem.text.strip()
                    break
            
            # Get authors
            for author_tag in ['author', '{http://www.w3.org/2005/Atom}author', 'creator']:
                for author in entry.findall(author_tag):
                    name_elem = author.find('name') or author.find('{http://www.w3.org/2005/Atom}name')
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                    elif author.text:
                        authors.append(author.text.strip())
            
            # Get year
            for date_tag in ['pubdate', '{http://prismstandard.org/namespaces/basic/2.0/}publicationDate',
                            'published', '{http://www.w3.org/2005/Atom}published']:
                date_elem = entry.find(date_tag)
                if date_elem is not None and date_elem.text:
                    try:
                        year = int(date_elem.text[:4])
                    except (ValueError, TypeError):
                        pass
                    break
            
            # Get DOI
            for id_tag in ['doi', 'id', '{http://prismstandard.org/namespaces/basic/2.0/}doi']:
                id_elem = entry.find(id_tag)
                if id_elem is not None and id_elem.text:
                    doi = id_elem.text.strip()
                    if 'doi.org' in doi or doi.startswith('10.'):
                        break
            
            # Get journal name
            for journal_tag in ['cdjournal', '{http://prismstandard.org/namespaces/basic/2.0/}publicationName',
                               'source']:
                journal_elem = entry.find(journal_tag)
                if journal_elem is not None and journal_elem.text:
                    journal = journal_elem.text.strip()
                    break
            
            if title:  # Only add if we at least have a title
                formatted_papers.append({
                    "title": title,
                    "abstract": abstract[:1000] if abstract else "",
                    "authors": authors[:10],  # Limit authors
                    "year": year,
                    "citations": 0,  # J-STAGE doesn't provide citation counts
                    "venue": journal,
                    "doi": doi,
                    "source": "jstage",
                    "region": "Japan",
                })
        except Exception:
            # Skip malformed entries
            continue
    
    return formatted_papers


# =============================================================================
# COMBINED PAPER SEARCH (with Japan option)
# =============================================================================

def search_papers_all(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50,
    include_japan: bool = False,
    fields_of_study: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Search papers from multiple sources, optionally including Japanese sources.
    
    Args:
        query: Search query
        year_start: Filter from year
        year_end: Filter to year
        limit: Max results per source
        include_japan: If True, also search J-STAGE for Japanese papers
        fields_of_study: Optional list of fields to filter by
    
    Returns:
        Combined list of papers from all sources
    """
    all_papers = []
    
    # Always search global sources
    global_papers = search_papers(query, year_start, year_end, limit, fields_of_study)
    all_papers.extend(global_papers)
    
    # Add Japanese sources if requested
    if include_japan:
        try:
            print(f"  Searching J-STAGE (Japan) for: {query[:50]}...")
            jstage_papers = search_papers_jstage(query, year_start, year_end, limit // 2)
            all_papers.extend(jstage_papers)
            print(f"  Found {len(jstage_papers)} papers from J-STAGE")
        except Exception as e:
            print(f"  J-STAGE search failed: {e}")
    
    return all_papers


# =============================================================================
# PATENT SEARCH
# =============================================================================

@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_tries=3
)
def search_patents(
    query: str,
    year_start: Optional[int] = None,
    limit: int = 30,
    country: str = "US",
) -> List[Dict]:
    """
    Search for patents. Tries multiple sources.
    """
    if year_start is None:
        year_start = datetime.now().year - 5
    
    # Try SerpAPI if available and configured (most reliable for patents)
    if SERPAPI_KEY and SERPAPI_KEY not in ["", "your-serpapi-key-here"]:
        try:
            results = search_patents_serpapi(query, year_start, limit, country)
            if results:
                return results
        except Exception as e:
            print(f"  SerpAPI patent search failed: {e}")
    
    # Fallback: Try Google Patents via web scraping
    try:
        return search_patents_google_fallback(query, year_start, limit)
    except Exception as e:
        print(f"  Google Patents fallback failed: {e}")
    
    return []


def search_patents_google_fallback(
    query: str,
    year_start: int,
    limit: int,
) -> List[Dict]:
    """Fallback patent search using Lens.org free API."""
    
    # Use Lens.org scholarly API - includes patents, free for research
    base_url = "https://api.lens.org/patent/search"
    
    # Simplify query
    clean_query = " ".join(query.split()[:8])
    
    payload = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": clean_query}}
                ],
                "filter": [
                    {"range": {"date_published": {"gte": f"{year_start}-01-01"}}}
                ]
            }
        },
        "size": limit,
        "sort": [{"date_published": "desc"}]
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AI-TechScout/1.0"
    }
    
    # Try Lens.org first
    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            patents = data.get("data", [])
            
            formatted_patents = []
            for patent in patents[:limit]:
                formatted_patents.append({
                    "patent_number": patent.get("lens_id", patent.get("doc_number", "")),
                    "title": patent.get("title", ""),
                    "abstract": (patent.get("abstract", "") or "")[:500],
                    "date": patent.get("date_published", ""),
                    "assignees": patent.get("applicants", []) or [],
                    "inventors": [inv.get("name", "") for inv in patent.get("inventors", []) or []],
                    "source": "lens_org",
                })
            
            if formatted_patents:
                return formatted_patents
    except Exception:
        pass
    
    # Fallback: Use EPO Open Patent Services (OPS) - free, no auth for basic search
    try:
        return search_patents_epo_ops(clean_query, year_start, limit)
    except Exception as e:
        print(f"  EPO OPS fallback failed: {e}")
    
    return []


def search_patents_epo_ops(
    query: str,
    year_start: int,
    limit: int,
) -> List[Dict]:
    """Search patents using EPO Open Patent Services (free, no auth required for basic)."""
    import urllib.parse
    
    # EPO OPS uses CQL query language
    # Search in title and abstract
    encoded_query = urllib.parse.quote(query)
    
    # Use the published-data/search endpoint
    url = f"https://ops.epo.org/3.2/rest-services/published-data/search?q=ti%3D{encoded_query}&Range=1-{min(limit, 25)}"
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "AI-TechScout/1.0"
    }
    
    response = requests.get(url, headers=headers, timeout=20)
    
    if response.status_code == 403:
        # EPO requires OAuth for some endpoints, skip gracefully
        return []
    
    response.raise_for_status()
    
    data = response.json()
    
    # Parse EPO response structure
    search_result = data.get("ops:world-patent-data", {}).get("ops:biblio-search", {})
    results = search_result.get("ops:search-result", {}).get("ops:publication-reference", [])
    
    if not isinstance(results, list):
        results = [results] if results else []
    
    formatted_patents = []
    for result in results[:limit]:
        doc_id = result.get("document-id", {})
        if isinstance(doc_id, list):
            doc_id = doc_id[0] if doc_id else {}
        
        patent_num = f"{doc_id.get('country', {}).get('$', '')}{doc_id.get('doc-number', {}).get('$', '')}"
        
        formatted_patents.append({
            "patent_number": patent_num,
            "title": "",  # Basic search doesn't return title
            "abstract": "",
            "date": doc_id.get("date", {}).get("$", ""),
            "assignees": [],
            "inventors": [],
            "source": "epo_ops",
        })
    
    return formatted_patents


def search_patents_serpapi(
    query: str,
    year_start: int,
    limit: int,
    country: str,
) -> List[Dict]:
    """Search patents using SerpAPI Google Patents."""
    base_url = "https://serpapi.com/search"
    
    params = {
        "engine": "google_patents",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": limit,
    }
    
    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    patents = data.get("organic_results", [])
    
    formatted_patents = []
    for patent in patents:
        formatted_patents.append({
            "patent_number": patent.get("patent_id", ""),
            "title": patent.get("title", ""),
            "abstract": patent.get("snippet", ""),
            "date": patent.get("publication_date", ""),
            "assignees": [patent.get("assignee", "")] if patent.get("assignee") else [],
            "inventors": patent.get("inventor", "").split(", ") if patent.get("inventor") else [],
            "source": "serpapi",
        })
    
    return formatted_patents

# =============================================================================
# NEWS SEARCH
# =============================================================================

@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_tries=3
)
def search_news(
    query: str,
    days_back: int = 90,
    limit: int = 30,
) -> List[Dict]:
    """
    Search for recent news articles about a technology topic.
    Uses free sources first, then NewsAPI if configured.
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Try Google News RSS (free, no API key)
    try:
        articles = search_news_google_rss(query, limit)
        if articles:
            return articles
    except Exception as e:
        print(f"  Google News RSS failed: {e}")
    
    # Try NewsAPI if configured
    if GOOGLE_NEWS_API_KEY and GOOGLE_NEWS_API_KEY != "your-newsapi-key-here":
        try:
            return search_news_newsapi(query, start_date, end_date, limit)
        except Exception as e:
            print(f"  NewsAPI search failed: {e}")
    
    # Return empty - news is optional
    return []


def search_news_google_rss(
    query: str,
    limit: int = 30,
) -> List[Dict]:
    """
    Search news using Google News RSS feed (free, no API key).
    """
    import urllib.parse
    
    # Google News RSS endpoint
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {"User-Agent": "AI-TechScout/1.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Parse RSS XML
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.content)
    
    formatted_articles = []
    items = root.findall(".//item")[:limit]
    
    for item in items:
        title = item.find("title")
        link = item.find("link")
        pub_date = item.find("pubDate")
        source = item.find("source")
        
        formatted_articles.append({
            "title": title.text if title is not None else "",
            "description": "",  # RSS doesn't include description
            "source": source.text if source is not None else "Google News",
            "author": "",
            "published_at": pub_date.text if pub_date is not None else "",
            "url": link.text if link is not None else "",
        })
    
    return formatted_articles


def search_news_newsapi(
    query: str,
    start_date: datetime,
    end_date: datetime,
    limit: int,
) -> List[Dict]:
    """Search news using NewsAPI (requires API key)."""
    base_url = "https://newsapi.org/v2/everything"
    
    params = {
        "q": query,
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "sortBy": "relevancy",
        "pageSize": min(limit, 100),
        "apiKey": GOOGLE_NEWS_API_KEY,
    }
    
    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    articles = data.get("articles", [])
    
    formatted_articles = []
    for article in articles:
        formatted_articles.append({
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "source": article.get("source", {}).get("name", ""),
            "author": article.get("author", ""),
            "published_at": article.get("publishedAt", ""),
            "url": article.get("url", ""),
        })
    
    return formatted_articles


# =============================================================================
# JAPAN-SPECIFIC NEWS SEARCH
# =============================================================================

def search_news_japan(
    query: str,
    days_back: int = 90,
    limit: int = 30,
) -> List[Dict]:
    """
    Search for news from Japan-focused sources.
    Uses Google News Japan + supplementary Japanese tech news sources.
    """
    all_articles = []
    
    # 1. Google News Japan RSS (Japanese results)
    try:
        jp_articles = search_news_google_rss_japan(query, limit // 2)
        all_articles.extend(jp_articles)
    except Exception as e:
        print(f"  Google News Japan failed: {e}")
    
    # 2. Try general Google News with Japan context
    try:
        japan_query = f"{query} Japan Japanese"
        global_jp_articles = search_news_google_rss(japan_query, limit // 2)
        all_articles.extend(global_jp_articles)
    except Exception as e:
        print(f"  Google News global Japan failed: {e}")
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title_lower = article.get("title", "").lower()
        if title_lower and title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_articles.append(article)
    
    return unique_articles[:limit]


def search_news_google_rss_japan(
    query: str,
    limit: int = 30,
) -> List[Dict]:
    """
    Search news using Google News RSS feed with Japan locale.
    Can search in English or Japanese.
    """
    import urllib.parse
    
    # Google News RSS endpoint - Japan locale
    encoded_query = urllib.parse.quote(query)
    
    # Use Japan Google News (English interface but Japan news)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=JP&ceid=JP:en"
    
    headers = {"User-Agent": "AI-TechScout/1.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Parse RSS XML
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.content)
    
    formatted_articles = []
    items = root.findall(".//item")[:limit]
    
    for item in items:
        title = item.find("title")
        link = item.find("link")
        pub_date = item.find("pubDate")
        source = item.find("source")
        
        formatted_articles.append({
            "title": title.text if title is not None else "",
            "description": "",
            "source": source.text if source is not None else "Google News Japan",
            "author": "",
            "published_at": pub_date.text if pub_date is not None else "",
            "url": link.text if link is not None else "",
            "region": "Japan",
        })
    
    return formatted_articles


# =============================================================================
# MAIN SCOUTING FUNCTION
# =============================================================================

def scout_technologies(
    base_dir: str,
    client,
    model: str,
    domain: str,
    focus_areas: List[str],
    search_queries: List[str],
    skip_search: bool = False,
    num_reflections: int = 3,
    year_lookback: int = 3,
    region_focus: Optional[str] = None,
) -> Dict:
    """
    Main function to scout for emerging technologies in a given domain.
    
    Args:
        base_dir: Directory to store results
        client: LLM client
        model: LLM model name
        domain: Technology domain to scout (e.g., "AI/ML", "Biotechnology")
        focus_areas: List of specific areas to focus on
        search_queries: List of search queries to use
        skip_search: Skip searching and use cached results
        num_reflections: Number of refinement iterations
        year_lookback: How many years back to search
        region_focus: Optional region focus (e.g., "japan", "eu", "us")
    
    Returns:
        Dictionary with discovered technologies and analysis
    """
    results_file = osp.join(base_dir, "scouting_results.json")
    
    # Check for cached results
    if skip_search and osp.exists(results_file):
        print("Loading cached scouting results...")
        with open(results_file, "r") as f:
            return json.load(f)
    
    # Check template for region focus
    prompt_file = osp.join(base_dir, "prompt.json")
    if osp.exists(prompt_file):
        with open(prompt_file, "r") as f:
            prompt_config = json.load(f)
        # Override region_focus from template if not provided
        if region_focus is None:
            region_focus = prompt_config.get("region_focus")
    
    include_japan = region_focus and region_focus.lower() in ["japan", "jp", "asia"]
    
    print(f"Starting technology scouting for domain: {domain}")
    print(f"Focus areas: {', '.join(focus_areas)}")
    if region_focus:
        print(f"Region focus: {region_focus}")
    
    # Collect data from all sources
    all_papers = []
    all_patents = []
    all_news = []
    
    year_start = datetime.now().year - year_lookback
    year_end = datetime.now().year
    
    for query in search_queries:
        print(f"\nSearching for: {query}")
        
        # Search academic papers (global + region-specific)
        try:
            if include_japan:
                papers = search_papers_all(
                    query, year_start, year_end, limit=30, include_japan=True
                )
            else:
                papers = search_papers(query, year_start, year_end, limit=30)
            all_papers.extend(papers)
            print(f"  Found {len(papers)} papers")
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"  Paper search failed: {e}")
        
        # Search patents
        try:
            patent_country = "JP" if include_japan else "US"
            patents = search_patents(query, year_start, limit=20, country=patent_country)
            all_patents.extend(patents)
            print(f"  Found {len(patents)} patents")
            time.sleep(1)
        except Exception as e:
            print(f"  Patent search failed: {e}")
        
        # Search news
        try:
            if include_japan:
                news = search_news_japan(query, days_back=180, limit=20)
            else:
                news = search_news(query, days_back=180, limit=20)
            all_news.extend(news)
            print(f"  Found {len(news)} news articles")
            time.sleep(1)
        except Exception as e:
            print(f"  News search failed: {e}")
    
    # Load existing technologies if available
    existing_tech_file = osp.join(base_dir, "existing_technologies.json")
    existing_technologies = []
    if osp.exists(existing_tech_file):
        with open(existing_tech_file, "r") as f:
            existing_technologies = json.load(f)
    
    # Format data for LLM
    papers_str = json.dumps(all_papers[:50], indent=2)  # Limit for context
    patents_str = json.dumps(all_patents[:30], indent=2)
    news_str = json.dumps(all_news[:30], indent=2)
    existing_str = json.dumps(existing_technologies, indent=2)
    
    # Load system prompt from template if available
    prompt_file = osp.join(base_dir, "prompt.json")
    if osp.exists(prompt_file):
        with open(prompt_file, "r") as f:
            prompt_config = json.load(f)
        system_prompt = prompt_config.get("system", "You are an expert technology scout.")
    else:
        system_prompt = "You are an expert technology scout with deep knowledge of emerging technologies and their commercial potential."
    
    # Generate initial analysis
    print("\nAnalyzing collected data with LLM...")
    msg_history = []
    
    text, msg_history = get_response_from_llm(
        technology_discovery_prompt.format(
            domain=domain,
            focus_areas="\n".join(f"- {area}" for area in focus_areas),
            papers=papers_str,
            patents=patents_str,
            news=news_str,
            existing_technologies=existing_str,
        ),
        client=client,
        model=model,
        system_message=system_prompt,
        msg_history=msg_history,
    )
    
    technologies = extract_json_between_markers(text)
    
    # Refinement iterations
    if num_reflections > 1:
        for i in range(num_reflections - 1):
            print(f"Refinement iteration {i + 2}/{num_reflections}")
            
            text, msg_history = get_response_from_llm(
                technology_refinement_prompt.format(
                    current_round=i + 2,
                    num_reflections=num_reflections,
                ),
                client=client,
                model=model,
                system_message=system_prompt,
                msg_history=msg_history,
            )
            
            new_technologies = extract_json_between_markers(text)
            if new_technologies:
                technologies = new_technologies
            
            if "ANALYSIS COMPLETE" in text:
                print(f"Analysis converged after {i + 2} iterations.")
                break
    
    # Generate trend analysis
    print("\nGenerating trend analysis...")
    trend_text, _ = get_response_from_llm(
        trend_analysis_prompt.format(
            domain=domain,
            technologies=json.dumps(technologies, indent=2),
        ),
        client=client,
        model=model,
        system_message=system_prompt,
        msg_history=[],
    )
    
    trend_insights = extract_json_between_markers(trend_text)
    
    # Compile results
    results = {
        "domain": domain,
        "focus_areas": focus_areas,
        "search_queries": search_queries,
        "scouting_date": datetime.now().isoformat(),
        "data_sources": {
            "papers_count": len(all_papers),
            "patents_count": len(all_patents),
            "news_count": len(all_news),
        },
        "technologies": technologies,
        "trend_insights": trend_insights,
        "raw_data": {
            "papers": all_papers,
            "patents": all_patents,
            "news": all_news,
        },
    }
    
    # Save results
    os.makedirs(base_dir, exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nScouting complete. Found {len(technologies) if technologies else 0} technologies.")
    print(f"Results saved to: {results_file}")
    
    return results


def generate_search_queries(
    client,
    model: str,
    domain: str,
    focus_areas: List[str],
    num_queries: int = 10,
) -> List[str]:
    """
    Use LLM to generate effective search queries for a given domain.
    """
    prompt = f"""Generate {num_queries} effective search queries for technology scouting in the following domain:

Domain: {domain}
Focus Areas:
{chr(10).join(f"- {area}" for area in focus_areas)}

Generate queries that will find:
1. Recent academic breakthroughs
2. Patent filings indicating commercial development
3. Startup and industry activity

Return as a JSON list of strings:
```json
["query1", "query2", ...]
```
"""
    
    text, _ = get_response_from_llm(
        prompt,
        client=client,
        model=model,
        system_message="You are an expert at information retrieval and technology scouting.",
        msg_history=[],
    )
    
    queries = extract_json_between_markers(text)
    return queries if queries else []


if __name__ == "__main__":
    # Test the module
    print("Technology Scouting Module")
    print("Use scout_technologies() to start scouting.")
