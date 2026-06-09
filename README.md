# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers off-campus housing experiences near Flushing, Queens, for students at CUNY Queens College.

Queens College is mostly a commuter school — only about 500 out of 19,000+ students live on campus. Most students need to figure out housing on their own. The problem is that the knowledge that actually matters — real rent prices, which neighborhoods are quiet versus noisy, how long the bus actually takes, what landlords are like, where to eat on $10 — is scattered. It lives in Reddit posts, community boards, word-of-mouth from older students, and local knowledge that doesn't appear anywhere official.

This system makes that scattered knowledge searchable. A student can ask a plain question and get an answer based on real documents, with sources shown.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Wikipedia — Flushing, Queens | Wikipedia (web fetch) | https://en.wikipedia.org/wiki/Flushing,_Queens |
| 2 | Wikipedia — Queens College CUNY | Wikipedia (web fetch) | https://en.wikipedia.org/wiki/Queens_College,_City_University_of_New_York |
| 3 | Wikipedia — IRT Flushing Line | Wikipedia (web fetch) | https://en.wikipedia.org/wiki/IRT_Flushing_Line |
| 4 | NYC HPD — Tenant Rights | NYC.gov (web fetch) | https://www1.nyc.gov/site/hpd/services-and-information/tenants-rights-and-responsibilities.page |
| 5 | Flushing Housing Tips | Curated (multiple public sources) | documents/flushing_housing_tips.txt |
| 6 | Student Housing Options | Curated (QC.cuny.edu + research) | documents/student_housing_options.txt |
| 7 | Flushing Rent Prices | Curated (StreetEasy/Zillow data) | documents/flushing_rent_prices.txt |
| 8 | Flushing Neighborhoods Guide | Curated (Wikipedia + community sources) | documents/flushing_neighborhoods_guide.txt |
| 9 | Flushing Food Scene | Curated (Wikipedia + Brick Underground) | documents/flushing_food_scene.txt |
| 10 | Queens Bus Routes | Curated (MTA route data) | documents/queens_bus_routes.txt |
| 11 | Flushing Meadows-Corona Park | Curated (Wikipedia) | documents/flushing_meadows_park.txt |

Note: Reddit, Yelp, and Google Reviews were attempted first but all returned 403 (automated access blocked). The course PDF says manual curation is normal and expected for these sources. Curated documents use real, accurate information sourced from multiple public references.

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**

The documents in this system are a mix of short tip-style writing and longer informational paragraphs. Most of the useful knowledge comes in short, specific facts: "A one-bedroom costs $1,500-$1,900/month" or "The Q25 bus stops on Kissena Blvd." A 300-character chunk is about 2-3 sentences — long enough to hold one complete fact with some context, short enough that retrieval can match specific questions precisely.

The 50-character overlap helps when a key fact sits at the boundary between two chunks. For example, if a price range is mentioned at the end of one chunk and the explanation is at the start of the next, both chunks will have partial context and either can match a relevant query.

The main tradeoff is that the longer Wikipedia articles (7 train, Flushing overview, Queens College) get split in the middle of paragraphs. Some chunks are partial sentences without full context. This affected retrieval quality for certain queries — see the Failure Case Analysis section.

**Final chunk count:** 189 chunks across 11 documents

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 (via sentence-transformers)

This model runs locally — no API key, no rate limits, no cost. It is fast enough to embed all 189 chunks in under 2 seconds on CPU. The 384-dimensional vectors work well for short English text like tips and review-style content.

**Production tradeoff reflection:**

If this were a real system deployed for thousands of students, I would think about several things:

**Better accuracy vs speed:** all-MiniLM-L6-v2 is fast and small but not the most accurate. A model like all-mpnet-base-v2 produces 768-dimensional embeddings with better semantic understanding, but it is about twice as slow and uses more memory. For a larger document corpus or more complex queries, the accuracy improvement would be worth it.

**Multilingual support:** Flushing has a large Chinese-speaking and Korean-speaking community. Many housing conversations happen in Mandarin, Cantonese, or Korean — in WeChat groups, on Chinese-language forums, and in community discussions that are not in English. The all-MiniLM-L6-v2 model is English-only, so any non-English source documents would produce poor embeddings. A multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would handle this better.

**API-hosted vs local:** OpenAI's text-embedding-3-small is very accurate and only costs about $0.02 per million tokens. For a student project running locally, the free local model is better. For a production app with thousands of daily queries and a team maintaining it, an API-hosted model might make sense for reliability and updates.

**Context length:** all-MiniLM-L6-v2 has a 256-token input limit. My 300-character chunks are typically under 100 tokens, so this is not a problem. For longer chunks or full paragraphs, a model with a higher context limit (like e5-large-v2 with 512 tokens) would be needed.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for Queens College students looking for off-campus housing near 
Flushing, Queens, New York. Answer the user's question using ONLY the information in the 
provided documents. Do not use any outside knowledge. If the documents do not contain enough 
information to answer the question, say exactly: 'I don't have enough information on that.' 
For every fact you state, mention which source document it came from (use the filename in 
brackets, e.g., [flushing_rent_prices.txt]). If source data may be outdated, say so.
```

**How source attribution is surfaced in the response:**

Source attribution works in two ways. First, the system prompt instructs the model to cite the filename in brackets for every fact it states — for example, "A one-bedroom costs $1,500-$1,900 per month [flushing_housing_tips.txt]." Second, the `ask()` function in query.py programmatically extracts the list of source filenames from the retrieved chunks and returns them separately in the `sources` field. The Gradio UI shows these in a "Retrieved from" box below the answer, so even if the model forgets to cite a specific source in its text, the user can still see which documents were used.

The context is formatted as a labeled block before the question:
```
[flushing_rent_prices.txt]
... chunk text ...

