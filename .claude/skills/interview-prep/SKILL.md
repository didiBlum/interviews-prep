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

## Step 2: Generate Output Directory

After ALL 3 agents return and the user has answered the language question, merge and deduplicate findings. Create the full output directory.

**CRITICAL: Maximize parallelism when writing files. Use multiple Write tool calls in a SINGLE message for all independent files. Batch all coding exercise files + solution files + system design files + behavioral prep + READMEs + report + plan into as few messages as possible. Do NOT write files one at a time sequentially.**

Directory structure:

```
reports/{company_snake_case}_{role_snake_case}/
├── README.md              # Overview + how to use this package
├── report.md              # Full interview prep report
├── plan.md                # Study plan with time estimates
├── exercises/
│   ├── README.md          # Exercise index with difficulty + recommended order
│   ├── coding/
│   │   ├── 01_problem_name.{ext}           # Starter code + tests
│   │   ├── 01_problem_name_solution.{ext}  # Solution
│   │   ├── 02_problem_name.{ext}
│   │   ├── 02_problem_name_solution.{ext}
│   │   └── ...
│   ├── system_design/
│   │   ├── sd_01_topic_name.md             # Full SD exercise
│   │   ├── sd_02_topic_name.md
│   │   └── ...
│   └── behavioral/
│       └── behavioral_prep.md              # All behavioral questions + STAR frameworks
```

### report.md

Full interview prep report with these sections:

1. **TL;DR** — 3-4 sentences: stages, timeline, difficulty, the single most important thing to know.
2. **Interview Process** — Table: Stage | Format | Duration | What to Expect. Include timeline, platform.
3. **Actual Questions Reported by Candidates** — The core section. Organized by:
   - Coding Questions (table: question, difficulty, LC equivalent, round, source, date)
   - System Design Questions (table: question, scope, source, date)
   - Behavioral Questions (list with source)
   - Take-Home / OA details
   - If few questions found, say so honestly with count.
4. **Topics & Patterns** — DS/algorithms tested, SD themes, behavioral themes, unique aspects.
5. **Tech Stack** — Backend, Databases, Infrastructure, Frontend. Architecture patterns.
6. **JD Alignment** (only if `{jd}` was provided) — Table mapping each JD requirement to specific exercises and prep activities. Highlight gaps where no exercise covers a JD requirement.
7. **Location Notes** (only if `{location}` was provided) — Location-specific details: office culture, local interview process differences, team composition at that location.
8. **Sources** — All URLs as markdown links.

### plan.md

A concrete study plan with time estimates. Structure:

```markdown
# Interview Prep Plan: $0 $1

## Overview
- Total estimated prep time: X hours
- Recommended timeline: X days/weeks
- Priority order: what to study first

## Week-by-Week Plan

### Week 1: Coding Fundamentals
| Day | Activity | Time | Details |
|-----|----------|------|---------|
| 1 | Exercise 01: {name} | 1.5h | 1h solve + 0.5h review solution & edge cases |
| 1 | Exercise 02: {name} | 1.5h | 1h solve + 0.5h review |
| 2 | ... | ... | ... |

### Week 2: System Design
| Day | Activity | Time | Details |
|-----|----------|------|---------|
| 1 | SD Exercise 01: {name} | 2h | 1h self-attempt + 1h study reference answer |
| ... | ... | ... | ... |

### Week 3: Behavioral + Mock
| Day | Activity | Time | Details |
|-----|----------|------|---------|
| 1 | Prepare STAR stories | 2h | Write out 5 stories covering ownership, failure, conflict |
| 2 | Mock interview practice | 1.5h | Time yourself: 45min coding + debrief |
| ... | ... | ... | ... |

## Readiness Checklist
- [ ] Can solve all coding exercises within time limit
- [ ] Can articulate system design for each SD question (whiteboard 45 min)
- [ ] Have 5+ STAR stories covering all behavioral themes
- [ ] Can explain company's tech stack and architecture
- [ ] Have used the product and formed opinions about it
- [ ] Can answer "Why $0?" authentically
```

Time estimates per exercise type:
- Coding exercise: **1h solving + 30min reviewing solution + 30min practicing clean code & edge cases = 2h**
- System design exercise: **1h self-attempt + 1h studying reference answer + 30min practicing verbal walkthrough = 2.5h**
- Behavioral prep: **2h total** (writing STAR stories + practicing delivery)
- Company research: **1-2h** (using product, reading eng blog)

