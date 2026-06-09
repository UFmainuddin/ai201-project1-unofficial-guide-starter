# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Off-campus housing experiences near Flushing, Queens, for CUNY Queens College students.

Queens College is mostly a commuter school — only about 500 out of 19,000+ students live on campus. Most students need to find their own housing nearby. The problem is that useful housing knowledge (real rent prices, which neighborhoods are safe and quiet, how long the bus actually takes, what landlords are like, where to eat on a student budget) is scattered across Reddit posts, forum threads, word-of-mouth, and personal experience. There is no one official resource that brings it together.

This RAG system makes that scattered knowledge searchable and answerable. A student can ask "How much does a one-bedroom cost in Flushing?" or "How do I get to campus from Main Street?" and get a grounded answer from real documents.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Wikipedia — Flushing, Queens | General neighborhood overview: demographics, culture, transit, history | https://en.wikipedia.org/wiki/Flushing,_Queens |
| 2 | Wikipedia — Queens College CUNY | Campus info, location, student population, on-campus housing | https://en.wikipedia.org/wiki/Queens_College,_City_University_of_New_York |
| 3 | Wikipedia — IRT Flushing Line (7 train) | 7 train stations, travel times, express/local service, ridership | https://en.wikipedia.org/wiki/IRT_Flushing_Line |
| 4 | NYC HPD — Tenant Rights and Responsibilities | Official NYC tenant rights: repairs, heat, harassment, eviction protections | https://www1.nyc.gov/site/hpd/services-and-information/tenants-rights-and-responsibilities.page |
| 5 | Flushing Housing Tips (curated) | Practical tips: rent ranges, landlord advice, commute, food, safety | documents/flushing_housing_tips.txt |
| 6 | Student Housing Options (curated) | Housing options for QC students: on-campus, neighborhoods, budgets | documents/student_housing_options.txt |
| 7 | Flushing Rent Prices (curated) | Rent prices by sub-neighborhood, what to budget for, how to find apartments | documents/flushing_rent_prices.txt |
| 8 | Flushing Neighborhoods Guide (curated) | Guide to Flushing sub-areas: culture, transit, pros/cons for students | documents/flushing_neighborhoods_guide.txt |
| 9 | Flushing Food Scene (curated) | Food courts, restaurant areas, grocery options, student budget food guide | documents/flushing_food_scene.txt |
| 10 | Queens Bus Routes (curated) | Bus routes Q25/Q17/Q44 connecting Queens College to Flushing; LIRR info | documents/queens_bus_routes.txt |
| 11 | Flushing Meadows-Corona Park (curated) | Park facilities, transit access, nearby redevelopment for students | documents/flushing_meadows_park.txt |

Note: Reddit, Yelp, and Google Reviews were attempted but block automated access (403/authentication required). The course PDF says manual curation is normal and expected. All curated documents are based on real, accurate information from multiple public sources and community knowledge about Flushing, Queens.

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Reasoning:**

The documents are a mix of short opinion-style tips and longer informational paragraphs. Most of the useful content in this domain comes in short, specific facts: "A one-bedroom in Flushing costs $1,500-$1,900/month" or "The Q25 bus stops on Kissena Blvd, right next to campus." A 300-character chunk is about 2-3 sentences — large enough to hold one complete fact with context, small enough to keep retrieval specific.

The 50-character overlap helps when a key fact spans a sentence boundary. For example, if a price range is mentioned at the end of one chunk and the explanation is at the start of the next, the overlap means both chunks carry partial context and either can match the query.

The main tradeoff: the longer Wikipedia articles will get split mid-paragraph with this approach. Some chunks will be fragments of a sentence. This is a known limitation and I document it in Anticipated Challenges below.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers)

**Top-k:** 5

**Reasoning for model choice:** all-MiniLM-L6-v2 is a lightweight (80MB) model that runs locally on CPU. It produces 384-dimensional embeddings and works well for short English text like reviews and tips. No API key needed, no rate limits, no cost.

**Production tradeoff reflection:**

If I were building this for real users and cost was not a concern, I would think about several tradeoffs:

- **Better accuracy:** A larger model like all-mpnet-base-v2 (768-dim) has higher quality embeddings but is slower and uses more memory. For a student housing guide it probably would not matter much, but for a larger corpus with more nuanced queries it would help.

- **Multilingual support:** Flushing has a large Chinese and Korean speaking community. Many reviews and forum posts are in Chinese or Korean. The all-MiniLM-L6-v2 model is English-only, so non-English source documents would produce bad embeddings. A multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would handle this better.

