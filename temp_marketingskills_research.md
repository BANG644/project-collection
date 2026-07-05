# Deep Research: coreyhaines31/marketingskills

## 1. Project Overview

| Field | Value |
|-------|-------|
| **Full Name** | coreyhaines31/marketingskills |
| **Stars** | 36,374 (⭐36k+, extremely high) |
| **Forks** | 5,891 |
| **Open Issues** | 45 |
| **Watchers** | 353 |
| **Language** | JavaScript (497KB) + Shell (7.8KB) |
| **License** | MIT |
| **Created** | 2026-01-15T19:45:23Z |
| **Last Updated** | 2026-07-05 (very actively maintained) |
| **Topics** | claude, codex, marketing |
| **Repo Size** | 2,425 KB |
| **Description** | "Marketing skills for Claude Code and AI agents. CRO, copywriting, SEO, analytics, and growth engineering." |
| **Archived** | No |
| **Visibility** | Public |

**Key stat**: 36K+ stars in ~6 months — extraordinary growth rate, one of the fastest-growing AI agent skills repos.

---

## 2. File Tree Structure

```
marketingskills/
├── .claude-plugin/
│   ├── marketplace.json      # Claude Code plugin marketplace manifest
│   └── plugin.json           # Plugin configuration
├── .github/
│   ├── FUNDING.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml
│   │   └── skill-request.yml
│   ├── PULL_REQUEST_TEMPLATE/
│   │   ├── documentation.md
│   │   ├── new-skill.md
│   │   └── skill-update.md
│   ├── scripts/
│   │   └── sync-skills.js     # Automated skill sync script
│   └── workflows/
│       ├── sync-skills.yml    # CI/CD for skill updates
│       └── validate-skill.yml # Validation workflow
├── .gitignore
├── AGENTS.md                  # Guidelines for AI agents
├── CLAUDE.md                  # Same as AGENTS.md (symlink/alias)
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── VERSIONS.md                # Version tracking for all skills
├── validate-skills.sh
├── validate-skills-official.sh
├── skills/                    # ** 46 skills total **
│   ├── ab-testing/
│   │   ├── SKILL.md
│   │   ├── evals/evals.json
│   │   └── references/
│   ├── ad-creative/
│   ├── ads/
│   ├── ai-seo/
│   ├── analytics/
│   ├── aso/
│   ├── churn-prevention/
│   ├── co-marketing/
│   ├── cold-email/
│   ├── community-marketing/
│   ├── competitor-profiling/
│   ├── competitors/
│   ├── content-strategy/
│   ├── copy-editing/
│   ├── copywriting/
│   ├── cro/
│   ├── customer-research/
│   ├── directory-submissions/
│   ├── emails/
│   ├── free-tools/
│   ├── image/
│   ├── launch/
│   ├── lead-magnets/
│   ├── marketing-ideas/
│   ├── marketing-loops/       # NEW v2.6.0 (43 repeatable loops)
│   ├── marketing-plan/
│   ├── marketing-psychology/
│   ├── offers/               # NEW v2.5.0
│   ├── onboarding/
│   ├── paywalls/
│   ├── popups/
│   ├── pricing/
│   ├── product-marketing/    # FOUNDATION skill - read by all others
│   ├── programmatic-seo/
│   ├── prospecting/
│   ├── public-relations/     # NEW v2.4.0
│   ├── referrals/
│   ├── revops/
│   ├── sales-enablement/
│   ├── schema/
│   ├── seo-audit/
│   ├── signup/
│   ├── site-architecture/
│   ├── sms/
│   ├── social/
│   └── video/
├── tools/
│   ├── REGISTRY.md          # Master tool index (70+ tools)
│   ├── clis/                # 51 zero-dependency Node.js CLI tools
│   │   ├── ga4.js, ahrefs.js, semrush.js, apollo.js,
│   │   ├── meta-ads.js, google-ads.js, linkedin-ads.js,
│   │   ├── klaviyo.js, mailchimp.js, resend.js,
│   │   ├── hubspot.js, salesforce.js, stripe.js,
│   │   ├── hunter.js, snov.js, lemlist.js, instantly.js,
│   │   ├── github-prospects.js, ... (51 total)
│   ├── composio/            # Composio integration layer
│   └── integrations/        # 70+ API integration guides
```

