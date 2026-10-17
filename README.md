# BorealLM

### Building a small language model for additive manufacturing — one experiment at a time

**Status:** Work in progress · **Focus:** Laser Powder Bed Fusion (LPBF), scientific text processing, and small language models

I'm building **BorealLM** as a student project to understand how a language model is made from the ground up, from gathering research papers to preparing text, training a tokenizer, implementing a Transformer, and evaluating what the model actually learns.

I chose **metal additive manufacturing**, especially **Laser Powder Bed Fusion (LPBF)**, because it is a field with a lot of interesting research and specialized terminology. Papers discuss everything from melt-pool behavior and porosity to process parameters, microstructure, and mechanical properties. That makes LPBF a useful domain for exploring how a small language model handles technical language.

The longer-term aim is to build a small, reproducible language-modeling research project, not just a chatbot interface. I also want the repository to show *how* I learn: the decisions I make, the experiments that fail, the limitations I find, and the improvements I can measure.

> **A note on the current stage:** BorealLM is **not a trained or deployed language model yet**. The scientific-data pipeline is working on a 39-paper pilot collection, with 38 papers currently extracted into a candidate text dataset. Tokenizer development is the next ML milestone.

---

## Why I'm working on this

When I started learning about LLMs, I realized that using a pretrained model and understanding how one is built are very different things. I wanted a project where I could work through the engineering and research questions myself:

- How do I collect scientific documents without losing track of their sources and licensing information?
- How much does PDF/XML extraction quality affect the text a model sees?
- Can a tokenizer trained on technical papers represent terms such as `Ti-6Al-4V`, `LPBF`, and `melt pool` efficiently?
- What can a small decoder-only Transformer actually learn from a limited domain corpus?
- How does training a small model from scratch compare with adapting an existing pretrained model?

I am using this project to strengthen my Python, NLP, deep-learning, experimental-design, and reproducible-research skills as I prepare for advanced study in AI and machine learning.

## Project at a glance

The data work started with an OpenAlex search for English, open-access LPBF research published from **2015 through 2026**, using license and full-text availability information as screening signals.

| Milestone | Current result |
| --- | ---: |
| Initial OpenAlex records retrieved | **2,266** |
| Canonical papers after deduplication/version resolution | **2,255** |
| Papers retained after LPBF-relevance screening | **2,246** |
| Technical themes used for pilot sampling | **13** |
| Papers in the frozen pilot manifest | **39** |
| Pilot GROBID XML files present locally | **39** |
| Pilot papers successfully extracted | **38** |
| Unique records in the extracted pilot dataset | **38** |
| Total extracted body/abstract characters | **1,606,053** |
| Pilot train / validation / test papers | **30 / 4 / 4** |
| Trained tokenizer | **Not yet completed** |
| Trained language model | **Not yet completed** |

The remaining extraction failure is **`W4390731192`**: the current parser could not find a TEI `<body>` element in its XML. I am keeping that failure visible rather than silently treating the dataset as complete.

The figures above describe a **pilot and an experimental dataset**, not a fully reviewed corpus or a claim of model performance.

## What the project looks like

```text
OpenAlex paper discovery
          │
          ▼
Metadata checks, deduplication, LPBF screening
          │
          ▼
Theme assignment and 39-paper pilot selection
          │
          ▼
Publisher PDF / OpenAlex GROBID TEI XML
          │
          ▼
Structure-aware text extraction
          │
          ├── Main article text
          └── Figure-related text
          │
          ▼
Quality checks and source tracking
          │
          ▼
Candidate JSONL dataset (38 papers)
          │
          ▼
Document-level train / validation / test split
          │
          ▼
BPE tokenizer                  ← next stage
          │
          ▼
Small decoder-only Transformer ← planned
          │
          ▼
Training, evaluation, and comparisons ← planned
```

## The scientific dataset

### Finding and selecting papers

Rather than downloading thousands of PDFs immediately, I built a staged collection process:

1. **Collect metadata** with the OpenAlex API, including paper identifiers, titles, abstracts, publication years, source links, and available license metadata.
2. **Resolve duplicates and publication versions** so the same research is not counted multiple times unnecessarily.
3. **Classify LPBF relevance** and preserve inclusion/exclusion decisions.
4. **Assign technical themes** to understand the range of subjects covered.
5. **Select a small pilot** to test acquisition and extraction before attempting much larger-scale training.

The pilot uses these 13 technical themes:

- Defects and porosity
- Design and geometry
- Functional properties
- Manufacturability
- Mechanical properties
- Melt-pool and thermal behavior
- Microstructure
- Monitoring and sensing
- Powder and feedstock
- Process parameters
- Residual stress
- Simulation and modeling
- Surface properties and post-processing

The frozen pilot has **three papers per theme**. This provides breadth for engineering tests; it does **not** make the 39-paper sample statistically representative of all LPBF research.

The collection also includes a metadata-based acquisition-priority score. That score helps organize downloads and reviews; it should not be interpreted as a definitive assessment of scientific quality.

### Why extraction quality became a major part of the project

