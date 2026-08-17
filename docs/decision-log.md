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
## Decision: TTS voice — ElevenLabs ("Shardul") for English narration; Hindi/Kannada vendor deferred

**Choice:** Use ElevenLabs, specifically the voice "Shardul," for the English
narration of the flagship story. Voice selection is done per story, matched
to that story's character/tone, rather than fixing one narrator voice for
the whole catalog. The original brief called for an Indian female narrator
voice; this was revised in favor of matching voice to character — a male,
deep, calming voice suited the protagonist of this particular story.
The Hindi/Kannada vendor choice is deliberately left open rather than
defaulting to ElevenLabs across all languages — Sarvam remains a strong
candidate for those languages and will be evaluated on its own merits
(with an actual listening test) before final audio is generated.

**Alternatives considered:** Sarvam AI for all languages (single vendor,
purpose-built for Indian speech); ElevenLabs for all languages (single
vendor, proven quality in English).

**Why:** ElevenLabs demonstrated strong emotional range for English on the
actual story text without heavy prompting. Rather than assuming that result
carries over to Hindi/Kannada, or defaulting to Sarvam untested, the vendor
decision for those languages is deferred to an evidence-based comparison —
avoiding a decision made on assumption rather than a verified listen.

**Trade-off accepted:** A potential two-vendor architecture (two API
integrations, two billing sources) if Hindi/Kannada ultimately goes to
Sarvam, in exchange for using the best-fit voice per language rather than
forcing a single vendor across all three.

**Date:** Aug 2026

## Decision: TTS model — Eleven v3 with audio tags, over Multilingual v2

**Choice:** Generate narration using ElevenLabs' `eleven_v3` model with inline
audio tags (e.g. `[nervous]`, `[determined]`, `[triumphant]`) placed at
emotionally significant points in the text, rather than `eleven_multilingual_v2`
with plain text.

**What happened:** The first full-story generation was run using
`eleven_multilingual_v2` with plain, untagged text — skipping the planned
emotion-annotation step entirely. This produced usable but flat narration
and cost real API credits for a version that didn't reflect the intended
design. It was caught after listening to the output, not before generating
it — a process gap, not a technical one. The story was regenerated correctly
afterward using `eleven_v3` with audio tags, at additional credit cost.

**Why v3 with tags is the right choice going forward:** v3 was purpose-built
for expressive, performance-style

## Decision: Duplicate final audio/timing files into site/, separate from content/

**Choice:** Keep `content/audio/` as the working area where audio is generated
(including intermediate files like tagged text and raw timestamps), and copy
only the final MP3 and sentence-timing JSON into `site/audio/`, which the
website actually references and serves.

**Why:** Local testing revealed that a web server only serves files within
its own root folder — `site/` cannot reach up into `content/` at runtime.
This also anticipates deployment: the eventual hosted site will be whatever
gets uploaded as its own self-contained unit, with no access to files
outside it. Keeping `content/` as the working/source area and `site/` as
the deployable output keeps that separation intentional rather than
accidental.

**Trade-off accepted:** Regenerating a story's audio requires manually
re-copying the updated files into `site/audio/`, or the live site will
keep serving a stale version. A small sync script may be added later to
automate this step.

**Date:** Aug 2026

## Decision: No custom domain; GitHub Pages as primary hosting, AWS as a documented exercise

**Choice:** Do not purchase or manage a custom domain. Use GitHub Pages
(free, using its default subdomain URL) as the sustainable, always-on way
to share a working version of the site. Treat AWS hosting (S3, CloudFront,
Lambda, Terraform) as a separate, documented build-and-tear-down exercise
rather than a permanently running deployment.

**Alternatives considered:** Purchasing a custom domain and running the
site permanently on AWS.

**Why:** A custom domain adds a recurring cost and a renewal obligation for
a project that isn't intended to be actively maintained or expanded on an
ongoing basis. GitHub Pages removes hosting cost and maintenance entirely
while still providing a real, working, shareable link. Running AWS
infrastructure as a one-time, documented exercise (rather than leaving it
live indefinitely) still demonstrates the infrastructure/IaC work without
the ongoing cost or operational burden of a project that isn't being
actively grown. This also reflects a deliberate choice to keep the project's
polish proportional to its actual scope — a small, honestly-labeled catalog
does not need to look or run like a production product.

**Date:** Aug 2026

## Decision: Semi-automated content pipeline with mandatory human approval gate

**Choice:** Automate the story-generation pipeline (tagging, TTS, timestamp
generation, page build, deployment) using GitHub Actions, but require an
explicit human approval step between automated tag generation and audio
generation/publishing, using GitHub's environment protection rules.

**Alternatives considered:** Fully automated pipeline with no human review
of LLM-generated tags before publishing.

**Why:** Automating tag generation introduces an LLM step with no guarantee
of its output — since the site is intended for children, there is a real
risk that unintended or inappropriate content could be generated and
published without anyone reviewing it first. A mandatory approve/reject
checkpoint keeps a human as the final gate on what a child can access,
preserving the project's original two-phase design principle (every word a
child hears is reviewed before it's ever generated) even as the surrounding
process is automated.

**Date:** Aug 2026

## Decision: Story generation as the first automated pipeline stage

**Choice:** Built a GitHub Actions workflow (`generate-story.yml`), triggered
manually via `workflow_dispatch` with a form (theme, word count, context,
age range, source epic). It calls the OpenAI API to draft a story and opens
a pull request for human review, rather than committing directly to main.