**Category breakdown of 46 skills**:
- **Conversion** (5): cro, signup, onboarding, popups, paywalls
- **Content & Copy** (6): copywriting, copy-editing, cold-email, emails, social, image
- **SEO & Discovery** (7): seo-audit, ai-seo, programmatic-seo, site-architecture, competitors, schema, content-strategy, aso
- **Paid & Distribution** (2): ads, ad-creative
- **Measurement & Testing** (2): analytics, ab-testing
- **Retention** (1): churn-prevention
- **Growth Engineering** (5): co-marketing, free-tools, referrals, community-marketing, directory-submissions
- **Strategy & Monetization** (6): marketing-ideas, marketing-psychology, launch, pricing, offers, marketing-plan
- **Sales & RevOps** (3): revops, sales-enablement, prospecting, competitor-profiling
- **PR & Communication** (1): public-relations
- **Automation** (1): marketing-loops
- **Foundation** (1): product-marketing
- **SMS** (1): sms
- **Video** (1): video

---

## 3. Key Architecture & Skill Design Patterns

### Skill Structure (SKILL.md format)

Every skill is a Markdown file with YAML frontmatter following the **Agent Skills spec** (`agentskills.io`):

```yaml
---
name: skill-name
description: "When to use this skill. Include trigger phrases and keywords."
metadata:
  version: 2.0.0
---
```

**Directory layout per skill:**
```
skills/skill-name/
├── SKILL.md          # Required - main instructions (<500 lines)
├── references/       # Optional - detailed docs loaded on demand
├── evals/            # Optional - quality evaluation suite
│   └── evals.json
└── assets/           # Optional - templates, data files
```

### Key Design Principles

1. **product-marketing is the foundation**: The `product-marketing` skill creates `.agents/product-marketing.md` — a comprehensive context document capturing product overview, target audience, ICP, competitive landscape, differentiation, objections, customer language, brand voice, etc. **Every other skill reads this file first** before producing output, ensuring alignment with the product.

2. **Skills cross-reference each other**: Skills form a dependency graph:
   - `copywriting` ↔ `cro` ↔ `ab-testing`
   - `revops` ↔ `sales-enablement` ↔ `cold-email`
   - `seo-audit` ↔ `schema` ↔ `ai-seo`
   - `customer-research` → `copywriting`, `cro`, `competitors`
   - `pricing` ↔ `offers` ↔ `launch` ↔ `copywriting` ↔ `sales-enablement`

3. **Reference files for depth**: Each skill has `SKILL.md` (concise) + `references/` (deep dives). The spec says SKILL.md under 500 lines; detail goes in references loaded on-demand by the agent.

4. **Versioned**: Each skill has semantic version metadata. VERSIONS.md tracks all versions with changelogs going back to v1.0.0.

5. **Eval suites**: Most skills include `evals/evals.json` for automated quality testing.

6. **Zero-dependency CLIs**: `tools/clis/` contains 51 Node.js scripts with zero external dependencies, each implementing a marketing platform API client.

### Claude Code-Specific Enhancements (in AGENTS.md/CLAUDE.md only)

- `!`command`` injection syntax (Claude Code only) for auto-injecting product context, date, git branch
- Version-check workflow: once per session, check VERSIONS.md for updates and notify user

---

## 4. Tools Registry

**70+ tools** across 14 categories in the tool ecosystem:

| Category | Tools |
|----------|-------|
| Analytics | GA4, Mixpanel, Amplitude, PostHog, Segment, Adobe Analytics, Plausible |
| SEO | Google Search Console, Semrush, Ahrefs, DataForSEO, Keywords Everywhere, Rankparse |
| Data Enrichment | Clearbit, Apollo, ZoomInfo, Clay |
| Data Aggregation | Supermetrics, Coupler |
| CRM | HubSpot, Salesforce, Close |
| Payments | Stripe, Paddle |
| Referral/Affiliate | Rewardful, Tolt, Mention-Me, PartnerStack, Dub |
| Email Marketing | Mailchimp, Customer.io, SendGrid, Resend, Kit, Beehiiv, Klaviyo, Postmark, Brevo, ActiveCampaign |
| SMS | Twilio, Plivo, Postscript, Attentive, Audiencetap |
| Email Outreach | Hunter, Snov, Lemlist, Instantly, Truelist |
| Ads | Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads |
| CRO/Testing | Hotjar, Optimizely |
| Social | Buffer |
| Video | Wistia, HeyGen, Hyperframes |
| Other | Zapier, Calendly, SavvyCal, Typeform, Intercom, Outreach, Crossbeam, Pendo, SimilarWeb, Exa, Firehose, SparkToro, RB2B, Gong, AirOps, Trustpilot, G2, OneSignal, Demio, GitHub, Firecrawl, Browserbase |