Scientific PDFs are much harder to process than ordinary plain-text files. They contain two-column layouts, citations, mathematical expressions, chemical formulas, plots, captions, and headers.

For the first pilot article, *Dynamics of pore formation during laser powder bed fusion additive manufacturing* (`W2942539847`), I compared text extracted from the publisher PDF using **PyMuPDF** with the corresponding **GROBID TEI XML**.

The first extraction exposed issues such as:

- `components.Widespread` — two sentences joined together;
- `liquidsolid`, `LPBFproduced`, and `laserinduced` — incorrect word boundaries already present in the parsed text;
- plot labels appearing inside a Results paragraph;
- a figure caption appearing in the article narrative;
- a mathematical equation missing from the extracted body text;
- journal footer text at the end of the document.

I then updated the XML extractor to recognize sentence elements and inline bibliography references, and to keep figure elements separate from the main narrative. A focused audit identified **eight known-pattern issue occurrences** in that first article. This is not an exhaustive error rate; it is a starting point for quality assurance.

**The lesson so far:** getting text out of a PDF is easy compared with getting *trustworthy scientific text* out of it. The current pipeline keeps original source files and extracted text separate, so mistakes can be investigated and corrected without losing the source.

### Current candidate dataset

The batch builder processes locally available GROBID XML files and writes one JSON object per successfully extracted paper:

`data/processed/pilot/borealam_pilot_extracted_v1.jsonl`

Each record includes fields such as:

| Field | Purpose |
| --- | --- |
| `work_id`, `openalex_id`, `doi` | Paper identity |
| `title`, `year`, `primary_theme` | Scientific metadata |
| `body_text` | Abstract and extracted body text |
| `figure_text` | Separately extracted figure-related text |
| `heading_count`, `paragraph_count`, `figure_count` | Extraction diagnostics |
| `source_xml`, `source_xml_sha256` | Source tracing and file integrity |
| `extraction_method`, `quality_status` | Method version and review state |

All 38 records currently have **`quality_status: "unreviewed"`**. They are usable for pipeline experiments, but they have not passed a comprehensive scientific-content review.

## Repository structure

The main parts of the repository are organized as follows. Files marked *planned* are part of the intended ML workflow, not completed results.

```text
BorealLM/
├── data/
│   ├── manifests/              # Candidate lists, frozen pilot, data splits
│   ├── reviews/                # Review decisions and quality checks
│   ├── raw/
│   │   ├── pdf/                # Locally acquired publisher PDFs
│   │   └── xml/                # Locally acquired GROBID TEI XML
│   ├── processed/
│   │   ├── debug/              # Extraction comparison files
│   │   └── pilot/              # Candidate pilot JSONL dataset
│   └── provenance/             # Source URLs, hashes, acquisition metadata
│
├── src/
│   ├── data/                   # Collection, classification, extraction, splits
│   │   ├── openalex_collector.py
│   │   ├── inspect_grobid_xml.py
│   │   ├── extract_grobid_text.py
│   │   ├── download_pilot_xml.py
│   │   ├── build_pilot_dataset.py
│   │   ├── audit_extraction_quality.py
│   │   └── create_dataset_splits.py
│   │
│   └── ml/
│       ├── tokenizer/          # BPE tokenizer experiments (next)
│       ├── models/             # Transformer implementation (planned)
│       ├── training/           # Training loops (planned)
│       └── evaluation/         # Evaluation scripts (planned)
│
├── artifacts/                  # Saved tokenizers/models when available
├── docs/                       # Project notes and documentation
├── Process/                    # Working notes and project process
└── README.md
```

The diagram highlights the files relevant to this stage and is not meant to list every utility script already in `src/data/`.

## Reproducing the pilot workflow

The project is currently being developed with Python in a virtual environment on Windows/PowerShell. The scripts below assume commands are run from the **repository root**.

