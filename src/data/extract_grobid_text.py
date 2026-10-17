import xml.etree.ElementTree as ET
from pathlib import Path


XML_PATH = Path(
    "data/raw/xml/W2942539847.tei.xml"
)

OUTPUT_PATH = Path(
    "data/processed/debug/W2942539847_grobid_raw.txt"
)

NS = {
    "tei": "http://www.tei-c.org/ns/1.0"
}

def extract_element_text(element):

    if element is None:
        return ""

    raw_text = "".join(element.itertext())

    normalized_text = " ".join(
        raw_text.split()
    )

    return normalized_text

def extract_article(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    abstract_element = root.find(
        ".//tei:abstract",
        NS,
    )

    body_element = root.find(
        ".//tei:body",
        NS,
    )

    if body_element is None:
        raise ValueError(
            "No TEI body element found."
        )

    abstract = extract_element_text(
        abstract_element
    )

    parts = []
    heading_count = 0
    paragraph_count = 0

    if abstract:
        parts.append("ABSTRACT")
        parts.append(abstract)

    parts.append("BODY")

    for element in body_element.iter():

        tag = element.tag.split("}")[-1]

        if tag == "head":
            heading = extract_element_text(element)

            if heading:
                parts.append(f"## {heading}")
                heading_count += 1

        elif tag == "p":
            paragraph = extract_element_text(element)

            if paragraph:
                parts.append(paragraph)
                paragraph_count += 1

    full_text = "\n\n".join(parts)

    return full_text, heading_count, paragraph_count


def main():

    full_text, headings, paragraphs = extract_article(
        XML_PATH
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        full_text,
        encoding="utf-8",
    )

    print("=" * 60)
    print("BOREALAM GROBID TEXT EXTRACTION")
    print("=" * 60)

    print("Section headings:", headings)
    print("Body paragraphs:", paragraphs)
    print("Extracted characters:", len(full_text))
    print("Output:", OUTPUT_PATH)

    print("\nTEXT PREVIEW")
    print("-" * 60)
    print(full_text[:1500])


if __name__ == "__main__":
    main()