**Integration methods**: API, MCP, CLI, SDK — documented per tool.

---

## 5. Version History & Evolution (Condensed)

| Version | Date | Key Changes |
|---------|------|-------------|
| v1.0.0 | 2026-01-27 | Initial version, 29 integration guides |
| v1.x | 2026-02-27 | Migrated from `.claude/` to `.agents/` for cross-agent compatibility |
| v2.0.0 | 2026-05-05 | **Major breaking**: 17 skill renames, 1 consolidation (page-cro+form-cro→cro). 40 skills |
| v2.1.0 | 2026-05-21 | Added SMS skill (41 total) |
| v2.2.0 | 2026-05-26 | Added prospecting skill, 51 CLI tools, GitHub prospects CLI |
| v2.3.0 | 2026-05-27 | Added marketing-plan skill (43 total) |
| v2.4.0 | 2026-06-10 | Added public-relations skill, social v2.1.0 (44 total) |
| v2.5.0 | 2026-06-16 | Added offers skill (45 total) |
| v2.6.0 | 2026-07-01 | Added marketing-loops skill (43 repeatable agent workflows), ads 2.1.0 (46 total) |

The project has been shipping **major features weekly** since inception.

---

## 6. Issue Analysis

**Total open issues: 45**

### Most Reacted/Liked Issues:

| Issue | 👍 | Topic |
|-------|---|-------|
| #263: Bug, unable to install | 3 | Installation issue |
| #261: BUG, can't install | 3 | Installation issue |
| #295: Add OpenAI Codex plugin support | 2 | Cross-platform request |
| #229: Create official Claude Code plugin marketplace | 2 | Platform integration |
| #80: Add Cowork plugin support | 2 | Cross-platform request |
| #348: Skill Request: marketing-art | 1 | New skill suggestion |
| #323: plugin.json version stuck at 1.9.0 | 1 | Bug fix |
| #319: Revise skills diagram in README | 1 | Documentation |
| #65: Improve skill quality scores | 1 | Quality improvement |

### Issue Pattern Analysis:

1. **Skill Requests (most common)**: Many users request new skill suggestions — `marketing-art`, `scientific-research`, `start-from-scratch`, `crisis-communications`, `control de gestion` (French), etc.

2. **Installation bugs**: Early issues (April 2026) about installation problems on various platforms, mostly resolved.

3. **Cross-platform support**: Requests for Codex CLI plugin, Cowork plugin, Hermes Agent integration — showing demand for multi-agent compatibility.

4. **Feature improvements**: Suggestions like "add prefix to all skills", "integrate X algorithm insights", "add X algorithm to social".

5. **Sponsor inquiries**: Commercial interest in sponsorship/advertising within the repo (Wisprs inquiry).

6. **Third-party platform integration**: Requests for badges from MseeP.ai, ForgeCat, AppNiche — showing the repo's status as a leading ecosystem.

**Note**: Most issues get responses and many are closed. The repo has healthy community engagement with some international (Brazilian Portuguese, Spanish, French) requests showing global reach.

---

## 7. Community Sentiment & Reviews

### From Chinese Tech Community (腾讯云开发者社区, 2026-06-24):

- **Positive**: Described as a "must-have" for indie developers and small-team founders who wear the marketing hat
- **Value proposition**: "Corey Haines made an open-source Marketing Skills pack for AI coding agents. After installing in Claude Code, Codex, Cursor, or Windsurf, agents can do CRO optimization, write marketing copy, run SEO audits, build email sequences, design pricing — covering most structurable marketing tasks"
- **Key highlight**: "The `product-marketing` foundation design is clever — every skill reads it first, so you don't repeat yourself about what your product does"
- **Praise**: "These aren't generic prompts — each is structurally designed for specific marketing scenarios and linked together through `product-marketing`"

### From HyperFX.ai Ranking (2026-05-10, updated June 2026):

