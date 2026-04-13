#!/usr/bin/env python3
"""
Interview Prep Report Generator

Scrapes public sources for interview data about a company and role,
then uses Claude to synthesize a preparation report.

Usage:
    python generate_report.py "Monday.com" "Backend Engineer"
    python generate_report.py "Stripe" "Software Engineer"
"""

import sys
import json
import os
import asyncio
from datetime import datetime
from urllib.parse import unquote, urlparse, parse_qs

try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency: pip install anthropic")

try:
    import aiohttp
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependencies: pip install aiohttp beautifulsoup4")


HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
SKIP_DOMAINS = {"youtube.com", "linkedin.com", "facebook.com", "twitter.com"}


async def search_duckduckgo(session: aiohttp.ClientSession, query: str, max_results: int = 8) -> list[dict]:
    """Search DuckDuckGo and return result URLs + snippets."""
    params = {"q": query, "t": "h_", "ia": "web"}
    try:
        async with session.get(
            "https://html.duckduckgo.com/html/",
            params=params,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for r in soup.select(".result")[:max_results]:
            title_el = r.select_one(".result__title a")
            snippet_el = r.select_one(".result__snippet")
            if title_el:
                href = title_el.get("href", "")
                if "uddg=" in href:
                    parsed = parse_qs(urlparse(href).query)
                    href = unquote(parsed.get("uddg", [href])[0])
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": href,
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })
        return results
    except Exception as e:
        print(f"  [warn] Search failed for '{query}': {e}")
        return []


async def fetch_page_text(session: aiohttp.ClientSession, url: str, title: str, max_chars: int = 15000) -> dict | None:
    """Fetch a URL and extract readable text."""
    try:
        async with session.get(
            url,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        if len(text) > 200:
            return {"title": title, "url": url, "text": text[:max_chars]}
        return None
    except Exception as e:
        print(f"  [warn] Failed to fetch {url}: {e}")
        return None


async def gather_data(company: str, role: str) -> str:
    """Search multiple sources in parallel and collect raw text data."""
    queries = [
        f"{company} {role} interview process questions",
        f"{company} {role} interview experience glassdoor",
        f"{company} engineering blog hiring interview",
        f"{company} tech stack backend architecture",
        f"{company} {role} interview reddit",
    ]

    async with aiohttp.ClientSession() as session:
        # Phase 1: Run all searches in parallel
        print("  Searching all queries in parallel...")
        search_tasks = [search_duckduckgo(session, q) for q in queries]
        search_results = await asyncio.gather(*search_tasks)

        # Deduplicate and filter URLs
        seen_urls = set()
        fetch_items = []
        for results in search_results:
            for r in results:
                url = r["url"]
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                if any(d in url for d in SKIP_DOMAINS):
                    continue
                fetch_items.append(r)

        # Phase 2: Fetch all pages in parallel
        print(f"  Fetching {len(fetch_items)} pages in parallel...")
        fetch_tasks = [
            fetch_page_text(session, r["url"], r["title"])
            for r in fetch_items
        ]
        fetched = await asyncio.gather(*fetch_tasks)

    all_content = []
    for result in fetched:
        if result:
            all_content.append(
                f"--- SOURCE: {result['title']} ({result['url']}) ---\n{result['text']}\n"
            )

    combined = "\n\n".join(all_content)
    if len(combined) > 80000:
        combined = combined[:80000] + "\n\n[...truncated...]"

    print(f"  Collected {len(all_content)} sources, {len(combined)} chars total")
    return combined


def generate_report(company: str, role: str, raw_data: str) -> str:
    """Use Claude to synthesize a prep report from raw data."""
    client = anthropic.Anthropic()

    prompt = f"""You are an interview preparation expert. Based on the following raw data
scraped from various sources about {company}'s interview process for {role} positions,
create a comprehensive interview preparation report.

The report should include:
1. **TL;DR** - 3-4 sentence summary
2. **Interview Process** - stages, timeline, format (table format)
3. **What They Ask** - coding, system design, and behavioral questions with specifics
4. **Tech Stack** - what the company uses (relevant to the role)
5. **How to Prepare** - concrete action items organized by timeline
6. **Key Signals** - what interviewers look for
7. **Sources** - list the URLs where the info came from

Be specific and actionable. If data is sparse for a section, say so rather than making things up.
Use markdown formatting.

RAW DATA:
{raw_data}
"""

    print("  Generating report with Claude...")
    message = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


async def async_main():
    if len(sys.argv) < 3:
        print("Usage: python generate_report.py <company> <role>")
        print('Example: python generate_report.py "Monday.com" "Backend Engineer"')
        sys.exit(1)

    company = sys.argv[1]
    role = sys.argv[2]

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY environment variable first")

    print(f"\n=== Interview Prep Report: {company} — {role} ===\n")

    print("[1/3] Gathering data from web sources...")
    raw_data = await gather_data(company, role)

    if len(raw_data) < 500:
        print("\n[!] Very little data found. Report may be sparse.")

    print("\n[2/3] Analyzing with Claude...")
    report = generate_report(company, role, raw_data)

    # Save report
    os.makedirs("reports", exist_ok=True)
    safe_name = company.lower().replace(" ", "_").replace(".", "")
    safe_role = role.lower().replace(" ", "_")
    filename = f"reports/{safe_name}_{safe_role}_{datetime.now().strftime('%Y%m%d')}.md"

    header = f"# {company} — {role} Interview Prep Report\n\n"
    header += f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n\n---\n\n"

    with open(filename, "w") as f:
        f.write(header + report)

    print(f"\n[3/3] Report saved to {filename}")
    print(f"\n{'='*50}")
    print(report)


if __name__ == "__main__":
    asyncio.run(async_main())