**Why:** Matches the human-in-the-loop principle established earlier -
AI-generated content is never trusted directly into the live site. The PR
mechanism was chosen specifically because it allows direct in-browser
editing of the draft before approval, not just a binary accept/reject.

**Date:** Aug 2026
<!-- Add new entries above this line as decisions are made. -->
## Decision: Automated pipeline architecture with human approval at every AI-touched stage

**Choice:** Built a four-stage automated content pipeline using GitHub
Actions and pull requests as the review mechanism: (1) story generation
from a theme/context form, (2) emotion tagging and name-pronunciation
proposal, (3) thumbnail image generation, (4) final audio/page/homepage
build. Each stage opens its own pull request; nothing proceeds to the
next stage or reaches the live site without an explicit merge decision.
The final stage is deliberately kept manually-triggered (not fully
automatic) so it can be observed and debugged directly while still being
validated.

**Why:** Automating tag generation, image generation, and story drafting
all introduce AI outputs with no inherent guarantee of quality or
appropriateness - given the site is for children, an explicit human
checkpoint before each stage's output is used stays a non-negotiable
part of the design, even as the mechanical process around it is fully
automated. Using pull requests (rather than a custom approval UI) means
review, direct editing, and rejection are all native, well-understood
GitHub actions - no additional tooling required.

**Date:** Aug 2026

---

## Decision: Voice registry - collapsed from three category-matched voices to one

**Choice:** Originally built a voice-selection scheme matching three
ElevenLabs voices to story categories (Shardul for Ramayana/Mahabharata,
Viraj for Puranas, Keshavi for folklore/default). After testing a
Puranic story with Viraj, his performance under eleven_v3 sounded less
authentically Indian-accented than expected, even before testing with
corrected pronunciation data. Keshavi was tested directly against the
same names and handled Indian pronunciation and accent naturally,
without needing Devanagari pronunciation assistance at all. Based on
this, the registry was changed so all three categories point to Keshavi,
rather than keeping three distinct voices.

**Alternatives considered:** Testing Viraj again with the corrected
pronunciation map before deciding; keeping a multi-voice registry with
a different second/third voice.

**Why:** Once Keshavi was shown to handle names and accent well without
extra help, on both an epic-toned excerpt and a Puranic story, using a
single reliable voice was preferred over maintaining voice-specific
quality differences and per-voice pronunciation dependencies. The
registry structure itself was kept intact (not deleted) so a different
voice can be reintroduced for a specific category later without
re-architecting the selection logic.

**Date:** Aug 2026

---

## Decision: Devanagari pronunciation substitution made an optional toggle, default off

**Choice:** The pronunciation-map substitution step (replacing English
spellings of Indian names with Devanagari before sending text to TTS)
is now controlled by a toggle (USE_PRONUNCIATION_MAP, default false)
rather than always running.

**Why:** This step was originally required because earlier voices
(Shardul, Viraj) produced noticeably better pronunciation with
Devanagari assistance. Keshavi, the now-default voice, performs well
without it. Rather than removing the substitution capability outright,
it was kept as an optional, per-run toggle - preserving the option to
re-enable it if a future voice needs it, without carrying its
maintenance overhead (reviewing and merging proposed names) by default.

**Date:** Aug 2026

---

## Decision: Thumbnail style guide evolved through three iterations

**Choice:** The default AI-image style guide changed twice during
testing: (1) flat/minimal illustration matching the site's original
CSS aesthetic, (2) a richly detailed painterly picture-book style after
the flat version felt visually underwhelming, (3) a photorealistic,
cinematic style after direct feedback that painterly still didn't match
the desired quality bar. The final version explicitly includes
child-safety guardrails in the prompt itself (avoid horror, gore,
frightening imagery, violence - favor calm/reverent treatment of
dramatic story moments) after an early realistic-style test produced an
image with intense, inappropriate elements (a demon army, fire, violent
imagery) for a children's story.

**Why:** Visual style was refined based on direct, iterative comparison
rather than settled on first attempt - consistent with the project's
overall practice of testing before committing to a default. The safety
language was added as a permanent, structural part of the prompt (not
a one-off fix) after a real instance of it being needed, so future
dramatic story moments do not require manual catching each time.

**Date:** Aug 2026

---

## Note: A few automation issues found and fixed during live testing

- Workflow permissions: repo defaulted to read-only Actions
  permissions with PR-creation disabled; both had to be manually
  enabled in Settings before any pipeline stage could open a pull
  request, despite the workflow files themselves declaring correct
  permissions.
- Tagging workflow fires on file deletion too: the tag-story
  workflow's trigger (paths: content/drafts/**) cannot distinguish an
  added file from a deleted one - merging a tagging PR (which deletes
  the promoted draft) re-triggers the same workflow, which then fails
  loudly since there's nothing new to process. Not harmful (no incorrect
  PR is opened), but noisy; worth a future fix to exit cleanly instead
  of erroring.
- Stage ordering dependency: the final publish stage assumes a
  story's thumbnail image already exists on main. If the thumbnail
  PR hasn't been merged yet, publishing proceeds anyway and produces a
  page/homepage referencing a nonexistent image file. Currently handled
  by manual ordering discipline (merge thumbnail PR before publish PR),
  not enforced by the pipeline itself.
- Automated proposal step was initially too conservative: the
  tagging stage's proper-noun detection skipped names it judged as
  "common enough" (e.g. Shiva, Amrita, Devas, Asuras), leaving them
  unconverted and contributing to a pronunciation issue. The prompt was
  rewritten to be exhaustive rather than selective.

**Date:** Aug 2026
<!-- Add new entries above this line as decisions are made. -->