### 1. Set up Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install requests pymupdf tokenizers
```

A pinned dependency file and more formal environment setup are on the roadmap. The package command above covers the main libraries used in this phase, but other existing scripts may require additional dependencies.

### 2. Configure OpenAlex access when acquiring data

Some acquisition scripts require an OpenAlex API key. Set it as an environment variable in your local PowerShell session:

```powershell
$env:OPENALEX_API_KEY = "YOUR_API_KEY"
```

Never commit an API key, `.env` file containing credentials, or other secrets to the repository. API access, costs, limits, and content availability may change over time.

### 3. Acquire pilot XML files

```powershell
python .\src\data\download_pilot_xml.py
```

This script is designed to reuse valid local XML files and report unavailable or failed downloads. Acquisition also depends on API access and sufficient quota. Check the script's `MAX_NEW_DOWNLOADS` setting before running it.

### 4. Build the candidate dataset

```powershell
python .\src\data\build_pilot_dataset.py
```

The builder writes:

`data/processed/pilot/borealam_pilot_extracted_v1.jsonl`

The current completed run contains **38 successfully extracted papers**, with one TEI-structure failure.

### 5. Create the document-level split

```powershell
python .\src\data\create_dataset_splits.py
```

The current split manifest is:

`data/manifests/borealam_pilot_splits_v1.json`

| Split | Papers | Purpose |
| --- | ---: | --- |
| Training | 30 | Fit tokenizer and model parameters |
| Validation | 4 | Compare settings during development |
| Test | 4 | Final held-out evaluation |

The split is deterministic with seed `42` and records a dataset SHA-256 checksum. **Do not regenerate or overwrite an existing split manifest after beginning experiments**; the script is intended to protect the frozen split. Splitting by entire paper helps reduce within-document leakage, although near-duplicate text and cross-paper overlap still need attention.

### 6. Train the tokenizer — next milestone

The tokenizer module will live in:

`src/ml/tokenizer/train_tokenizer.py`

The initial experiment is planned around a **4,096-token byte-level BPE vocabulary**, trained on the **30 training papers only**. No tokenizer results are reported yet.

## ML plan

My intention is to keep the modeling work understandable and measurable instead of jumping straight to the largest model I can run.

### Stage A — Tokenization

Train a small domain-oriented BPE tokenizer and examine:

- whether text can be encoded and decoded correctly;
- how LPBF terminology is segmented;
- average tokens per character/word on held-out articles;
- behavior on alloy names, Greek letters, measurements, and equations.

### Stage B — A small decoder-only Transformer

Implement the main language-model components in PyTorch:

- token and position embeddings;
- causal self-attention;
- feed-forward layers and normalization;
- next-token prediction loss;
- batching, optimization, checkpointing, and reproducible training runs.

A model near **10 million parameters** is an eventual experimental target, not a completed architecture or a claim that the pilot corpus is large enough to train a useful domain model from scratch.

### Stage C — Experiments and evaluation

I want to compare at least a small from-scratch baseline with an appropriate pretrained-model adaptation approach once the data and compute budget support it. Possible evaluation measures include validation loss, perplexity, tokenizer efficiency, domain-term handling, and carefully checked scientific generation examples.

Because this pilot dataset is small, the four-document validation and test partitions will provide only noisy estimates. I will report those limitations rather than presenting pilot results as evidence of broad scientific expertise.

### Stage D — Share the work

The longer-term goal is to publish reproducible experiments, model and dataset documentation, and—if the results justify it—a Hugging Face model/demo. There is no published BorealLM checkpoint or deployment yet.

## Roadmap

- [x] Collect and organize OpenAlex candidate metadata
- [x] Deduplicate papers and document screening decisions
- [x] Create and review a 39-paper LPBF pilot
- [x] Prototype publisher-PDF and GROBID XML extraction
- [x] Separate main text from identifiable figure elements
- [x] Build an automated pilot XML acquisition/extraction workflow
- [x] Extract 38 unique pilot articles into JSONL
- [x] Create a reproducible document-level train/validation/test split
- [ ] Handle the alternative/unsupported XML structure of `W4390731192`
- [ ] Add scalable quality gates and source-license verification
- [ ] Train and evaluate a BPE tokenizer
- [ ] Implement and test a decoder-only Transformer
- [ ] Train small language-model baselines
- [ ] Compare model strategies and document results
- [ ] Publish a model card, dataset documentation, and reproducible checkpoints when ready

## Reproducibility and responsible data use

There are a few principles I want to follow as the project grows:

**Keep originals separate from transformations.** Raw PDFs/XML, processed text, and training-ready data are different artifacts. Checksums and source identifiers help trace the path between them.

**Be transparent about limitations.** OpenAlex license metadata and a downloadable full-text link are screening information, not a blanket guarantee that every file can be redistributed or used for every purpose. Each source's applicable license and attribution requirements need to be checked before publishing its full text or derivatives. Third-party content may have separate terms.

**Avoid uploading large or restricted raw corpora by default.** The public repository should focus on code, small metadata manifests where appropriate, documentation, and reproducible instructions. Raw documents, large processed corpora, credentials, and model checkpoints should be handled deliberately, with suitable `.gitignore` rules and separate distribution decisions.

**Don't confuse extraction success with scientific correctness.** A file that parses successfully can still contain missing equations, corrupted units, or mixed-in figures. Those errors matter when the objective is scientific language modeling.

**Report what has actually run.** Planned experiments are marked as planned. When model results are available, I want to include configurations, dataset versions, compute conditions, seeds, and both successful and unsuccessful findings.

## Tools and references

- [OpenAlex](https://openalex.org/) — scientific literature discovery and metadata
- [GROBID](https://github.com/kermitt2/grobid) — structured parsing of scholarly documents into TEI XML
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF inspection and text extraction
- [Hugging Face Tokenizers](https://github.com/huggingface/tokenizers) — tokenizer training and evaluation
- [PyTorch](https://pytorch.org/) — planned model implementation and training

The scientific papers themselves belong to their respective authors and publishers. BorealLM does not claim ownership of the source research.

## Final note

This is a learning project, and I'm deliberately keeping the messy parts visible. Building the data pipeline taught me that small decisions—like how to handle a citation, a split word, or an equation—can affect the quality of everything that comes after.

The next chapter is the one I've been working toward: **turning the text into tokens, implementing the model, and seeing what a small Transformer can actually learn.**