### exercises/coding/

For EACH specific coding question found in the report, create an exercise file in `{lang}`. Each file:

1. **Problem statement** as a docstring/comment — clear, self-contained (derived from real interview question)
2. **Starter code** — function signature(s) with types, `# TODO` markers
3. **Test cases** — at least 5 tests (including edge cases) runnable with `pytest` / language test framework
4. **Hints** — 3 progressive hints as comments: `# HINT 1: ...`, `# HINT 2: ...`, `# HINT 3: ...`
5. **Complexity targets** — what time/space complexity the interviewer expects

Separate solution file with:
1. Clean, well-commented solution
2. Complexity analysis
3. **Common interviewer follow-ups** — "what if the input is very large?", "how would you parallelize this?"
4. **What interviewers look for** — clean code practices, variable naming, edge case handling, testing approach
5. Alternative approaches with tradeoffs

### exercises/system_design/

For EACH system design question, create a markdown file with:

1. **The prompt** — exactly as asked in the interview
2. **Time budget** — how to spend 45 minutes on this question
3. **Clarifying questions to ask** — what a strong candidate asks before designing
4. **Step-by-step framework** — specific to this problem
5. **Key components to draw** — specific diagrams/components
6. **Deep dive areas** — where the interviewer probes, based on company tech stack
7. **Sample answer outline** — strong answer skeleton with right tradeoffs for this company
8. **Common mistakes** — what weaker candidates do wrong
9. **Connection to company's actual architecture** — reference their tech stack/blog posts

### exercises/behavioral/

Single file `behavioral_prep.md` with:

1. Every behavioral question found, grouped by theme
2. For each question: what the interviewer is really assessing
3. STAR framework template for each theme
4. Example of a strong vs. weak answer structure
5. Company-specific angles to emphasize (e.g. ownership culture, data-driven decisions)

### exercises/README.md

Index of all exercises:

```markdown
# Exercise Index

## Coding Exercises
| # | Name | Difficulty | Time Limit | Interview Round | Status |
|---|------|-----------|------------|-----------------|--------|
| 01 | {name} | Medium-Hard | 45 min | Round 1 Coding | [ ] |
| 02 | {name} | Medium | 30 min | Round 2 Coding | [ ] |

## System Design Exercises
| # | Topic | Difficulty | Time Budget | Interview Round | Status |
|---|-------|-----------|-------------|-----------------|--------|
| 01 | {name} | Hard | 45 min | Round 3 SD | [ ] |

## Behavioral Prep
| Theme | Questions | Status |
|-------|-----------|--------|
| Ownership | 3 questions | [ ] |
| Failure | 4 questions | [ ] |

## Recommended Order
1. Start with coding exercises (easiest first)
2. Move to system design
3. Behavioral last (can prep in parallel)
```

### README.md (root)

```markdown
# $0 $1 Interview Prep

## What's Inside
- `report.md` — Full research report with real questions from candidates
- `plan.md` — Week-by-week study plan with time estimates
- `exercises/` — Hands-on practice materials

## How to Use
1. Read `report.md` to understand the interview process
2. Follow `plan.md` day by day
3. For each coding exercise: solve it first, then check the solution
4. Ask Claude to review your solution — it will suggest improvements,
   clean code practices, test coverage, and what interviewers look for
5. Track your progress with the checkboxes in `exercises/README.md`

## Practicing with Claude
When you solve an exercise, share your solution and ask for feedback.
Claude will:
- Review code quality (naming, structure, readability)
- Suggest missing test cases and edge cases
- Point out complexity improvements
- Flag what interviewers specifically look for
- Give a readiness score and next steps
```

## Critical Rules

- **SPECIFICITY OVER GENERALITY**: Real questions with sources, not generic advice.
- **NEVER fabricate questions**. Only include questions actually found in sources.
- **Always attribute**: every question should have a source link.
- **Recency matters**: prioritize 2024-2026 data. Note dates.
- **Fetch aggressively**: real questions are in page content, not snippets.
- **ALL 3 research agents + AskUserQuestion MUST be launched in a SINGLE message** — this is what makes them parallel.
- **ALL exercise files MUST be written in parallel** — batch all independent Write calls into as few messages as possible. Never write files one-by-one.
- After saving all files, tell the user the report is ready and show only the **TL;DR** section from report.md. Do NOT re-output the full report.