- **API vs local:** OpenAI's text-embedding-3-small is very accurate and cheap, but it requires an API key, adds network latency, and has rate limits. For a demo project running locally, the sentence-transformers approach is better.

- **Context length:** all-MiniLM-L6-v2 has a 256 token input limit. Most of my 300-character chunks are under 100 tokens, so this is fine. For longer documents, a model with higher context length like e5-large-v2 would be needed.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | How much does a one-bedroom apartment cost in Flushing? | Around $1,500 to $1,900 per month based on rent prices document |
| 2 | How do I get from Queens College to Flushing Main Street? | Take the Q25 or Q17 bus from Kissena Blvd campus stop to Flushing Main Street, about 20-25 minutes |
| 3 | What are the quieter neighborhoods in Flushing for a student who wants less noise? | Murray Hill (Flushing), Broadway-Flushing, or Auburndale — residential areas away from the Main Street commercial core |
| 4 | What rights do I have if my landlord refuses to fix a broken heater? | NYC law requires heat October 1 through May 31. File a complaint with 311/HPD. Can take landlord to Housing Court. Good Cause Eviction law also provides protections. |
| 5 | Where can I get cheap food near Flushing Main Street? | New World Mall food court and Golden Shopping Mall basement food court both have meals starting at $5-8. Dozens of restaurants on Main Street for Asian and South Asian cuisine. |

---

## Anticipated Challenges

1. **Short chunks may split mid-thought on longer documents.** The 300-character chunking will split the Wikipedia articles in the middle of paragraphs. A retrieved chunk might say "...the 7 train connects Flushing to" and then cut off. The 50-character overlap helps but doesn't fully solve this. The LLM will sometimes get incomplete context and have to say it doesn't have enough information.

2. **Rent prices may be outdated.** The rent figures in my documents are estimates based on publicly available data from 2024. Real market rents change constantly. If a user asks about current prices, the system might return outdated numbers without flagging them as estimates. The system prompt tells the model to note when source information may be dated.

---

## Architecture

```
+------------------+     +------------------+     +-------------------------+
|  documents/*.txt |     |   ingest.py       |     |   embed.py              |
|  (11 plain text  | --> |  load, clean,     | --> |  all-MiniLM-L6-v2       |
|   files)         |     |  chunk (300/50)   |     |  sentence-transformers  |
+------------------+     +------------------+     |  ChromaDB (local)       |
                                                   |  collection: housing_   |
                                                   |  guide                  |
                                                   +-------------------------+
                                                             |
                                                   +-------------------------+
                                                   |   query.py              |
                                                   |  retrieve top-5 chunks  |
                                                   |  send to Groq LLM       |
                                                   |  llama-3.3-70b-         |
                                                   |  versatile              |
                                                   +-------------------------+
                                                             |
                                                   +-------------------------+
                                                   |   app.py (Gradio UI)    |
                                                   |  text input + Ask btn   |
                                                   |  answer + sources boxes |
                                                   |  localhost:7860         |
                                                   +-------------------------+
```

Five pipeline stages:
1. **Document Ingestion** — ingest.py loads .txt files
2. **Chunking** — ingest.py splits with 300 char size, 50 char overlap
3. **Embedding + Vector Store** — embed.py uses all-MiniLM-L6-v2, stores in ChromaDB
4. **Retrieval** — embed.py retrieve() returns top-5 chunks for a query
5. **Generation** — query.py sends context to Groq llama-3.3-70b-versatile, app.py shows result

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

I will give Claude the Chunking Strategy section of this planning.md and ask it to implement `ingest.py` with a `load_documents()`, `clean_text()`, `chunk_text(size=300, overlap=50)`, and `ingest_all()` function. I will verify the output by running it and checking that 5 sample chunks look readable and are approximately 300 characters each. I will also verify the chunk count makes sense (should be 100-500 chunks for 11 documents).

**Milestone 4 — Embedding and retrieval:**

I will give Claude the Retrieval Approach section and the architecture diagram and ask it to implement `embed.py` using `SentenceTransformer("all-MiniLM-L6-v2")` and `chromadb.PersistentClient`. I will verify by running 3 test queries from the evaluation plan and checking that the returned chunks are actually relevant to those questions. Distance scores above 0.6 would mean retrieval is not working well.

**Milestone 5 — Generation and interface:**

I will give Claude the evaluation plan questions and the Gradio skeleton from the course PDF and ask it to implement `query.py` (Groq API call with grounding system prompt) and `app.py` (Gradio UI). I will verify by testing all 5 evaluation questions, confirming source citations appear in every answer, and testing an out-of-scope question to confirm the system declines to answer rather than hallucinating.
