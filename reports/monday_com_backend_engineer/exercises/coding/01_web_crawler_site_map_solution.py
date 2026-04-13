"""
Solution: Web Crawler / Site Map Graph
=======================================
Monday.com Backend Engineer Interview Question (Real)

Complexity Analysis:
    Time:  O(N) where N = number of pages visited. Each page is fetched exactly once.
    Space: O(N + E) where N = visited URLs, E = total link edges stored in the graph.

Approach: BFS (Breadth-First Search) with depth tracking.
"""

from collections import deque, defaultdict
from typing import Dict, List, Set, Tuple

# ---------------------------------------------------------------------------
# Mock web: simulates a small website. DO NOT MODIFY.
# ---------------------------------------------------------------------------
MOCK_WEB: Dict[str, List[str]] = {
    "https://example.com": [
        "https://example.com/about",
        "https://example.com/products",
        "https://example.com/blog",
    ],
    "https://example.com/about": [
        "https://example.com",
        "https://example.com/about/team",
    ],
    "https://example.com/products": [
        "https://example.com",
        "https://example.com/products/widget",
        "https://example.com/products/gadget",
    ],
    "https://example.com/blog": [
        "https://example.com",
        "https://example.com/blog/post-1",
        "https://example.com/blog/post-2",
    ],
    "https://example.com/about/team": [
        "https://example.com/about",
    ],
    "https://example.com/products/widget": [
        "https://example.com/products",
    ],
    "https://example.com/products/gadget": [
        "https://example.com/products",
        "https://external-site.com/review",
    ],
    "https://example.com/blog/post-1": [
        "https://example.com/blog",
    ],
    "https://example.com/blog/post-2": [
        "https://example.com/blog",
        "https://example.com/blog/post-1",
    ],
    "https://external-site.com/review": [],
}


def fetch_links(url: str) -> List[str]:
    """Simulate fetching a page and extracting its hyperlinks."""
    return MOCK_WEB.get(url, [])


# ---------------------------------------------------------------------------
# SOLUTION
# ---------------------------------------------------------------------------

def crawl(root_url: str, max_depth: int) -> Tuple[Dict[str, List[str]], Set[str]]:
    """Crawl starting from root_url up to max_depth levels using BFS.

    The key insight is to use BFS with explicit depth tracking. We store
    (url, depth) pairs in the queue. A URL is "visited" the moment we add
    it to the queue (not when we dequeue it) -- this prevents duplicate
    enqueuing.

    Args:
        root_url: The starting URL.
        max_depth: Maximum depth to crawl (root is depth 0).

    Returns:
        A tuple of (site_map adjacency list, set of visited URLs).
    """
    site_map: Dict[str, List[str]] = {}
    visited: Set[str] = set()

    # BFS queue holds (url, depth) pairs
    queue: deque = deque()
    queue.append((root_url, 0))
    visited.add(root_url)

    while queue:
        current_url, depth = queue.popleft()

        # Fetch links for the current page (this is the "visit" / "process" step)
        child_links = fetch_links(current_url)
        site_map[current_url] = child_links

        # Only follow children if we haven't reached max_depth
        if depth < max_depth:
            for link in child_links:
                if link not in visited:
                    visited.add(link)
                    queue.append((link, depth + 1))

    return site_map, visited


# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACH: DFS with depth tracking
# ---------------------------------------------------------------------------

def crawl_dfs(root_url: str, max_depth: int) -> Tuple[Dict[str, List[str]], Set[str]]:
    """DFS-based crawler. Same complexity, different traversal order.

    Tradeoff vs BFS:
      - BFS explores level by level (breadth-first), which naturally respects
        depth limits and finds shortest paths first.
      - DFS uses less memory for wide graphs but may go deep before going wide.
      - For web crawling, BFS is generally preferred because it discovers
        the most important (closest to root) pages first.
    """
    site_map: Dict[str, List[str]] = {}
    visited: Set[str] = set()

    def dfs(url: str, depth: int) -> None:
        visited.add(url)
        child_links = fetch_links(url)
        site_map[url] = child_links

        if depth < max_depth:
            for link in child_links:
                if link not in visited:
                    dfs(link, depth + 1)

    dfs(root_url, 0)
    return site_map, visited


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------
import pytest


class TestWebCrawler:

    def test_depth_zero_only_root(self):
        site_map, visited = crawl("https://example.com", max_depth=0)
        assert "https://example.com" in visited
        assert len(visited) == 1
        assert set(site_map["https://example.com"]) == {
            "https://example.com/about",
            "https://example.com/products",
            "https://example.com/blog",
        }

    def test_depth_one(self):
        site_map, visited = crawl("https://example.com", max_depth=1)
        expected_visited = {
            "https://example.com",
            "https://example.com/about",
            "https://example.com/products",
            "https://example.com/blog",
        }
        assert visited == expected_visited

    def test_depth_two_reaches_leaves(self):
        site_map, visited = crawl("https://example.com", max_depth=2)
        assert "https://example.com/about/team" in visited
        assert "https://example.com/products/widget" in visited
        assert "https://example.com/blog/post-2" in visited

    def test_no_duplicate_visits(self):
        site_map, visited = crawl("https://example.com", max_depth=5)
        url_count = sum(1 for _ in site_map.keys())
        assert url_count == len(visited)

    def test_unknown_root_url(self):
        site_map, visited = crawl("https://nonexistent.com", max_depth=3)
        assert visited == {"https://nonexistent.com"}
        assert site_map["https://nonexistent.com"] == []

    def test_external_link_discovered(self):
        site_map, visited = crawl("https://example.com", max_depth=3)
        assert "https://external-site.com/review" in visited

    def test_site_map_is_directed_graph(self):
        site_map, _ = crawl("https://example.com", max_depth=1)
        assert "https://example.com/about/team" not in site_map


# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS:
#
# 1. "How would you make this concurrent / multithreaded?"
#    -> Use a thread pool (concurrent.futures.ThreadPoolExecutor). Each worker
#       fetches a page. Use a thread-safe queue and a lock around 'visited'.
#       This maps to LC #1242 Web Crawler Multithreaded.
#
# 2. "How would you handle rate limiting?"
#    -> Token bucket or leaky bucket rate limiter. Add a semaphore or
#       asyncio.Semaphore to limit concurrent requests per domain.
#
# 3. "How would you restrict crawling to the same domain?"
#    -> Parse the URL with urllib.parse, compare the netloc (domain) of each
#       discovered link against the root URL's domain before enqueuing.
#
# 4. "How would you handle very large websites (billions of pages)?"
#    -> Distributed crawling (multiple machines), URL frontier with priority
#       queue, persistent visited set (Bloom filter for probabilistic
#       membership, or distributed key-value store like Redis).
#
# 5. "How would you respect robots.txt?"
#    -> Fetch and parse robots.txt for each domain before crawling.
#       Use urllib.robotparser.RobotFileParser.
#
# 6. "What if fetch_links can fail or timeout?"
#    -> Retry with exponential backoff. Mark failed URLs and optionally
#       retry them later. Use a dead-letter queue for persistent failures.
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR:
#
# - Correct BFS/DFS with depth tracking (not just "visit everything")
# - Cycle detection via visited set (critical for web graphs)
# - Clean separation between fetching logic and graph building
# - Awareness of edge cases: unreachable URLs, external domains, cycles
# - Discussion of production concerns: concurrency, rate limiting, scale
# - Clear variable names and function documentation
# ---------------------------------------------------------------------------
