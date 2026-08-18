# Story Safari

A small storytelling site that narrates stories from Indian epics and folklore for kids, using AI-generated voice narration with expressive, emotional delivery. Built as a personal project to get hands-on with applied AI — content generation, text-to-speech, image generation, and the operational side of running an AI-assisted pipeline — rather than as a commercial product.

**Live site:** https://guruduttadongre.github.io/mythic-tales/

## What this is

Each story is adapted from Indian mythology and folklore, narrated by an AI voice with emotion and expression matched to the moment, illustrated with an AI-generated thumbnail, and presented with synced, progressively-revealed text as the narration plays.

## What's built so far

- **3 complete stories**, each fully narrated with expressive AI voice, synced text-reveal, a custom audio player, and its own AI-generated illustration
- A static site (plain HTML/CSS/JS — no framework) with a homepage story grid and individual story pages, all generated from a reusable template
- A four-stage automated content pipeline, built on GitHub Actions and reviewed via pull requests at every stage:
  1. Story drafting from a theme/context prompt (OpenAI)
  2. Emotion tagging and Indian-name pronunciation review (OpenAI)
  3. Thumbnail image generation (OpenAI)
  4. Final audio generation, page build, and homepage update (ElevenLabs + custom scripts), with a manual pre-publish listen-and-review step
- A human approval checkpoint before every AI-generated output (text, audio, image) is used — nothing reaches the live site without direct review
- Automated deployment via GitHub Actions to GitHub Pages on every push — no manual publish step

## How content gets made

Content generation happens **offline, in advance** — nothing is generated live when a visitor uses the site. A visitor only ever streams pre-generated, pre-reviewed audio, images, and static pages. See the [decision log](docs/decision-log.md) for the full architecture reasoning, including a few honest mistakes made and fixed along the way.

## What's planned

- Additional stories in the catalog
- Flipping the final publish stage from manually-triggered to fully automatic, once proven reliable
- A one-time documented AWS deployment exercise (S3, CloudFront, Lambda, Terraform) as a separate infrastructure exploration, alongside the permanent GitHub Pages hosting

## Documentation

- [`docs/decision-log.md`](docs/decision-log.md) — every significant architecture and tooling decision made during this project, including the reasoning, alternatives considered, and honest mistakes along the way
- `docs/case-study.md` *(coming soon)* — a narrative write-up of the full build

## Tech stack

**In use:**
Plain HTML/CSS/JS · ElevenLabs (text-to-speech) · OpenAI API (story generation, tagging, image generation) · GitHub Actions (CI/CD and content pipeline orchestration) · GitHub Pages (hosting)

**Built with the help of:**
Claude (Anthropic) —  with all architecture and AI-governance decisions human-moderated and approved throughout this build