- **Ranked #7 out of 10** in "Best Marketing Skills, MCPs, and CLIs for AI Agents in 2026"
- **Score**: 8/10
- **Pros**: 46-skill bundle across full marketing spectrum; created by well-known marketing operator (Corey Haines); operator-grade specificity; referenced in VoltAgent's awesome-agent-skills (1,100+ entries)
- **Cons**: Skills cover diagnosis and analysis; execution requires separate MCP integration; no built-in MCP server; single maintainer; documentation lighter than enterprise products
- **Pricing**: Free (open-source)
- **Best for**: "Marketers who want a curated bundle of marketing-specific skills installable as a unit"

### Key Community Themes:

1. **Practical utility**: Users praise the depth — these aren't surface-level prompts but structured marketing frameworks
2. **Cross-platform**: Works across Claude Code, Codex CLI, Cursor, Windsurf, OpenClaw, Hermes
3. **Foundation-first design**: The product-marketing context document approach is widely appreciated
4. **Free value**: 46 professional-grade marketing skills, free and MIT-licensed, compared to paid alternatives
5. **Active development**: Weekly releases with meaningful updates

---

## 8. Competitive Landscape

### Direct Competitors (Marketing-specific skill packs):

| Competitor | Stars | Description |
|------------|-------|-------------|
| **coreyhaines31/marketingskills** | **36,366** | 46 marketing skills — **the market leader** |
| Hyper MCP + Skills | N/A (private/paid) | 80+ marketing integrations, $49/mo, vertically focused |
| VoltAgent marketing skills (via awesome-agent-skills) | 1,100+ entries curated | Broader collection but less depth per skill |
| Various community single-skill repos | Varies | Individual skills (e.g., last30days-skill at 25,400★) |

### Broader Ecosystem Competitors:

| Platform/Product | Focus | Key Differentiator |
|------------------|-------|-------------------|
| **Composio + awesome-claude-skills** | Horizontal integration | 28K★, 1,000+ tools, marketing is one category |
| **Hyper MCP** | Vertical marketing execution | 80+ integrations, audited skills, paid |
| **Mastra** | Agent framework | Build custom workflows, $250/mo cloud |
| **Claude Code native skills** | General agent host | Largest install base, 1,000+ community skills |
| **OpenClaw marketplace** | Skill marketplace | 4,200 monthly searches, but 41.7% have security issues |
| **Agent Skills (agentskills.io)** | Open standard | 40+ adopting products |

### What Makes coreyhaines31/marketingskills Special vs. Competition:

1. **Depth**: Not one-offs — 46 skills that form a coherent, interconnected system
2. **Foundation design**: product-marketing context file read by every skill (unique approach)
3. **Cross-reference architecture**: Skills are aware of each other, creating workflow chains
4. **Marketing-domain expertise**: Created by Corey Haines (author of "Founding Marketing", agency owner) — real marketing authority, not just a tech wrapper
5. **Tool ecosystem**: 70+ integration guides + 51 CLI tools bundled
6. **Completeness**: Covers the entire marketing stack from strategy to execution
7. **Open standard**: Follows agentskills.io spec, works across 40+ agent hosts
8. **Free & open source**: MIT license, no paywall for the skills themselves

---

## 9. Security & Trust Assessment

- **No known vulnerabilities** for coreyhaines31/marketingskills (unlike OpenClaw's 41.7% vulnerability rate)
- Skills are **read-only markdown files** — they guide agent behavior rather than executing code
- The CLI tools in `tools/clis/` are audited, zero-dependency Node.js scripts
- **Update mechanism**: The AGENTS.md provides a version-check workflow to ensure skills stay current
- All skills **open-source and inspectable** before installation

---

## 10. Summary: What Makes This Repo Special

1. **36K+ stars in 6 months**: Extraordinary growth, signaling massive demand and quality
2. **46 interconnected skills**: Most comprehensive marketing-specific agent skills ecosystem
3. **Architectural innovation**: product-marketing context foundation + cross-referencing skills
4. **Tool ecosystem**: 70+ integration guides + 51 zero-dep CLI tools
5. **Real marketing expertise**: Created by Corey Haines — marketing veteran, agency founder, author
6. **Adherence to open standard**: agentskills.io compliant, works across 40+ agent hosts
7. **Weekly active development**: Version 2.6.0 released July 1, 2026, with regular major additions
8. **Strong community**: 5,891 forks, 45 open issues with active triage

**Bottom line**: This is the definitive marketing skills repository for AI coding agents — the largest, most comprehensive, most actively maintained, and most architecturally sophisticated collection available. No competitor comes close in terms of marketing-domain depth, skill interconnectivity, and ecosystem completeness.
