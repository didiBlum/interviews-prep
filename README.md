# Interview Prep Generator

A Claude Code skill that generates comprehensive, research-backed interview preparation packages for any company and role.

## What It Does

Running `/interview-prep <company> <role>` will:

1. **Ask** your preferred programming language
2. **Research** the company's interview process across 20+ sources in parallel (Glassdoor, Blind, LeetCode, Reddit, engineering blogs, levels.fyi, Prepfully, and more)
3. **Generate** a complete prep package with:
   - Detailed report of real questions asked by candidates (with sources and dates)
   - Coding exercises with starter code, tests, hints, and full solutions
   - System design exercises with frameworks, sample answers, and company-specific angles
   - Behavioral prep with STAR templates and company culture insights
   - A week-by-week study plan with time estimates

## Quick Start

```bash
# In Claude Code, run:
/interview-prep google senior backend engineer
/interview-prep stripe senior fullstack engineer
/interview-prep microsoft senior backend engineer
```

## Output Structure

```
reports/{company}_{role}/
├── README.md                              # Overview + how to use
├── report.md                              # Full research report
├── plan.md                                # Week-by-week study plan
└── exercises/
    ├── README.md                          # Exercise index with difficulty + order
    ├── coding/
    │   ├── 01_problem_name.{ext}          # Starter code + tests
    │   ├── 01_problem_name_solution.{ext} # Solution + follow-ups
    │   └── ...
    ├── system_design/
    │   ├── sd_01_topic.md                 # Full SD exercise with framework
    │   └── ...
    └── behavioral/
        └── behavioral_prep.md             # Questions + STAR frameworks
```

## How to Use the Output

### Coding Exercises
1. Open the starter file (e.g., `01_lru_cache.java`)
2. Read the problem statement and constraints
3. Implement the solution — tests are included in the file
4. Check the solution file for the optimal approach, follow-ups, and what interviewers look for
5. Share your solution with Claude for personalized feedback

### System Design Exercises
1. Set a 45-minute timer
2. Read only "The Prompt" section
3. Work through the problem on a whiteboard or Excalidraw
4. Compare your approach with the reference answer
5. Practice the verbal walkthrough aloud

### Behavioral Prep
1. Read all reported questions grouped by theme
2. Write 5-6 STAR stories covering the key themes
3. Practice each story in under 2 minutes
4. Adapt stories to the company's specific culture and values

## Example Reports

Two example reports are included:

- **`reports/monday_com_backend_engineer/`** — Python exercises, monday.com-specific system design
- **`reports/microsoft_senior_backend_engineer/`** — Java exercises, Azure-focused system design, compliance-heavy

## How It Works

The skill launches 4 parallel research agents that search:
- Interview databases (Glassdoor, Blind, levels.fyi)
- Community sources (Prepfully, Reddit, InterviewQuery, DataLemur)
- Company engineering blogs and tech stack
- Niche sources (LeetCode tagged problems, OA platforms, system design repositories)

All questions in the report are sourced from real candidate experiences — nothing is fabricated.

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- The skill file at `.claude/skills/interview-prep/SKILL.md`

## Customization

The skill accepts two arguments:
- **Company name** — any company (researched dynamically)
- **Role** — e.g., "senior backend engineer", "staff fullstack", "junior frontend"

Language is chosen interactively and determines the coding exercise file format.
