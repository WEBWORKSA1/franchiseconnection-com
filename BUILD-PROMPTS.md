# FranchiseConnection.com — Phase-wise build prompts

## The idea (and why it wins)

**FranchiseConnection.com = an independent franchise matchmaking and due-diligence hub.**
Buyers come for free, brand-neutral tools and guides (what can I afford, what does a category really cost, how do I read an FDD, how do I finance it). They leave as **qualified leads** through a free Match Report. Franchisors pay to reach those buyers.

Why this beats the alternatives for this domain:

| Option | Revenue ceiling | Verdict |
|---|---|---|
| Pure brand directory (Franchise Direct clone) | High, but needs a sales team and hundreds of paying brands before it has content | Too slow to start |
| News/media site | AdSense only, low RPM without huge traffic | Too thin |
| **Matchmaking + education hub (chosen)** | AdSense on high-CPC finance/business queries **plus** lead sales, consultant referral fees, lender referrals, featured listings | Earns from day one, compounds with SEO |

### Unit economics (planning numbers — validate with real data)
- Franchise consultant networks are paid by the franchisor on each placement; referral partners commonly earn a share of that.
- Directory portals sell buyer leads to franchisors per lead; qualified leads (capital + timeline stated) command the higher end.
- AdSense RPM on franchise/finance/SBA-loan content is typically above general-interest content.

Model at month 12 (conservative): 30,000 sessions/mo × 2% match-form conversion = 600 leads/mo. Selling or referring 30% at $40 = **$7,200/mo**, plus AdSense at a $15–$30 RPM on ~60,000 pageviews = **$900–$1,800/mo**, plus featured listings and sponsorships. Lead revenue, not ads, is the profit engine — AdSense pays for content.

---

## Phase 0 — Positioning & compliance guardrails
> You are building FranchiseConnection.com, an independent franchise matchmaking and due-diligence hub for prospective franchise buyers (US, Canada, UK, Australia) and for franchisors who want qualified buyers. Tone: plain-spoken, numerate, brand-neutral. The site must pass Google AdSense review: original long-form content, clear navigation, About/Contact/Privacy/Terms pages, no thin or placeholder pages, no deceptive ad placement, no content that implies endorsement by any franchisor. Do not use the phrase "Franchise Connection" as a trademark claim; include a Trademark & Copyright disclosure page and a short footer disclosure. Every page shows a top strip: "Contact, if you are interested in this website / domain name / sponsorship / advertisement / partnership" linking to https://web.works/contact. All forms route to one private inbox that never appears in page source as plain text.

## Phase 1 — Foundation
> Create a static site deployable on GitHub Pages (free plan, main branch, root). Use a tiny Python build script (`build.py`) that wraps page fragments in `src/pages/` with a shared head, header and footer, writes relative links so the site works on `username.github.io/repo/` and on the custom domain, and generates `sitemap.xml` and an HTML sitemap. Add `ads.txt`, `robots.txt`, `site.webmanifest`, an SVG favicon, Open Graph image and `.nojekyll`. Put the AdSense script and `google-adsense-account` meta in every page head. Design tokens: deep ledger teal `#123A42` ink, cool paper `#F3F5F6`, storefront-sign yellow `#FFC531` for primary actions, money green `#0E7C66` for positive figures, slate line `#D3DBE0`. Type: Archivo (expanded width for display, normal for UI) + Source Serif 4 for long-form article body. Left-aligned layouts, 1200px max width, visible focus states, reduced-motion respected, mobile first.

## Phase 2 — Lead-generation core (the money)
> Build three conversion paths that all post to the private inbox with a lead score:
> 1. **Get Matched** (`match.html`): 7-step quiz — goal, industries of interest, liquid capital, net worth, owner role (owner-operator / semi-absentee / passive), timeline, location — then contact details with explicit consent. Score franchise categories client-side from `data/concepts.json` and show the top matches instantly; send the lead with answers, score and matches.
> 2. **Explorer** (`explore.html`): filter 60+ franchise categories by budget, industry, owner role, home-based, recurring revenue, SBA-friendly; sort; compare up to 3 side by side; save favorites in localStorage; add to a "request info" basket and submit one two-step form (email first, then name/phone/capital).
> 3. **Budget dial** on the home page: a single slider ("I can invest about $___") that live-filters categories and hands the value to the Match quiz.
> Also: inline "Get your free match report" panels inside every guide, and a sticky mobile CTA bar.

