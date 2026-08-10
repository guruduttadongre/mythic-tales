# Decision Log

This log tracks the significant architecture, tooling, and scope decisions made
during this project, along with the alternatives considered and the reasoning
behind each choice. It's maintained as the project is built, not reconstructed
afterward — the goal is an honest record of judgment calls, not a polished
after-the-fact narrative.

---

## Decision: Two-phase architecture (offline content generation vs. live serving)

**Choice:** Split the system into a Content Creation phase (done once, offline)
and a Content Serving phase (fully static, triggered by every visitor).
No AI inference happens at runtime when a visitor uses the site.

**Alternatives considered:** Generate narration on-demand per visitor request
(dynamic TTS call triggered by page load or button click).

**Why:** Pre-generating and caching audio removes runtime dependency on any
AI vendor's uptime, keeps marginal cost per visitor near zero (static file
serving vs. metered API calls), guarantees instant playback with no
generation-wait spinner, and — since this is a children's site — ensures
every word a child hears was reviewed in advance rather than generated live
in front of them. This removes an entire class of runtime content-moderation
risk by construction rather than by policy.

**Trade-off accepted:** No dynamic personalization (e.g., inserting a child's
name into the story) in v1, since that would reintroduce live generation.
Documented as a possible future addition, not built now.

**Date:** Aug 2026

---

## Decision: Language scope — 5 stories in English, 1 flagship story trilingual

**Choice:** Build all 5 stories in English. Pick one flagship story and
additionally produce it in Hindi and Kannada.

**Alternatives considered:** All 5 stories in all 3 languages (English, Hindi,
Kannada) — 15 full content builds.

**Why:** The full 5×3 matrix triples Phase A work (translation review, SSML
annotation, TTS generation, timestamp data) for every story, not just cost —
review time and quality control were the binding constraint, not cost. A
single trilingual flagship story proves the content pipeline is
language-agnostic without tripling review burden across the whole catalog,
and produces a more precise claim: the pipeline was validated as
language-agnostic, with the rest of the catalog scoped for straightforward
localization — rather than implying full multilingual coverage that wasn't
the actual goal of this build.

**Date:** Aug 2026

---

## Decision: Git workflow — direct commits to main, no feature branches/PRs

**Choice:** Commit directly to the main branch throughout the project, with a
high bar on commit quality (one logical change per commit, descriptive
messages, a history that reads as a sensible build order). No feature
branches or pull requests.

**Alternatives considered:** Feature-branch + pull-request workflow, even as
a solo contributor.

**Why:** Branch/PR discipline earns its value when there's real risk to
manage — multiple contributors, a production system where main must stay
deployable, or a CI pipeline gating merges. None of that applies to a
solo-built static content site. A PR-to-self demonstrates familiarity with
git mechanics, not judgment, and there's no second reviewer to make the
review step meaningful. Effort was better spent on architecture, cost
control, and infrastructure-as-code, rather than process ceremony that
doesn't reflect an actual production constraint.

**Date:** Aug 2026

---

## Decision: Frontend — plain HTML/CSS/JS, no framework

**Choice:** Build the site with plain HTML, CSS, and vanilla JavaScript.
No React, Next.js, or other framework.

**Alternatives considered:** React/Next.js.

**Why:** This is a content site (5 static story pages plus audio playback),
not an interactive application. A framework adds build tooling, dependencies,
and abstraction layers that make debugging harder without buying much for
this scope. Plain HTML/CSS/JS is directly readable — every line is exactly
what runs in the browser — which also matters for a repo meant to be clean
and understandable.

**Date:** Aug 2026

---

## Decision: Hosting and cloud provider — AWS (S3 + CloudFront + Lambda)

**Choice:** Host the static site on AWS (S3 for storage, CloudFront as CDN),
with a small AWS Lambda function to proxy calls to the TTS vendor's API
during content generation (Phase A), keeping the API key server-side.

**Alternatives considered:** Vercel or Netlify.

**Why:** An AWS account already existed, avoiding a new vendor account.
Keeping hosting and infrastructure-as-code in the same cloud keeps the
architecture and decision log coherent — one cloud story, not a split
between "AWS for infra" and "Vercel for the site."

**Date:** Aug 2026

---

<!-- Add new entries above this line as decisions are made. -->