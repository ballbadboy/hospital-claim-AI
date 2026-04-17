# Hermes Agent — สปสช Knowledge Wiki

## Mission

This is an LLM-maintained knowledge wiki about **สปสช (สำนักงานหลักประกันสุขภาพแห่งชาติ)** — Thailand's National Health Security Office.

Sources are YouTube videos, documents, and web content about สปสช policies, procedures, medical billing, and healthcare systems. The LLM (Hermes Agent) maintains all wiki pages. You read; Hermes writes.

---

## Directory Structure

```
สปสช/
├── CLAUDE.md           ← This file (schema + instructions for Hermes)
├── index.md            ← Content catalog (updated on every ingest)
├── log.md              ← Chronological activity log (append-only)
├── raw/                ← Immutable source data (READ ONLY — never modify)
│   └── <video-id>/     ← YouTube extraction output
│       ├── metadata.json
│       ├── transcript_*.txt
│       ├── transcript_timestamps.json
│       ├── frames/
│       └── frame_index.json
└── wiki/               ← LLM-generated pages (Hermes writes, you read)
    ├── overview.md     ← สปสช master overview
    ├── entities/       ← Organizations, programs, people
    ├── concepts/       ← Policies, procedures, medical terms
    ├── sources/        ← One summary page per video/document
    └── queries/        ← Answered questions filed as reusable pages
```

---

## Page Types

### `wiki/sources/<video-id>.md`
One page per ingested source. Format:
```markdown
---
type: source
video_id: <id>
title: <title>
channel: <channel>
url: https://youtu.be/<id>
date_ingested: YYYY-MM-DD
duration: <MM:SS>
topics: [topic1, topic2]
---

# <Title>

**Channel:** | **Duration:** | **Ingested:**

## Summary
[2-3 paragraph overview]

## Key Points
- ...

## Topics Covered
- [[concept/name]] — brief note
- ...

## Timestamps
| Time | Topic |
|------|-------|
| 00:00 | ... |

## Source
[Watch on YouTube](https://youtu.be/<id>)
```

### `wiki/concepts/<name>.md`
One page per concept/policy/procedure. Format:
```markdown
---
type: concept
tags: [policy, billing, claim, etc.]
sources: [video-id-1, video-id-2]
last_updated: YYYY-MM-DD
---

# <Concept Name>

## Definition
[Clear explanation]

## How It Works
[Process/procedure]

## Related Concepts
- [[concept/related]] — why related

## Source Videos
- [[sources/video-id]] — what this video covers about this concept
```

### `wiki/entities/<name>.md`
Organizations, departments, programs. Format:
```markdown
---
type: entity
category: [organization|program|department|person]
sources: [video-id-1]
last_updated: YYYY-MM-DD
---

# <Entity Name>

## Overview
[What it is]

## Role in สปสช System
[How it relates]

## Related
- [[concept/...]]
- [[entity/...]]
```

### `wiki/queries/<slug>.md`
Answered questions filed for future reuse:
```markdown
---
type: query
question: "exact question asked"
date: YYYY-MM-DD
sources_used: [page1, page2]
---

# Q: <Question>

## Answer
[Full answer with citations]

## Sources
- [[sources/...]]
```

---

## Operations

### INGEST — Adding a new YouTube source

When user runs `/hermes ingest <url>`:

1. **Extract** — Run youtube-skill-extractor script to get raw data into `raw/<video-id>/`
2. **Read** — Read `raw/<video-id>/metadata.json`, transcript, frame_index.json
3. **Discuss** — Briefly discuss key takeaways with user (optional, can skip with --auto)
4. **Write source page** — Create `wiki/sources/<video-id>.md`
5. **Update entities** — Find or create entity pages mentioned in video
6. **Update concepts** — Find or create concept pages covered in video
7. **Update index.md** — Add new source + any new pages
8. **Append log.md** — Log entry: `## [YYYY-MM-DD] ingest | <title>`

**A single source should touch 5–15 wiki pages.**

### QUERY — Answering a question

When user runs `/hermes query <question>`:

1. Read `index.md` to find relevant pages
2. Read relevant wiki pages
3. Synthesize answer with citations to source pages
4. Ask user: "File this answer as a wiki page?" → if yes, write `wiki/queries/<slug>.md`
5. Append to log.md: `## [YYYY-MM-DD] query | <question>`

### LINT — Health check

When user runs `/hermes lint`:

1. Read all pages in wiki/
2. Check for:
   - Orphan pages (no inbound links)
   - Stale claims (newer sources contradict)
   - Missing concept pages (mentioned but not created)
   - Missing cross-references
   - Inconsistent terminology
3. Report findings + fix where possible
4. Log: `## [YYYY-MM-DD] lint | <N issues found, M fixed>`

### STATUS — Show wiki stats

When user runs `/hermes status`:
- Count pages by type
- Show last 5 log entries
- List sources ingested
- Suggest next actions

---

## Conventions

- All pages use Thai or English matching the source video language
- Wikilinks use `[[path/name]]` format (Obsidian compatible)
- Frontmatter is YAML — required on every page
- Never modify files in `raw/` — it is the immutable source of truth
- Cross-reference liberally — links are the value of a wiki
- When concepts appear in multiple sources, consolidate on the concept page

---

## สปสช Domain Knowledge

Key entities to track:
- สปสช (สำนักงานหลักประกันสุขภาพแห่งชาติ) — the main organization
- บัตรทอง (Gold Card / UC Scheme) — universal coverage scheme
- โรงพยาบาล (Hospitals) — service providers
- กองทุนหลักประกันสุขภาพ — health security fund
- e-Claim / e-Prior Auth — digital claim systems

Key concept categories:
- `billing` — การเบิกจ่าย, claim submission
- `policy` — นโยบาย, สิทธิ์
- `procedure` — ขั้นตอนการทำงาน
- `it-system` — ระบบ IT, software
- `fund` — กองทุน, งบประมาณ

---

## YouTube Extractor Integration

Raw data lives at:
`~/.claude/skills/youtube-skill-extractor/output/<video-id>/`

Or copied to:
`raw/<video-id>/`

To extract a new video:
```bash
~/.claude/skills/youtube-skill-extractor/scripts/extract.sh "<youtube-url>" "$(pwd)/raw"
```

This puts output directly into `raw/<video-id>/` inside this vault.

---

## log.md Format (important)

Each entry starts with `## [YYYY-MM-DD]` — this makes it grep-able:
```bash
grep "^## \[" log.md | tail -10   # last 10 operations
grep "ingest" log.md               # all ingests
grep "query" log.md                # all queries
```
