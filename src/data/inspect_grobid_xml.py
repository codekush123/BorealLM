import os
import requests
import xml.etree.ElementTree as ET

from pathlib import Path
from collections import Counter


WORK_ID = "W2942539847"

XML_URL = (
    f"https://content.openalex.org/works/"
    f"{WORK_ID}.grobid-xml"
)

OUTPUT_PATH = Path(
    f"data/raw/xml/{WORK_ID}.tei.xml"
)


def local_name(element):
    return element.tag.split("}")[-1].lower()

def inspect_body_headings(root):

    namespace = {
        "tei": "http://www.tei-c.org/ns/1.0"
    }

    body = root.find(".//tei:body", namespace)

    if body is None:
        raise ValueError("No body found.")

    parent_map = {
        child: parent
        for parent in root.iter()
        for child in parent
    }

    print("\nHEADING STRUCTURE")
    print("=" * 60)

    for element in body.iter():

        if local_name(element) != "head":
            continue

        heading = " ".join(
            "".join(element.itertext()).split()
        )

        parent = parent_map.get(element)

        if parent is None:
            continue

        print("Heading:", heading[:80])
        print("Parent tag:", local_name(parent))
        print("Parent attributes:", parent.attrib)
        print("-" * 40)

    figure_count = sum(
        1
        for element in body.iter()
        if local_name(element) == "figure"
    )

    print("Figure elements in body:", figure_count)


def inspect_abstract_fragments(root):

    namespace = {
        "tei": "http://www.tei-c.org/ns/1.0"
    }

    abstract = root.find(
        ".//tei:abstract",
        namespace,
    )

    if abstract is None:
        print("No abstract found.")
        return

    fragments = list(abstract.itertext())

    print("\nABSTRACT TEXT FRAGMENTS")
    print("=" * 60)
    print("Total fragments:", len(fragments))

    targets = (
        "components.",
        "Widespread",
        "liquid",
        "solid",
    )

    for index, fragment in enumerate(fragments):

        if not any(
            target.lower() in fragment.lower()
            for target in targets
        ):
            continue

        print(f"\nFragment {index} and its neighbors:")

        start = max(0, index - 1)
        end = min(len(fragments), index + 2)

        for position in range(start, end):
            print(
                position,
                repr(fragments[position])
            )
def inspect_body_fragments(root):

    namespace = {
        "tei": "http://www.tei-c.org/ns/1.0"
    }

    body = root.find(
        ".//tei:body",
        namespace,
    )

    if body is None:
        raise ValueError("No body found.")

    paragraphs = body.findall(
        ".//tei:p",
        namespace,
    )

    print("\nBODY TEXT FRAGMENT INSPECTION")
    print("=" * 60)

    for paragraph_number, paragraph in enumerate(
        paragraphs[:2],
        start=1,
    ):

        fragments = list(paragraph.itertext())

        print(f"\nPARAGRAPH {paragraph_number}")
        print("Number of fragments:", len(fragments))

        for index, fragment in enumerate(
            fragments[:20]
        ):

            print(
                f"Fragment {index}: "
                f"{repr(fragment[:150])}"
            )

def inspect_inline_markup(root):

    namespace = {
        "tei": "http://www.tei-c.org/ns/1.0"
    }

    body = root.find(".//tei:body", namespace)

    if body is None:
        raise ValueError("No body found.")

    first_paragraph = body.find(
        ".//tei:p",
        namespace,
    )

    if first_paragraph is None:
        raise ValueError("No paragraph found.")

    print("\nINLINE XML MARKUP INSPECTION")
    print("=" * 60)

    children = list(first_paragraph)

    print("Direct child elements:", len(children))

    for index, child in enumerate(children[:10], start=1):

        tag = child.tag.split("}")[-1]

        print(f"\nChild {index}")
        print("Tag:", tag)
        print("Attributes:", child.attrib)

        print(
            "Element text:",
            repr("".join(child.itertext())[:100])
        )

        print(
            "Following text:",
            repr((child.tail or "")[:100])
        )

def main():
    if OUTPUT_PATH.is_file():

        print("Loading existing XML:", OUTPUT_PATH)

        tree = ET.parse(OUTPUT_PATH)
        root = tree.getroot()

        inspect_body_headings(root)
        inspect_abstract_fragments(root)
        inspect_body_fragments(root)
        inspect_inline_markup(root)


        return

    # Keep your existing download code below this line.
    api_key = os.getenv("OPENALEX_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENALEX_API_KEY is not set."
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            f"XML already exists: {OUTPUT_PATH}"
        )

    response = requests.get(
        XML_URL,
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        timeout=(15, 60),
    )

    print("HTTP status:", response.status_code)
    response.raise_for_status()

    xml_bytes = response.content

    if len(xml_bytes) > 20 * 1024 * 1024:
        raise ValueError("XML exceeds 20 MiB limit.")

    root = ET.fromstring(xml_bytes)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_bytes(xml_bytes)

    tags = Counter(
        local_name(element)
        for element in root.iter()
    )

    print("\nBOREALAM GROBID XML REPORT")
    print("=" * 60)

    print("Root element:", local_name(root))
    print("File size:", len(xml_bytes), "bytes")
    print("Abstract elements:", tags["abstract"])
    print("Section elements:", tags["div"])
    print("Paragraph elements:", tags["p"])
    print("Bibliographic entries:", tags["biblstruct"])

    abstracts = [
        element
        for element in root.iter()
        if local_name(element) == "abstract"
    ]

    if abstracts:
        abstract = " ".join(
            " ".join(abstracts[0].itertext()).split()
        )

        print("\nABSTRACT PREVIEW")
        print("-" * 60)
        print(abstract[:1000])

    print("\nSaved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()