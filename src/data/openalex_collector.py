import os
import requests
import json

OPENALEX_URL = "https://api.openalex.org/"

OUTPUT_PATH = "src/data/manifests/lpbf_candidates.jsonl"

OQL_QUERY = """
works where best OA license is (cc-by)
  and language is (en)
  and open access is (true)
  and year >= (2015)
  and year <= (2026)
  and title/abstract has (stemmed "laser powder bed fusion")
  and type is (article or review)
  and PDF-linked is (true)
  and retracted is (false)
"""

def fetch_works(api_key, cursor="*", per_page=100):
    """
    This function will fetch all the requested parameters like which 
    paper , how many should return and who is making the request.
    Date: 22/09/2026
    Updated: 03/10/2026
    """
    params = {
    "oql": OQL_QUERY,
    "per-page": per_page,
    "cursor": cursor,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.get(
        OPENALEX_URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    if not response.ok:
        print("Status code: ", response.status_code)
        print("OpenAlex response:")
        print(response.text)

    response.raise_for_status()

    return response.json()

def fetch_all_works(api_key):
    """
    This function will fetct all the mentioned pages and return the result
    Created: 27/09/2026
    Updated: 06/10/2026
    """
    all_works = []
    cursor = "*"
    page_number = 1

    while cursor:
        print(f"Fetching page {page_number}...")

        data = fetch_works(
            api_key=api_key,
            cursor=cursor,
            per_page=100,
        )

        works = data["results"]

        if not works:
            break
        
        all_works.extend(works)

        print(
            f"Received {len(works)} works"
            f"| Total collected: {len(all_works)}"
        )

        cursor = data["meta"]["next_cursor"]

        page_number += 1

    return all_works


def normalize_work(work):
    """
    This function normalize the work by different parameters such as doi, title,
    author, license and many more.
    Created: 25/09/2026
    Updated: 03/10/2026
    """
    best_oa = work.get("best_oa_location") or {}
    source = best_oa.get("source") or {}
    topic = work.get("primary_topic") or {}

    has_content = work.get("has_content") or {}
    content_urls = work.get("content_urls") or {}

    authors = []

    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        name = author.get("display_name")

        if name:
            authors.append(name)

    abstract = reconstruct_abstract(
        work.get("abstract_inverted_index")
    )

    return {
        "openalex_id": work.get("id"),
        "doi": work.get("doi"),
        "title": work.get("title"),
        "abstract": abstract,
        "year": work.get("publication_year"),
        "citations": work.get("cited_by_count"),

        "authors": authors,

        "license": best_oa.get("license"),
        "version": best_oa.get("version"),
        "pdf_url": best_oa.get("pdf_url"),
        "landing_page_url": best_oa.get("landing_page_url"),

        "journal": source.get("display_name"),
        "primary_topic": topic.get("display_name"),

        "has_pdf": has_content.get("pdf"),
        "has_grobid_xml": has_content.get("grobid_xml"),

        "openalex_pdf_url": content_urls.get("pdf"),
        "grobid_xml_url": content_urls.get("grobid_xml"),
    }

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return None

    words_by_position = {}

    for word, positions in inverted_index.items():
        for position in positions:
            words_by_position[position] = word

    ordered_positions = sorted(words_by_position)

    abstract = " ".join(
        words_by_position[position]
        for position in ordered_positions
    )

    return abstract

def inspect_work(work):
    print("=" * 80)

    print("Title: ")
    print(work.get("title"))

    print("\nOpenAlex ID: ")
    print(work.get("id"))

    print("\nDOI: ")
    print(work.get("doi"))

    print("\nYear:")
    print(work.get("publication_year"))

    print("\nCitations:")
    print(work.get("cited_by_count"))

    best_oa = work.get("best_oa_location") or {}

    print("\nLicense:")
    print(best_oa.get("license"))

    print("\nVersion:")
    print(best_oa.get("version"))

    print("\nPDF:")
    print(best_oa.get("pdf_url"))

    source = best_oa.get("source") or {}

    print("\nJournal:")
    print(source.get("display_name"))

    topic = work.get("primary_topic") or {}

    print("\nPrimary topic:")
    print(topic.get("display_name"))
        
def save_jsonl(records, output_path):
    """
    This function will save all the normalized output in a locally as a jsonl file,
    so that it can be append later for more data. because earlier, the normalized record is a Python dictionary.
    Created: 06/10/2026
    Updated: 06/10/2026
    """
    with open(output_path, "w", encoding="utf-8") as file:
        for record in records:
            line = json.dumps(
                record,
                ensure_ascii=False,
            )

            file.write(line + "\n")

def main():
    api_key = os.getenv("OPENALEX_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENALEX_API_KEY is not set."
        )

    all_works = fetch_all_works(api_key)
    print()
    print("Raw works:", len(all_works))

    normalized_works = []

    for work in all_works:
        normalized_work = normalize_work(work)
        normalized_works.append(normalized_work)
    print()

    print("Normalized works:", len(normalized_works))

    save_jsonl(
        normalized_works,
        OUTPUT_PATH,
    )

    print(f"Saved manifest to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()