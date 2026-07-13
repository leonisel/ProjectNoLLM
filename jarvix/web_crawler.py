"""
Jarvix - Web Crawler Module v3
Advanced HTML filtering, fact extraction, and knowledge integration.
Strips nav/ads/menus/dictionary-metadata.
Only keeps headings + main prose content.
"""

import re
import time
import logging
from urllib.parse import urlparse, urljoin
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Set
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class CrawlQuality(Enum):
    """Quality assessment enum for crawl results."""
    A = "A — High-density knowledge (>15% facts)"
    B = "B — Solid factual content (8-15%)"
    C = "C — Moderate factual content (3-8%)"
    D = "D — Low fact density (0-3%)"
    F = "F — No extractable facts"


@dataclass
class PageResult:
    """Result of processing a single page."""
    url: str
    title: str = ""
    word_count: int = 0
    sentence_count: int = 0
    facts_extracted: int = 0
    facts_stored: int = 0
    facts_skipped: int = 0
    top_topics: list = field(default_factory=list)
    error: str = ""
    fetch_time_ms: int = 0


@dataclass
class CrawlReport:
    """Complete report from a crawl operation."""
    seed_url: str
    pages_visited: int = 0
    pages_failed: int = 0
    total_words: int = 0
    total_sentences: int = 0
    total_facts: int = 0
    stored_facts: int = 0
    duplicate_facts: int = 0
    top_topics: list = field(default_factory=list)
    top_facts: list = field(default_factory=list)
    page_results: list = field(default_factory=list)
    knowledge_gain: float = 0.0
    errors: list = field(default_factory=list)
    elapsed_ms: int = 0


class WebCrawler:
    """
    Production-grade web crawler for fact extraction.
    
    Features:
    - Aggressive HTML noise removal (nav, ads, sidebars)
    - Sentence quality filtering
    - SVO triple extraction
    - Confidence-based deduplication
    - Structured reporting
    """

    # Tags always discarded (navigation, ads, UI chrome)
    DISCARD_TAGS = {
        "script", "style", "nav", "header", "footer", "aside",
        "form", "noscript", "iframe", "svg", "button", "input",
        "select", "textarea", "meta", "link", "figure", "figcaption",
        "picture", "video", "audio", "canvas", "map", "object",
        "table", "sup", "sub", "cite",  # dictionary/wiki noise
    }

    # CSS class/id patterns indicating nav/ad/menu content
    NOISE_PATTERNS = re.compile(
        r"(nav|menu|sidebar|banner|ad|ads|advertisement|cookie|\n"
        r"popup|modal|footer|header|breadcrumb|pagination|\n"
        r"related|share|social|comment|login|signup|subscribe|\n"
        r"toc|contents|infobox|hatnote|catlinks|reflist|\n"
        r"references|external\\.links|see\\.also)",
        re.I
    )

    # Sentence quality filters - reject junk patterns
        # Sentence quality filters - reject junk patterns
    _JUNK_PATTERNS = [
        re.compile(r"^\s*\[[^\]]+\]\s*$"),  # Matches [edit], [1], [citation needed]
        re.compile(r"^[^a-zA-Z]*$"),  # no letters
        re.compile(r"^\s*\d+\s*$"),  # bare numbers
        re.compile(
            r"(click here|read more|learn more|"
            r"sign up|log in|subscribe|cookie|"
            r"privacy policy|terms of)",
            re.I,
        ),
        re.compile(r"^.{1,10}$"),  # too short
        re.compile(r"^.{400,}$"),  # too long
        re.compile(r"\|.*\|"),  # nav pipe separators
        re.compile(
            r"^\s*(home|about|contact|help|search|menu|navigation)\s*$",
            re.I,
        ),
        re.compile(
            r"^(before|after|used|when|consonant sound|vowel sound)\s+",
            re.I,
        ),
        re.compile(
            r"\b(IPA|pronunciation|phonetic|syllable|hyphenation)\b",
            re.I,
        ),
    ]

    # Relation patterns for SVO triple extraction
        # Sentence quality filters - reject junk patterns
    _JUNK_PATTERNS = [
        re.compile(r"^\s*\[[^\]]+\]\s*$"),  # Matches [edit], [1], [citation needed]
        re.compile(r"^[^a-zA-Z]*$"),  # no letters
        re.compile(r"^\s*\d+\s*$"),  # bare numbers
        re.compile(
            r"(click here|read more|learn more|"
            r"sign up|log in|subscribe|cookie|"
            r"privacy policy|terms of)",
            re.I,
        ),
        re.compile(r"^.{1,10}$"),  # too short
        re.compile(r"^.{400,}$"),  # too long
        re.compile(r"\|.*\|"),  # nav pipe separators
        re.compile(
            r"^\s*(home|about|contact|help|search|menu|navigation)\s*$",
            re.I,
        ),
        re.compile(
            r"^(before|after|used|when|consonant sound|vowel sound)\s+",
            re.I,
        ),
        re.compile(
            r"\b(IPA|pronunciation|phonetic|syllable|hyphenation)\b",
            re.I,
        ),
    ]

    # Configuration thresholds
    MIN_PHRASE_LENGTH = 2
    MAX_SUBJECT_LENGTH = 60
    MAX_OBJECT_LENGTH = 120
    MAX_OBJECT_WORDS = 12
    MIN_REAL_WORDS_IN_SENTENCE = 3
    DUPLICATE_CONFIDENCE_THRESHOLD = 0.5
    BASE_TRIPLE_CONFIDENCE = 0.60
    REQUEST_TIMEOUT_SECONDS = 8
    DEFAULT_USER_AGENT = "Jarvix-Crawler/3.0"

    def __init__( 
        self,
        agent,
        max_depth: int = 1,
        max_pages: int = 10,
        timeout_s: int = 8,
        same_domain_only: bool = True,
        request_delay_s: float = 0.5,
        ):
        """Initialize the web crawler.
        
        Args:
        agent: Jarvix agent instance for memory/knowledge integration
        max_depth: Maximum crawl depth (0 = seed only)
        max_pages: Maximum pages to process
        timeout_s: HTTP request timeout in seconds
        same_domain_only: Whether to restrict crawling to seed domain
        request_delay_s: Delay between requests (politeness)
        """
        self.agent = agent
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout_s = timeout_s
        self.same_domain_only = same_domain_only
        self.request_delay_s = request_delay_s
        self._visited: Set[str] = set()
        self._last_request_time = 0.0