[flushing_housing_tips.txt]
... chunk text ...

Question: How much is rent?
```

This explicit labeling gives the model clear information about which text came from which source.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How much does a one-bedroom apartment cost in Flushing? | $1,500–$1,900/month | Correctly stated $1,500–$1,900/month, cited sources, noted possible outdatedness | Relevant (dist 0.51) | Accurate |
| 2 | How do I get from Queens College to Flushing Main Street by bus? | Take Q25 or Q17 from Kissena Blvd, 20-25 min | Correctly named Q25 and Q17, gave accurate travel times, cited queens_bus_routes.txt | Relevant (dist 0.57) | Accurate |
| 3 | What are quieter neighborhoods near Flushing for a student who wants less noise? | Murray Hill, Broadway-Flushing, Auburndale | Listed all three neighborhoods with brief reasons for each, cited both relevant documents | Relevant (dist 0.31) | Accurate |
| 4 | What rights do I have if my landlord refuses to fix a broken heater? | File 311 complaint to HPD, heat required Oct 1–May 31 at 68°F | Mentioned 311 and Tenant Helpline but gave generic advice, missed specific heat temperature rules | Off-target (dist 1.0+) | Partially accurate |
| 5 | Where can I get cheap food near Flushing Main Street? | New World Mall food court ($5–8), Golden Shopping Mall ($4–6) | Named both food courts with correct prices, added grocery stores and restaurant variety | Relevant (dist 0.45) | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
What rights do I have if my landlord refuses to fix a broken heater?

**What the system returned:**
The system retrieved chunks from nyc_tenant_rights.txt with very high distance scores (1.0–1.1, compared to 0.5–0.6 for successful queries). The answer mentioned calling 311 and the Tenant Helpline, which is correct but generic. It did not mention the specific NYC heat regulations: landlords must provide heat from October 1 through May 31, and indoor temperature must be at least 68°F between 6am–10pm when it is below 55°F outside.

**Root cause (tied to a specific pipeline stage):**

This is a retrieval failure caused by two compounding issues:

1. **Content loss at the fetch stage:** The nyc_tenant_rights.txt file was created by fetching the HPD page and trimming the content to 6,000 characters to keep file sizes manageable. The specific heat regulation text ("October 1 through May 31," "68 degrees Fahrenheit," temperature thresholds) appears further into the HPD page and was cut off by the 6,000-character limit.

2. **Chunk content mismatch:** The 300-character chunks from the HPD page that made it into the index are mostly generic legal boilerplate ("Tenants should expect to live in safe, well-maintained buildings..."). None of the indexed chunks contain the word "heat" or "heater." The embedding model produces a query vector for "broken heater" that finds no good semantic match in the collection, resulting in distance scores above 1.0.

**What you would change to fix it:**

Remove the 6,000-character limit on the HPD page fetch, or split the page into multiple documents by section. Alternatively, write a focused document specifically about heat and repair rights that uses the same vocabulary as common user queries ("heater," "heat complaint," "no heat"). Better source coverage of the specific topic would give the embedding model something to actually match against.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the evaluation plan in planning.md before any code forced me to think about what specific questions the system should answer. This directly shaped how I wrote the curated documents. For example, because one test question was about bus routes, I made sure to write a detailed queens_bus_routes.txt that specifically covered the Q25 and Q17 from campus. Without that planning step, I might have collected documents that were interesting but not actually useful for the queries students would ask.

**One way your implementation diverged from the spec, and why:**

The spec in planning.md listed Brick Underground and 6sqft.com as sources I would fetch via HTTP GET. Both URLs either returned 404 or gave back empty content (search result pages instead of actual articles). I replaced them with curated documents I wrote based on the same publicly available information. The resulting documents are more focused on what students actually need to know — they skip the editorial context that housing blogs include and get straight to the useful facts. In hindsight, curated documents written for a specific audience worked better for this use case than scraped blog articles.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The full project specification (milestones 1–6), the planning.md spec sections (chunking strategy, retrieval approach, architecture diagram), and the requirements.txt file showing available libraries.
- *What it produced:* Complete implementations of collect_docs.py, ingest.py, embed.py, query.py, and app.py. The AI also helped troubleshoot the Wikipedia API not returning extracts for some articles (needed different page title format) and the HPD tenant rights URL that had moved.
- *What I changed or overrode:* I replaced the Brick Underground and 6sqft sources after the AI's scraping attempts failed — the AI tried several URL variations and the content either returned 404 or was a search results page. The final document set uses more reliable sources (Wikipedia API, HPD, and curated content).

**Instance 2**

- *What I gave the AI:* The actual evaluation results from running all 5 test questions — the full system responses with distance scores and retrieved chunks for each query.
- *What it produced:* The failure case analysis for Question 4 (heater query), identifying that the 6,000-character trim of the HPD page cut off the specific heat regulation text, and that the retrieved chunks were generic legal boilerplate that didn't semantically match "broken heater."
- *What I changed or overrode:* The AI's initial failure analysis focused only on chunk size. I directed it to also look at the fetch-stage content loss (the 6,000-char trim) as a contributing factor, since that was the root cause of the missing heat regulation information, not just how the chunks were split.

---

## Demo Video

  https://drive.google.com/file/d/1mZz0D2oDhMRXxVn_uTUlANYayAk6fHpI/view?usp=sharing
