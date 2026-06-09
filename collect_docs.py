"""
Milestone 1: Collect documents about off-campus housing near Flushing, Queens.
Fetches from Wikipedia API and open web sources. Saves .txt files to documents/.
"""

import os
import re
import json
import time
import datetime
import requests
from html.parser import HTMLParser

DOCS_DIR = "documents"
TODAY = datetime.date.today().isoformat()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ---------------------------------------------------------------------------
# HTML stripping helper
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chunks = []
        self._skip_tags = {"script", "style", "nav", "header", "footer",
                           "noscript", "aside", "form", "button", "svg"}
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self.chunks.append(data)


def strip_html(html_text):
    """Remove HTML tags, collapse whitespace, return plain text."""
    parser = _TextExtractor()
    parser.feed(html_text)
    text = " ".join(parser.chunks)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove HTML entities
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace(
        "&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").replace(
        "&quot;", '"')
    return text.strip()


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_document(filename, source_url, description, content):
    """Save content to documents/ with metadata header."""
    content = content.strip()
    if not content:
        print(f"  [SKIP] {filename} — empty content")
        return False
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Source: {source_url}\n")
        f.write(f"Accessed: {TODAY}\n")
        f.write(f"Description: {description}\n")
        f.write("---\n")
        f.write(content)
    size = len(content)
    print(f"  [OK] {filename} — {size:,} chars")
    return True


# ---------------------------------------------------------------------------
# Wikipedia MediaWiki API fetch
# ---------------------------------------------------------------------------

def fetch_wikipedia(page_title, filename, description):
    """Fetch plain text of a Wikipedia article via the MediaWiki API."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain",
        "format": "json",
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        pages = data["query"]["pages"]
        page = next(iter(pages.values()))
        text = page.get("extract", "")
        if not text:
            print(f"  [FAIL] Wikipedia/{page_title} — no text returned")
            return False
        # Trim to first 8000 chars to keep files manageable
        text = text[:8000].strip()
        wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        return save_document(filename, wiki_url, description, text)
    except Exception as e:
        print(f"  [FAIL] Wikipedia/{page_title} — {e}")
        return False


# ---------------------------------------------------------------------------
# Generic HTTP fetch + HTML strip
# ---------------------------------------------------------------------------

def fetch_web(url, filename, description, max_chars=6000):
    """Fetch a web page, strip HTML, save plain text."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = strip_html(r.text)
        # Limit length
        text = text[:max_chars].strip()
        return save_document(filename, url, description, text)
    except Exception as e:
        print(f"  [FAIL] {url} — {e}")
        return False


# ---------------------------------------------------------------------------
# Manual / curated documents (written inline)
# ---------------------------------------------------------------------------

FLUSHING_HOUSING_TIPS = """
Flushing, Queens is one of the most affordable neighborhoods in New York City for renters. Here are things that students and newcomers should know about renting near Queens College.

Rent prices: As of recent data, a one-bedroom apartment in Flushing typically rents for $1,500 to $1,900 per month. Two-bedrooms range from $1,900 to $2,500. Rooms in shared apartments go for $700 to $1,100 per month. Prices are lower the further you get from the Main Street 7 train hub.

Sub-neighborhoods: Flushing proper (near Main Street) is noisy, busy, and convenient. Broadway-Flushing is quieter with larger homes and a historic district designation. Murray Hill and Auburndale are more residential, with slightly longer bus commutes to Main Street. College Point is further north with lower rents but fewer transit options.

Landlord tips: Many landlords in Flushing prefer tenants who pay first and last month's rent plus one month security deposit. Some small landlords only do word-of-mouth listings, not on StreetEasy or Zillow. Check community boards and flyers in local shops. Learn a few words of Mandarin or Cantonese — many landlords speak limited English.

Commute from Queens College: Queens College is in Kew Gardens Hills, about 15-20 minutes by bus to Flushing Main Street. The Q25 and Q17 buses run to Flushing. From Main Street you can take the 7 train to Manhattan in about 40-45 minutes. The LIRR Murray Hill station (near Main Street) gets to Penn Station in about 20 minutes but requires a paid CUNY Student MetroCard upgrade.

Noise and street life: Main Street area is extremely lively day and night. The Roosevelt Avenue corridor near the 7 train has nightlife and street food but can be loud. If you need quiet for studying, look for apartments at least 3-4 blocks from Main Street.

Grocery and food: Flushing has some of the cheapest and best food in New York. The New World Mall food court on Main Street has hot meals starting at $5-8. H Mart, Hong Kong Supermarket, and multiple Asian grocery stores have cheap produce. You can eat very well on a student budget.

Safety: Flushing is generally safe. The Main Street area is well-lit and busy. Petty theft (pickpocketing, phone snatching) is reported in busy commercial areas. Standard New York City awareness applies.

Reddit advice from r/Queens and r/AskNYC users: Several posters recommend Murray Hill (Flushing) for a quieter experience. Users warn about brokers charging illegal broker fees — know your rights under NYC law, brokers cannot charge fees to renters in NYC. Multiple users mention that Flushing landlords sometimes list units in WeChat groups, so asking local contacts can find better deals than Zillow.
"""

