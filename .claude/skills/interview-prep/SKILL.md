---
name: interview-prep
description: Generate an interview preparation report for a specific company and role. Use when the user wants to prepare for a job interview, research a company's hiring process, or understand what questions to expect.
argument-hint: "<company> <role>"
disable-model-invocation: true
---

Generate a comprehensive interview preparation package for **$0** for the **$1** role.

## Step 1: Research Phase + User Questions — ALL IN PARALLEL

**CRITICAL: Launch ALL 3 research agents AND AskUserQuestion in a SINGLE message (4 tool calls). The questions run while agents research — no wasted time waiting.**

Ask the user via AskUserQuestion (up to 3 questions in one call):

1. "What programming language are you most comfortable with?" — Options: Python, Java, JavaScript, Go (+ Other). Store as `{lang}`.
2. "Would you like to tailor this to a specific country/location?" — Options: "No, keep it general", "Yes (please specify)" with Other for free text. Store as `{location}` or empty.
3. "Do you have a specific job description you'd like to incorporate?" — Options: "No, use general research", "Yes, I'll paste it". If yes, wait for their paste and store as `{jd}`.

If `{location}` is provided, append it to ALL search queries in the research agents (e.g., `$0 $1 interview questions glassdoor {location}`). This surfaces location-specific interview experiences, office culture, and regional process differences.

If `{jd}` is provided, extract key responsibilities, required skills, and technologies from it. Use these to:
- Prioritize coding exercises that match the JD's technical requirements
- Tailor system design questions to the JD's domain focus
- Add a "JD Alignment" section to the report mapping exercises to JD requirements

### Agent 1: Interview Questions (Glassdoor, Blind, LeetCode, OA platforms)

Launch an Agent (subagent_type: "general-purpose", model: "sonnet") with this prompt:

> Research interview questions for $0 $1 role{if location: in {location}}. Do these searches and fetch the top 2-3 result pages for each:
>
> - Search: `$0 $1 interview questions glassdoor site:glassdoor.com {location}`
> - Search: `$0 $1 interview blind teamblind {location}`
> - Search: `$0 $1 interview questions levels.fyi`
> - Search: `$0 $1 online assessment OA leetcode questions`
> - Search: `$0 interview Codility OR CoderPad OR HackerRank test`
>
> If {location} was provided, also search: `$0 {location} office interview process`
>
> If you find references to specific platforms (Codility, CoderPad) or LeetCode problems, do follow-up searches for those.
>
> Return a structured summary:
> - SPECIFIC coding questions (with source URL, date, difficulty)
> - SPECIFIC system design questions (with source URL, date)
> - SPECIFIC behavioral questions (with source URL)
> - Interview process details (stages, timeline, platform used)
> - Online assessment / take-home details
> - LeetCode problem numbers referenced
>
> Be thorough. Fetch aggressively. Never fabricate questions.

### Agent 2: Community Sources (Prepfully, Reddit, InterviewQuery)

Launch an Agent (subagent_type: "general-purpose", model: "sonnet") with this prompt:

> Research interview questions for $0 $1 role{if location: in {location}} from community sources. Do these searches and fetch the top 2-3 result pages for each:
>
> - Search: `$0 $1 interview questions prepfully`
> - Search: `$0 $1 interview questions interviewquery`
> - Search: `$0 $1 interview experience reddit cscareerquestions {location}`
> - Search: `$0 system design interview question design OR scale OR architecture`
>
> If {location} was provided, also search: `$0 $1 interview {location} experience reddit`
>
> Return a structured summary:
> - SPECIFIC coding questions (with source URL, date, difficulty)
> - SPECIFIC system design questions (with source URL, date)
> - SPECIFIC behavioral questions (with source URL)
> - Any take-home / OA details
>
> Be thorough. Fetch aggressively. Never fabricate questions.

### Agent 3: Company Engineering & Tech Stack

Launch an Agent (subagent_type: "general-purpose", model: "sonnet") with this prompt:

> Research the engineering culture and tech stack for $0{if location: , specifically the {location} office}. Do these searches and fetch the top result pages:
>
> - Search: `$0 engineering blog`
> - Search: `$0 tech stack architecture infrastructure`
> - Search: `$0 $1 job description responsibilities {location}`
> - Search: `$0 $1 interview process 2025 OR 2026`
>
> If {location} was provided, also search: `$0 {location} office engineering team`
>
> If {jd} was provided, here is the job description to incorporate:
> ```
> {jd}
> ```
> Extract: key technologies, required skills, team focus areas, and specific responsibilities. Include these in your summary.
>
> Return a structured summary:
> - Complete tech stack: Backend, Databases, Infrastructure, Frontend
> - Architecture patterns
> - Engineering culture (deploy frequency, team structure, values)
> - Interview process from official sources
> - Notable engineering blog topics

## Step 2: Identify Interview Rounds

After ALL 3 agents return and the user has answered, **first identify the company's actual interview rounds** from the research. Do NOT assume a fixed structure. Different companies use different rounds.

Common round types (use only what the research confirms):

| Round Type | Slug | Description |
|-----------|------|-------------|
| Online Assessment | `online_assessment` | HackerRank/Codility/CodeSignal timed test |
| Coding | `coding` | Live coding — algorithms, data structures, implementation |
| Practical Coding | `practical_coding` | Business-logic-heavy coding, production-quality code |
| Bug Bash / Debugging | `debugging` | Fix bugs in an unfamiliar codebase |
| Integration | `integration` | Call real APIs, parse docs, integrate into existing code |
| System Design | `system_design` | Architecture, distributed systems, database design |
| API Design | `api_design` | Design REST/GraphQL APIs, HTTP semantics, versioning |
| Take-Home Project | `take_home` | Multi-hour project done asynchronously |
| Pair Programming | `pair_programming` | Code together with interviewer on a feature |
| Domain-Specific | `domain_{name}` | SQL, ML, data pipelines, mobile, etc. |
| Behavioral | `behavioral` | Culture fit, STAR stories, values alignment |
| Presentation | `presentation` | Present past work or solve a problem live (Staff+) |
| Hiring Manager | `hiring_manager` | Career goals, team fit, leadership |

**Create exercises ONLY for rounds that the research confirms exist for this company + role.** If the company has a "Bug Bash" round, create debugging exercises. If they have an "Integration" round, create API integration exercises. Don't create system design exercises if the company doesn't have that round.

## Step 3: Generate Output Directory

**CRITICAL: Maximize parallelism when writing files. Use multiple Write tool calls in a SINGLE message for all independent files. Do NOT write files one at a time sequentially.**

Directory structure (round folders are DYNAMIC — based on Step 2):

```
reports/{company_snake_case}_{role_snake_case}/
├── README.md              # Overview + how to use this package
├── report.md              # Full interview prep report
├── plan.md                # Study plan with time estimates
├── exercises/
│   ├── README.md          # Exercise index with difficulty + recommended order
│   ├── {round_slug_1}/    # e.g., practical_coding/
│   │   ├── 01_problem_name.{ext}
│   │   ├── 01_problem_name_solution.{ext}
│   │   └── ...
│   ├── {round_slug_2}/    # e.g., debugging/
│   │   ├── 01_exercise_name.md
│   │   └── ...
│   ├── {round_slug_3}/    # e.g., system_design/
│   │   ├── 01_topic_name.md
│   │   └── ...
│   └── {round_slug_N}/    # e.g., behavioral/
│       └── behavioral_prep.md
```

### report.md

Full interview prep report with these sections:

1. **TL;DR** — 3-4 sentences: stages, timeline, difficulty, the single most important thing to know.
2. **Interview Process** — Table: Stage | Format | Duration | What to Expect. Include timeline, platform. This table should reflect the ACTUAL rounds this company uses — not a generic template.
3. **Actual Questions Reported by Candidates** — The core section. Organize by the company's actual rounds (NOT by a fixed coding/SD/behavioral split). Each round gets its own subsection with:
   - Table of specific questions (with source URL, date, difficulty)
   - What this round evaluates
   - If few questions found for a round, say so honestly with count.
4. **Topics & Patterns** — Per round: what skills, patterns, and knowledge areas are tested. Include anything unique to this company's process.
5. **Tech Stack** — Backend, Databases, Infrastructure, Frontend. Architecture patterns.
6. **JD Alignment** (only if `{jd}` was provided) — Table mapping each JD requirement to specific exercises and prep activities.
7. **Location Notes** (only if `{location}` was provided) — Location-specific details: office culture, local process differences.
8. **Sources** — All URLs as markdown links.

