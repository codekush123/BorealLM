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
    first_work = data["results"][1]
    inspect_work(first_work)


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