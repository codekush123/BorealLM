import os
import requests
import json

OPENALEX_URL = "https://api.openalex.org/"

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

def fetch_works(api_key, per_page=5):
    """
    This function will fetch all the requested parameters like which 
    paper , how many should return and who is making the request.
    Date: 22/09/2026
    Updated: 22/09/2026
    """
    params = {
    "oql": OQL_QUERY,
    "per_page": per_page,
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

    response.raise_for_status()

    return response.json()

def main():
    api_key = os.getenv("OPENALEX_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENALEX_API_KEY is not set."
        )

    data = fetch_works(api_key)


    print("Total matching works: ", data["meta"]["count"])
    print("Works returned: ", len(data["results"]))
    first_work = data["results"][0]

    normalized_work = normalize_work(first_work)

    print(
        json.dumps(
            normalized_work,
            indent=2,
            ensure_ascii=False,
        )
    )

def normalize_work(work):
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
        


if __name__ == "__main__":
    main()