### plan.md

A concrete study plan organized by the company's actual interview rounds:

```markdown
# Interview Prep Plan: $0 $1

## Overview
- Total estimated prep time: X hours
- Recommended timeline: X days/weeks
- Interview rounds: {list the actual rounds}
- Priority order: what to study first

## Week-by-Week Plan

### Week 1: {Most important round type}
| Day | Activity | Time | Details |
|-----|----------|------|---------|
| 1 | Exercise 01: {name} | Xh | ... |
| ... | ... | ... | ... |

### Week 2: {Next round type}
...

### Week N: Mock Interviews + Polish
...

## Readiness Checklist
(One checklist item per round — dynamically generated)
- [ ] {Round-specific readiness criteria}
- [ ] Can explain company's tech stack and architecture
- [ ] Have used the product and formed opinions about it
- [ ] Can answer "Why $0?" authentically
```

Time estimates per exercise type:
- Coding exercise (any type): **1h solving + 30min reviewing solution + 30min edge cases = 2h**
- Debugging exercise: **1h practice + 30min studying methodology = 1.5h**
- Integration exercise: **1h practice + 30min API doc reading drill = 1.5h**
- System design exercise: **1h self-attempt + 1h studying reference + 30min verbal walkthrough = 2.5h**
- API design exercise: **1h self-attempt + 1h studying reference = 2h**
- Behavioral prep: **2h total** (writing STAR stories + practicing delivery)
- Company research: **1-2h** (using product, reading eng blog)

### Exercise Templates By Round Type

**Use the template that matches each round. If the company has a round not listed here, create an appropriate exercise format for it.**

#### Coding rounds (coding, practical_coding, online_assessment)

For EACH specific question found, create an exercise file in `{lang}`:

1. **Problem statement** as a docstring/comment — clear, self-contained (derived from real interview question)
2. **Starter code** — function signature(s) with types, `# TODO` markers
3. **Test cases** — at least 5 tests (including edge cases) runnable with `pytest` / language test framework
4. **Hints** — 3 progressive hints: `# HINT 1: ...`, `# HINT 2: ...`, `# HINT 3: ...`
5. **Complexity targets** — what time/space complexity the interviewer expects

Separate solution file with:
1. Clean, well-commented solution
2. Complexity analysis
3. **Common interviewer follow-ups**
4. **What interviewers look for** — clean code, naming, edge cases, testing
5. Alternative approaches with tradeoffs

#### Debugging rounds (debugging, bug_bash)

For EACH confirmed debugging scenario, create a markdown exercise:

1. **Round format** — What to expect (duration, tools allowed, codebase type)
2. **Confirmed codebases used** — Which OSS projects appear in this round
3. **Confirmed bug types** — Categorized list of bugs candidates encountered
4. **Debugging methodology drill** — Step-by-step approach the interviewer evaluates:
   - How to read unfamiliar code quickly
   - How to reproduce from a failing test
   - When to use print vs. debugger vs. stack trace
   - How to communicate your reasoning
5. **Practice exercises** — 3-5 practice drills:
   - Clone a specific OSS repo, find a real bug from its git history, fix it
   - Each with: repo URL, commit to checkout, what to look for, time limit
6. **Common mistakes** — What weak candidates do wrong
7. **What interviewers look for** — Systematic approach over speed, hypothesis-driven debugging

#### Integration rounds (integration)

For EACH confirmed integration scenario, create a markdown exercise:

1. **Round format** — Duration, what's provided, what's allowed (docs, internet)
2. **Skills tested** — HTTP calls, JSON parsing, reading unfamiliar API docs, file I/O
3. **Practice exercises** — 3-5 drills:
   - Call a real public API (e.g., Stripe test mode, GitHub API), parse response, store results
   - Each with: API to use, task description, time limit, expected deliverable
4. **What makes this round unique** — "0% LeetCode, 100% on-the-job skills"
5. **Common mistakes** — Not reading docs carefully, over-engineering, not testing
6. **Tips from candidates** — Speed of doc reading matters as much as coding speed