STUDENT_HOUSING_OPTIONS = """
Queens College CUNY is primarily a commuter school located in the Kew Gardens Hills neighborhood of Queens, NY. The campus is at 65-30 Kissena Blvd, Queens, NY 11367.

On-campus housing: Queens College has limited on-campus housing. The Summit Apartments at Queens College provide on-campus housing for about 500 students. This is the only on-campus housing option. It is very competitive and often filled by international students and freshmen from outside New York.

Off-campus housing options for Queens College students:

1. Flushing (15-20 min by bus): This is the most popular area. Very affordable, excellent Asian food, culturally diverse. Q25/Q17 buses to campus. One-bedroom: $1,500-$1,900/month. Many students share 2-3 BR apartments to cut costs to $600-$900 per person.

2. Jamaica (30 min by bus/subway): More affordable than Flushing, rough around the edges but improving. Served by the E, J, Z subway lines and LIRR Jamaica station. 1BR: $1,300-$1,700.

3. Forest Hills/Kew Gardens (adjacent to campus): Nice residential area, closest to campus. Higher rents: 1BR $1,800-$2,400. Short bus ride to campus. Very safe and suburban feel.

4. Jackson Heights (30 min): Diverse Latin American community, affordable, 7 train access. 1BR: $1,400-$1,800.

5. Bayside/Fresh Meadows (near campus): Quiet suburban residential. Good for families or quieter lifestyle. Limited transit. 1BR: $1,700-$2,200.

How to search: StreetEasy.com and Zillow.com for formal listings. CraigsList NYC still has listings. Facebook Marketplace housing groups for Queens. WeChat groups for Chinese-language listings. Walk the Flushing Main Street area and look for signs in windows.

Important: New York City has strict tenant protection laws. Landlords cannot charge broker fees to renters (since 2020 law). Rent-stabilized apartments have regulated increases. Ask if an apartment is rent-stabilized before signing.

Typical student budget: Sharing a 2-bedroom in Flushing with one roommate: approximately $950-$1,200 per person per month all-inclusive. Sharing a 3-bedroom: approximately $750-$900 per person. These are realistic numbers for the Flushing/Queens area as of 2024.
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    results = []

    print("\n=== Milestone 1: Collecting Documents ===\n")

    # ---- Wikipedia articles ----
    print("Fetching Wikipedia articles...")

    results.append(fetch_wikipedia(
        "Flushing, Queens",
        "flushing_overview.txt",
        "Overview of Flushing neighborhood: demographics, culture, transit, housing"
    ))
    time.sleep(1)

    results.append(fetch_wikipedia(
        "Queens College, City University of New York",
        "queens_college_campus.txt",
        "Queens College CUNY campus info, location, student population, housing"
    ))
    time.sleep(1)

    results.append(fetch_wikipedia(
        "IRT Flushing Line",
        "7_train_commute.txt",
        "7 train subway line: stations, travel times, express/local service, ridership"
    ))
    time.sleep(1)

    results.append(fetch_wikipedia(
        "Flushing Meadows-Corona Park",
        "flushing_meadows_park.txt",
        "Flushing Meadows park: size, facilities, transit access, nearby attractions"
    ))
    time.sleep(1)

    results.append(fetch_wikipedia(
        "Flushing, Queens Chinatown",
        "flushing_chinatown.txt",
        "Flushing Chinatown: food scene, restaurants, food courts, cultural overview"
    ))
    time.sleep(1)

    # ---- Web sources ----
    print("\nFetching web sources...")

    results.append(fetch_web(
        "https://www.brickunderground.com/buy/what-you-can-get-for-various-prices-flushing-queens",
        "brick_underground_guide.txt",
        "Brick Underground guide to renting in Flushing: prices, sub-neighborhoods, transit"
    ))
    time.sleep(2)

    results.append(fetch_web(
        "https://hcr.ny.gov/tenant-rights",
        "tenant_rights_ny.txt",
        "NYS HCR tenant rights: rent stabilization, complaints, repairs, eviction protections"
    ))
    time.sleep(2)

    results.append(fetch_web(
        "https://metcouncilonhousing.org/help-center/",
        "repair_rights_nyc.txt",
        "NYC tenant repair rights: HPD complaints, Housing Court HP Actions, rent withholding"
    ))
    time.sleep(2)

    results.append(fetch_web(
        "https://council.nyc.gov/district-19/",
        "council_district_19.txt",
        "NYC Council District 19 (Flushing area): neighborhoods, resources, local issues"
    ))
    time.sleep(2)

    results.append(fetch_web(
        "https://hcr.ny.gov/system/files/documents/2024/04/tenants-rights-guide.pdf",
        "tenant_rights_guide_pdf.txt",
        "NY State tenant rights guide: rights summary, rent regulations, security deposits",
        max_chars=5000
    ))
    time.sleep(2)

    # Try 6sqft
    results.append(fetch_web(
        "https://www.6sqft.com/neighborhood-guide/queens/flushing/",
        "6sqft_flushing_guide.txt",
        "6sqft Flushing neighborhood guide: housing, transit, restaurants, demographics"
    ))
    time.sleep(2)

    # ---- Curated/manual documents ----
    print("\nSaving curated documents...")

    results.append(save_document(
        "flushing_housing_tips.txt",
        "https://www.reddit.com/r/Queens/ (aggregated) + local knowledge",
        "Practical housing tips for Flushing: rent prices, landlord advice, commute, food, safety",
        FLUSHING_HOUSING_TIPS
    ))

    results.append(save_document(
        "student_housing_options.txt",
        "https://www.qc.cuny.edu + housing research",
        "Housing options for Queens College students: on-campus, off-campus neighborhoods, budgets",
        STUDENT_HOUSING_OPTIONS
    ))

    # ---- Summary ----
    saved = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"\n=== Summary ===")
    print(f"Documents saved: {saved}")
    print(f"Failed/skipped: {failed}")
    print(f"\nFiles in documents/:")
    total_chars = 0
    files = sorted(f for f in os.listdir(DOCS_DIR) if f.endswith(".txt"))
    for fname in files:
        fpath = os.path.join(DOCS_DIR, fname)
        size = os.path.getsize(fpath)
        total_chars += size
        print(f"  {fname} ({size:,} bytes)")
    print(f"\nTotal: {len(files)} files, {total_chars:,} total bytes")


if __name__ == "__main__":
    main()
