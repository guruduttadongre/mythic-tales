# Mythic Tales

A small storytelling site that narrates stories from Indian epics for kids, using AI-generated voice narration with expressive, emotional delivery. Built as a personal project to get hands-on with applied AI — content generation, text-to-speech, and the operational side of running an AI-assisted pipeline — rather than as a commercial product.

**Live site:** https://guruduttadongre.github.io/mythic-tales/

## What this is

Each story is adapted from Indian mythology (Ramayana, Mahabharata), narrated by an AI voice with emotion and expression matched to the moment, and presented with synced, progressively-revealed text as the narration plays. The catalog is intentionally small — a handful of stories, not a large content library.

## What's built so far

- **1 complete story** — *Hanuman's Leap of Faith*, fully narrated with expressive AI voice, synced text-reveal, and a custom audio player
- A static site (plain HTML/CSS/JS — no framework) with a homepage story grid and individual story pages
- An audio-generation pipeline: story text → emotion-tagged narration → text-to-speech with accurate pronunciation of Sanskrit-origin names → sentence-level timing data for text sync
- Automated deployment via GitHub Actions to GitHub Pages on every push — no manual publish step

## How content gets made

Content generation happens **offline, in advance** — nothing is generated live when a visitor uses the site. A visitor only ever streams pre-generated, pre-reviewed audio and static pages. See the [decision log](docs/decision-log.md) for the full reasoning behind this and other architecture choices.

## What's planned

- The remaining 4 stories in the catalog
- A semi-automated content pipeline (story generation → tagging → image → final review, each with a human approval step) using GitHub Actions
- A one-time documented AWS deployment exercise (S3, CloudFront, Lambda, Terraform) as a separate infrastructure exploration, alongside the permanent GitHub Pages hosting

## Documentation

- [`docs/decision-log.md`](docs/decision-log.md) — every significant architecture and tooling decision made during this project, including the reasoning, alternatives considered, and a couple of honest mistakes along the way
- `docs/case-study.md` *(coming soon)* — a narrative write-up of the full build

## Tech stack

Plain HTML/CSS/JS · ElevenLabs (text-to-speech) · GitHub Actions (CI/CD) · GitHub Pages (hosting)