#### System Design rounds (system_design)

For EACH question, create a markdown file with:

1. **The prompt** — exactly as asked in the interview
2. **Time budget** — how to spend 45 minutes on this question
3. **Clarifying questions to ask** — what a strong candidate asks before designing
4. **Step-by-step framework** — specific to this problem
5. **Key components to draw** — specific diagrams/components
6. **Deep dive areas** — where the interviewer probes, based on company tech stack
7. **Sample answer outline** — strong answer skeleton with right tradeoffs for this company
8. **Common mistakes** — what weaker candidates do wrong
9. **Connection to company's actual architecture** — reference their tech stack/blog posts

#### API Design rounds (api_design)

For EACH question, create a markdown file with:

1. **The prompt** — the API to design
2. **HTTP semantics to demonstrate** — PUT vs PATCH, status codes, idempotency headers
3. **Resource modeling** — entities, relationships, URL structure
4. **Request/response examples** — full JSON examples for each endpoint
5. **Edge cases** — pagination, error responses, rate limiting, versioning
6. **What interviewers look for** — consistency, RESTfulness, developer experience
7. **Connection to company's actual API style** — reference their public API docs

#### Behavioral rounds (behavioral, hiring_manager)

Single file `behavioral_prep.md` with:

1. Every behavioral question found, grouped by theme
2. For each question: what the interviewer is really assessing
3. STAR framework template for each theme
4. Example of a strong vs. weak answer structure
5. Company-specific angles to emphasize (values, culture, operating principles)

#### Other round types

For rounds not listed above (pair_programming, take_home, presentation, domain-specific), create appropriate exercises based on what the research reveals about the format. Always include:
1. What the round looks like (format, duration, tools)
2. What is evaluated
3. Practice exercises that simulate the actual round
4. Tips from candidates who went through it

### exercises/README.md

Index of all exercises, organized by interview round:

```markdown
# Exercise Index

## Round 1: {Round Name} ({duration})
| # | Name | Difficulty | Time Limit | Status |
|---|------|-----------|------------|--------|
| 01 | {name} | Medium | 45 min | [ ] |

## Round 2: {Round Name} ({duration})
| # | Name | Difficulty | Time Limit | Status |
|---|------|-----------|------------|--------|
| 01 | {name} | Hard | 60 min | [ ] |

...

## Recommended Prep Order
1. {Round with most exercises} — start here
2. {Next priority round}
3. ...
```

### README.md (root)

```markdown
# $0 $1 Interview Prep

## Interview Rounds
{List each round the company uses with a one-line description}

## What's Inside
- `report.md` — Full research report with real questions from candidates
- `plan.md` — Week-by-week study plan with time estimates
- `exercises/` — Hands-on practice for each interview round

## How to Use
1. Read `report.md` to understand the full interview process
2. Follow `plan.md` day by day
3. Work through exercises round by round
4. For coding exercises: solve first, then check the solution
5. Ask Claude to review your solution for feedback
6. Track progress with checkboxes in `exercises/README.md`

## Practicing with Claude
Share your solution and ask for feedback. Claude will:
- Review code quality (naming, structure, readability)
- Suggest missing test cases and edge cases
- Point out complexity improvements
- Flag what interviewers specifically look for
- Give a readiness score and next steps
```

## Critical Rules

- **ROUND-DRIVEN STRUCTURE**: Exercise folders and report sections must match the company's ACTUAL interview rounds — never force a generic coding/SD/behavioral split.
- **SPECIFICITY OVER GENERALITY**: Real questions with sources, not generic advice.
- **NEVER fabricate questions**. Only include questions actually found in sources.
- **Always attribute**: every question should have a source link.
- **Recency matters**: prioritize 2024-2026 data. Note dates.
- **Fetch aggressively**: real questions are in page content, not snippets.
- **ALL 3 research agents + AskUserQuestion MUST be launched in a SINGLE message** — this is what makes them parallel.
- **ALL exercise files MUST be written in parallel** — batch all independent Write calls into as few messages as possible. Never write files one-by-one.
- After saving all files, tell the user the report is ready and show only the **TL;DR** section from report.md. Do NOT re-output the full report.
