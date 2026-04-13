"""
Exercise 1: Web Crawler / Site Map Graph
=========================================
Monday.com Backend Engineer Interview Question (Real)

PROBLEM:
    Given a root URL and max_depth, implement a web crawler that searches for
    hyperlinks in each page and stores found URLs in a graph data structure
    representing a site map.

    The program should take a root URL and max_depth as inputs. Starting from the
    root URL, the crawler visits each page, extracts the hyperlinks found on that
    page, and records the parent->child URL relationships in a directed graph.

    The crawler must:
    1. Start from the root URL at depth 0.
    2. For each visited page, call fetch_links(url) to get outgoing links.
    3. Follow links up to (but not exceeding) max_depth levels from the root.
    4. Avoid visiting the same URL twice.
    5. Store results in a graph (adjacency list): {url: [list of linked urls]}.
    6. Return the graph (site map) and the set of all visited URLs.

    IMPORTANT: A mock fetch_links() function is provided below so you can test
    without making real HTTP requests. Do NOT modify the mock.

CONSTRAINTS:
    - Time Complexity Target: O(N) where N = total number of pages visited
    - Space Complexity: O(N + E) where E = total number of edges (links)
    - Do not visit the same URL more than once
    - Respect max_depth (root is depth 0)

DIFFICULTY: Medium-Hard
LC EQUIVALENT: #1236 Web Crawler, #1242 Web Crawler Multithreaded

Author's note: In a real interview you would discuss how to handle rate limiting,
robots.txt, same-domain filtering, and parallelism. Focus on correctness first.
"""

from collections import defaultdict
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
    """Simulate fetching a page and extracting its hyperlinks.

    Returns a list of URLs found on the given page.
    Returns an empty list if the URL is unknown / unreachable.
    """
    return MOCK_WEB.get(url, [])


# ---------------------------------------------------------------------------
# YOUR IMPLEMENTATION
# ---------------------------------------------------------------------------

def crawl(root_url: str, max_depth: int) -> Tuple[Dict[str, List[str]], Set[str]]:
    """Crawl starting from root_url up to max_depth levels.

    Args:
        root_url: The starting URL.
        max_depth: Maximum depth to crawl (root is depth 0).

    Returns:
        A tuple of:
          - site_map: dict mapping each visited URL to the list of URLs it links to.
          - visited: set of all URLs that were visited (fetched).
    """
    site_map: Dict[str, List[str]] = {}
    visited: Set[str] = set()

    # TODO: Implement BFS or DFS crawl
    # - Start from root_url at depth 0
    # - Use fetch_links(url) to get outgoing links for each page
    # - Track depth so you don't exceed max_depth
    # - Don't visit the same URL twice
    # - Populate site_map with {url: [child_urls]} for each visited page
    # - Populate visited with every URL you fetched

    pass  # Remove this line

    return site_map, visited


# ---------------------------------------------------------------------------
# TESTS -- run with: pytest 01_web_crawler_site_map.py -v
# ---------------------------------------------------------------------------
import pytest


class TestWebCrawler:

    def test_depth_zero_only_root(self):
        """At depth 0, we visit only the root and record its links."""
        site_map, visited = crawl("https://example.com", max_depth=0)
        assert "https://example.com" in visited
        assert len(visited) == 1
        assert set(site_map["https://example.com"]) == {
            "https://example.com/about",
            "https://example.com/products",
            "https://example.com/blog",
        }

    def test_depth_one(self):
        """At depth 1, we visit root + its direct children."""
        site_map, visited = crawl("https://example.com", max_depth=1)
        expected_visited = {
            "https://example.com",
            "https://example.com/about",
            "https://example.com/products",
            "https://example.com/blog",
        }
        assert visited == expected_visited

    def test_depth_two_reaches_leaves(self):
        """At depth 2, we reach the deeper pages."""
        site_map, visited = crawl("https://example.com", max_depth=2)
        assert "https://example.com/about/team" in visited
        assert "https://example.com/products/widget" in visited
        assert "https://example.com/blog/post-2" in visited

    def test_no_duplicate_visits(self):
        """Even with cycles (e.g. child links back to parent), each URL visited once."""
        site_map, visited = crawl("https://example.com", max_depth=5)
        # visited should be a set so duplicates are impossible,
        # but also the site_map should not have duplicate fetch calls.
        url_count = sum(1 for _ in site_map.keys())
        assert url_count == len(visited)

    def test_unknown_root_url(self):
        """If the root URL has no links, return it visited with empty links."""
        site_map, visited = crawl("https://nonexistent.com", max_depth=3)
        assert visited == {"https://nonexistent.com"}
        assert site_map["https://nonexistent.com"] == []

    def test_external_link_discovered(self):
        """External links should be discovered and visited if within depth."""
        site_map, visited = crawl("https://example.com", max_depth=3)
        assert "https://external-site.com/review" in visited

    def test_site_map_is_directed_graph(self):
        """The site_map should represent directed edges (parent -> children)."""
        site_map, _ = crawl("https://example.com", max_depth=1)
        # /about links back to root, but root's entry should not list /about/team
        # (that requires depth 2 to discover)
        assert "https://example.com/about/team" not in site_map


# Complexity target:
# Time:  O(N) where N = number of pages visited (each page fetched exactly once)
# Space: O(N + E) for the adjacency list (N nodes, E edges)

# HINT 1: Use BFS with a queue that stores (url, current_depth) tuples.
#          Initialize with (root_url, 0). Only enqueue children if depth < max_depth.

# HINT 2: Maintain a 'visited' set. Before enqueuing a child URL, check if it
#          has already been visited to avoid cycles and redundant work.

# HINT 3: For each URL you dequeue, call fetch_links(url) and store the result
#          in site_map[url]. Then for each child link, if not visited and depth
#          < max_depth, add it to the queue with depth+1.