## Phase 3 — Calculators (AdSense dwell time + lead magnets)
> On `tools.html`, build tabbed, no-dependency calculators: total investment estimator, SBA 7(a) loan payment, affordability check (liquid capital vs typical 20–30% equity injection), break-even & payback, true cost of royalties and ad-fund fees over the term, and multi-unit ramp. Each shows a plain-English verdict and a "Get matched with categories that fit these numbers" CTA.

## Phase 4 — Content hub (AdSense approval engine)
> Write 10+ original 1,200–2,000-word guides: how to buy a franchise, the FDD's 23 items, financing (SBA 7(a), 504, ROBS, HELOC, franchisor financing), validation-call questions, franchise vs independent startup, how to franchise your business, true costs, red flags, multi-unit and semi-absentee ownership, international franchise law (US/Canada/UK/Australia). Add a 100-term glossary with search. Each guide: table of contents, last-reviewed date, sources, related guides, in-article lead CTA, Article + Breadcrumb JSON-LD.

## Phase 5 — Media & automation (self-updating)
> Add a news page fed by `data/news.json`. A scheduled GitHub Actions workflow runs daily, pulls franchise headlines from public RSS (Google News queries for franchising, franchise expansion, SBA franchise loans), de-duplicates, keeps the newest 60, rebuilds sitemap dates and commits. The browser loads the freshest copy from the repo with a local fallback. Add a video library of franchise-education YouTube videos using click-to-load facades (fast pages, no tracking until play). Add an events calendar that hides past events automatically and counts down to the next one.

## Phase 6 — Monetization surfaces
> - `franchisors.html`: List your franchise (free profile, Featured, Pay-per-lead program, Sponsored guide) with an intake form.
> - `advertise.html`: sponsorships, newsletter, display packages, partnership — plus link to web.works/contact.
> - `support.html`: donations (one-time / monthly tiers) for operations, promotion, hiring and prizes — pledge form that triggers a secure payment link by email (no card fields on site).
> - `contests.html`: quarterly Franchise Pitch Challenge and monthly Franchise IQ quiz giveaway, auto-rolling countdowns, official rules (no purchase necessary).
> - `careers.html`: writers, video creators, consultant partners (commission), partnership sales, campus ambassadors — with application form.
> - Config-driven AdSense slots (`AD_SLOTS` in `site.js`) so manual units appear only once slot IDs exist; Auto ads work immediately.

## Phase 7 — Trust & legal
> About, Contact, Editorial policy (how categories are researched, no pay-to-rank), Privacy (Google AdSense cookies, opt-out links, form data, FormSubmit processor), Terms, Disclaimer (not legal/financial advice; earnings not guaranteed; verify in the FDD), Cookie policy, Trademark & Copyright disclosure, 404.

## Phase 8 — QA & launch
> Check: every page has the AdSense tag, title, description, canonical, one H1; no broken internal links; the private inbox string never appears in any file; forms validate and show success/error states; Lighthouse-friendly (lazy video, no layout shift); responsive at 360/768/1280. Publish on GitHub Pages from main. Then: point DNS (A records 185.199.108.153, .109, .110, .111 and `www` CNAME → `webworksa1.github.io`), set the custom domain in Pages settings, enforce HTTPS, verify in Search Console, submit sitemap, apply to AdSense, enable Google's consent message for EEA/UK.

## Phase 9 — Growth roadmap
> Programmatic pages: "franchises under $X in {state/province}", "{industry} franchise costs"; monthly "Franchise Market Pulse" from the news feed; newsletter; partner with 2–3 consultant networks and 1 SBA lender for referral revenue; sell featured placements once traffic > 20k/mo; add brand profiles only with verified FDD data.
