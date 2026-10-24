# BorealLM

### Building a small language model

**Status:** Work in progress  
**Focus:** Laser Powder Bed Fusion (LPBF), scientific text processing, tokenization, and small decoder-only language models

I am building **BorealLM** as a student project to understand how a language model is made from the ground up — from finding and preparing scientific papers to training a tokenizer, implementing a Transformer in PyTorch, training it, and evaluating what it actually learns.

I chose **metal additive manufacturing**, especially **Laser Powder Bed Fusion (LPBF)** domain to train the model, because it combines a technically interesting research domain with specialized language. LPBF papers discuss melt-pool behavior, porosity, process parameters, microstructure, residual stress, mechanical properties, monitoring, simulation, and many other topics that make the domain useful for experimenting with scientific NLP.

The goal is not to build a chatbot as quickly as possible. I want BorealLM to be a small, reproducible research project where I can learn the full process — including design decisions, preprocessing problems, failed assumptions, model limitations, and measurable improvements.

> **Current stage:** BorealLM now has a working scientific-data pipeline, a 4,096-token domain BPE tokenizer, a custom 10.06M-parameter decoder-only Transformer implemented in PyTorch, a completed one-epoch baseline training run, and working autoregressive text generation. A three-epoch follow-up experiment is currently in progress.

---

## Why I am working on this

When I started learning about large language models, I realized that using a pretrained model and understanding how one is built are very different things.

I wanted a project where I could work through the engineering and research questions myself:

- How do I collect scientific documents while keeping track of provenance and licensing information?
- How much does PDF/XML extraction quality affect the text a model sees?
- Can a tokenizer trained on technical papers represent terms such as `Ti-6Al-4V`, `LPBF`, `melt pool`, and `powder feedstock` efficiently?
- How do token embeddings, positional embeddings, attention, feed-forward layers, residual connections, and LayerNorm fit together?
- What can a roughly 10M-parameter decoder-only Transformer learn from a limited technical corpus?
- How can I tell the difference between real learning, memorization, undertraining, and overfitting?
- How does a small model trained from scratch compare with adapting an existing pretrained model?

I am using this project to strengthen my Python, NLP, deep-learning, experimental-design, and reproducible-research skills as I prepare for advanced study in AI and machine learning.

---

## Project at a glance

The data work started with an OpenAlex search for English, open-access LPBF research published from **2015 through 2026**, using license and full-text availability information as screening signals.

| Milestone                                               |             Current result |
| ------------------------------------------------------- | -------------------------: |
| Initial OpenAlex records retrieved                      |                  **2,266** |
| Canonical papers after deduplication/version resolution |                  **2,255** |
| Papers retained after LPBF-relevance screening          |                  **2,246** |
| Technical themes used for pilot sampling                |                     **13** |
| Papers in the frozen pilot manifest                     |                     **39** |
| Pilot GROBID XML files present locally                  |                     **39** |
| Pilot papers successfully extracted                     |                     **38** |
| Unique records in the extracted pilot dataset           |                     **38** |
| Total extracted body/abstract characters                |              **1,606,053** |
| Pilot train / validation / test papers                  |             **30 / 4 / 4** |
| BPE tokenizer vocabulary                                |           **4,096 tokens** |
| Training tokens after tokenization                      |                **296,796** |
| Validation tokens                                       |                 **35,904** |
| Test tokens                                             |                 **40,496** |
| BorealLM v1 parameter count                             |             **10,064,896** |
| BorealLM v1 context length                              |             **256 tokens** |
| Completed baseline training                             |                **1 epoch** |
| Baseline validation loss                                |                 **6.1361** |
| Autoregressive generation                               |                **Working** |
| Follow-up experiment                                    | **3 epochs — in progress** |

The remaining extraction failure is **`W4390731192`**: the current parser could not find a TEI `<body>` element in its XML. I am keeping that failure visible rather than silently treating the dataset as complete.

The figures above describe a **pilot and an experimental dataset**. They are not a claim that BorealLM is already a reliable scientific language model.

---

## What the project looks like

```text
OpenAlex paper discovery and collection of data
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
4,096-token byte-level BPE tokenizer
          │
          ▼
Encoded train / validation / test token streams
          │
          ▼
Causal language-model context windows
          │
          ▼
10.06M-parameter decoder-only Transformer
          │
          ▼
Training + validation checkpointing
          │
          ▼
Autoregressive text generation
          │
          ▼
Controlled experiments and evaluation
```

# Data pipeline

## Finding and selecting papers

Rather than downloading thousands of PDFs immediately, I built the collection process in stages:

1. **Collect metadata** with the OpenAlex API, including identifiers, titles, abstracts, publication years, source links, and available license metadata.
2. **Resolve duplicates and publication versions** so that the same research is not unnecessarily counted multiple times.
3. **Classify LPBF relevance** and preserve inclusion/exclusion decisions.
4. **Assign technical themes** to understand the range of subjects in the corpus.
5. **Select a small pilot** to test acquisition, extraction, tokenization, and training before scaling further.

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

The frozen pilot contains **three papers per theme**. This gives the engineering experiments some breadth, but it does **not** make the 39-paper sample statistically representative of all LPBF research.

---

## Current candidate dataset

The batch builder writes one JSON object per successfully extracted paper to:

```text
data/processed/pilot/borealam_pilot_extracted_v1.jsonl
```

Each record includes paper identity, scientific metadata, extracted body text, separately extracted figure-related text, extraction diagnostics, source XML paths and SHA-256 hashes, and a review status.

The 38 extracted records are still treated as an **experimental candidate corpus**. They are useful for tokenizer and model-pipeline experiments but have not passed a comprehensive paper-by-paper scientific review.

---

# Dataset split

The current pilot uses a deterministic, document-level split:

| Split      | Papers | Purpose                             |
| ---------- | -----: | ----------------------------------- |
| Training   | **30** | Fit tokenizer and model parameters  |
| Validation |  **4** | Compare settings during development |
| Test       |  **4** | Held-out evaluation                 |

The split uses seed `42` and records a SHA-256 checksum of the extracted dataset.

Splitting by whole paper helps reduce within-document leakage, although related papers, duplicated phrases, citations, and domain overlap can still create leakage risks.

---

# Tokenizer

## BorealAM BPE tokenizer v1

The first tokenizer is a **4,096-token byte-level BPE tokenizer** trained only on the 30 training papers.

```text
Training documents: 30
Training characters: 1,290,329
Vocabulary size: 4,096
```

The tokenizer is saved at:

```text
artifacts/tokenizer/borealam_bpe_v1.json
```

### Tokenizer evaluation

| Split      | Characters |  Tokens | Characters / token | Tokens / word |
| ---------- | ---------: | ------: | -----------------: | ------------: |
| Train      |  1,290,329 | 296,796 |          **4.348** |     **1.451** |
| Validation |    143,928 |  35,904 |          **4.009** |     **1.595** |
| Test       |    171,796 |  40,496 |          **4.242** |     **1.480** |

### Example technical-term tokenization

| Term                      | Token count |
| ------------------------- | ----------: |
| `LPBF`                    |       **1** |
| `melt pool`               |       **2** |
| `powder feedstock`        |       **2** |
| `additive manufacturing`  |       **3** |
| `microstructure`          |       **3** |
| `residual stress`         |       **3** |
| `SS316L`                  |       **4** |
| `laser powder bed fusion` |       **5** |
| `keyhole porosity`        |       **5** |
| `Ti-6Al-4V`               |       **7** |

For the first model baseline, I kept the 4,096-token vocabulary instead of increasing it immediately. A larger vocabulary could improve some tokenization cases, but it would also consume more of the parameter budget in the embedding and output layers.

---

# From text to causal language-model training

After tokenization, the three splits are converted into compact NumPy token streams:

```text
artifacts/dataset/
├── train_tokens.npy
├── validation_tokens.npy
├── test_tokens.npy
└── tokenization_metadata.json
```

An `[EOS]` token is inserted between documents so the model does not treat the end of one paper and the beginning of another as one continuous passage.

The first causal language-model dataset uses a context length of **256 tokens**.

```text
input  = [A, B, C, D, E]
target = [B, C, D, E, F]
```

The model therefore learns next-token prediction.

---

# BorealLM v1 architecture

BorealLM v1 is a decoder-only Transformer implemented directly in PyTorch rather than using a ready-made GPT model class.

I built and smoke-tested the main pieces separately:

- token embeddings;
- learned positional embeddings;
- query/key/value projection;
- multi-head scaled dot-product attention;
- causal masking;
- feed-forward network;
- GELU activation;
- Pre-LayerNorm;
- residual connections;
- stacked Transformer blocks;
- final language-model projection.

## Architecture configuration

| Component            |    BorealLM v1 |
| -------------------- | -------------: |
| Vocabulary size      |      **4,096** |
| Context length       |        **256** |
| Embedding dimension  |        **256** |
| Attention heads      |          **8** |
| Dimension per head   |         **32** |
| Transformer blocks   |         **10** |
| MLP hidden dimension |      **1,024** |
| Dropout              |        **0.1** |
| Total parameters     | **10,064,896** |

The model accepts:

```text
[batch, 256]
```

token IDs and returns:

```text
[batch, 256, 4096]
```

logits.

The final model contains **10,064,896 trainable parameters**, which is very close to the original goal of building a roughly 10M-parameter SLM.

---

# Training

The training code now includes:

- causal next-token cross-entropy loss;
- AdamW optimization;
- gradient clipping;
- validation after each epoch;
- best-checkpoint saving;
- training-history logging;
- reproducible seeds;
- CPU/CUDA/MPS device selection.

The first training run used:

| Setting               |     Value |
| --------------------- | --------: |
| Context length        |   **256** |
| Batch size            |     **4** |
| Learning rate         |  **3e-4** |
| Weight decay          |   **0.1** |
| Maximum gradient norm |   **1.0** |
| Epochs                |     **1** |
| Training tokens       | **~296k** |

A uniform prediction over a 4,096-token vocabulary would have cross-entropy around:

```text
ln(4096) ≈ 8.32
```

| Experiment         | Epochs | Validation loss | Generation quality                                  |
| ------------------ | -----: | --------------: | --------------------------------------------------- |
| BorealLM-v1-1epoch |      1 |          6.1361 | Domain terms, repetitive but somewhat sentence-like |
| BorealLM-v1-3epoch |      3 |      **5.3763** | Lower loss, but stronger table/extraction artifacts |

---

# First generation result

BorealLM can now generate text autoregressively.

The first baseline generation used:

```text
Prompt: "Laser powder bed fusion"
Temperature: 0.8
Top-k: 50
Checkpoint: 1 epoch
Validation loss: 6.1361
```

One generated sample was:

> Laser powder bed fusion can be the same of the laser power the temperature the part and the melt pool of the melt pool of the laser powerly to the powder bed not the melt pool size of the melt pool in the laser power. The temperature. The the thermal effect of the melt pool during the laser power of powder bed surface, which (Fig. The scan speed were the lasers for the melt pool and the

The output is not yet good scientific prose, but it is also not random. It repeatedly uses domain-related concepts such as laser power, temperature, melt pool, powder bed, scan speed, and thermal effects.

It also exposes important weaknesses:

- repetition;
- weak grammar;
- poor long-range coherence;
- extraction artifacts such as `(Fig.`;
- no guarantee of scientific correctness.

The `(Fig.` fragment is especially useful because it connects model behavior back to preprocessing: contamination in training text can appear in generated text.

The second baseline generation use

BOREALLM GENERATION
Device: cpu
Checkpoint epoch: 3
Validation loss: 5.3763
Prompt: Laser powder bed fusion
Temperature: 0.8
Top-k: 50

GENERATED TEXT

Laser powder bed fusion in our the powder bed, the gas of the plume.

## PAPFIDImentioned in each strut of the effect on the LoFs on the particle size of the HIP pressure of the as well as the part.

Table 29 m/L stainless steel

In the same surface. The surface:

F-zation of the

GENERATION STATS
Total tokens: 84

---

# Repository structure

```text
BorealLM/
├── data/
│   ├── manifests/
│   ├── reviews/
│   ├── raw/
│   │   ├── pdf/
│   │   └── xml/
│   ├── processed/
│   │   ├── debug/
│   │   └── pilot/
│   └── provenance/
│
├── src/
│   ├── data/
│   │   ├── openalex_collector.py
│   │   ├── inspect_grobid_xml.py
│   │   ├── extract_grobid_text.py
│   │   ├── download_pilot_xml.py
│   │   ├── build_pilot_dataset.py
│   │   ├── audit_extraction_quality.py
│   │   └── create_dataset_splits.py
│   │
│   └── ml/
│       ├── tokenizer/
│       │   ├── train_tokenizer.py
│       │   ├── evaluate_tokenizer.py
│       │   └── encode_dataset.py
│       ├── models/
│       │   ├── embeddings.py
│       │   ├── attention.py
│       │   ├── feed_forward.py
│       │   ├── transformer_block.py
│       │   └── boreallm.py
│       ├── training/
│       │   ├── lm_dataset.py
│       │   ├── train_smoke_test.py
│       │   └── train.py
│       └── evaluation/
│           └── generate.py
│
├── artifacts/
│   ├── tokenizer/
│   ├── dataset/
│   ├── checkpoints/
│   └── training/
│
├── docs/
├── Process/
└── README.md
```

Generated artifacts and large files should be handled deliberately through `.gitignore` or separate model/data distribution.

---

# Reproducing the current pipeline

## 1. Create and activate the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install requests pymupdf tokenizers numpy torch
```

## 2. Configure OpenAlex access

```powershell
$env:OPENALEX_API_KEY = "YOUR_API_KEY"
```

Never commit API keys or credentials.

## 3. Build the extracted pilot dataset

```powershell
python .\src\data\build_pilot_dataset.py
```

## 4. Create the document split

```powershell
python .\src\data\create_dataset_splits.py
```

## 5. Train and evaluate the tokenizer

```powershell
python .\src\ml\tokenizer\train_tokenizer.py
python .\src\ml\tokenizer\evaluate_tokenizer.py
python .\src\ml\tokenizer\encode_dataset.py
```

## 6. Test the model components

```powershell
python .\src\ml\models\embeddings.py
python .\src\ml\models\attention.py
python .\src\ml\models\feed_forward.py
python .\src\ml\models\transformer_block.py
python .\src\ml\models\boreallm.py
```

The assembled model should report:

```text
Total parameters: 10,064,896
Input shape:  [2, 256]
Logits shape: [2, 256, 4096]
```

## 7. Train BorealLM

```powershell
python .\src\ml\training\train.py
```

## 8. Generate text

```powershell
python .\src\ml\evaluation\generate.py
```

Generated scientific text should **not** be treated as factually reliable.

---

# What I have learned so far

### Data quality affects the model directly

Extraction artifacts that look small during preprocessing can reappear in generated text.

### A tokenizer is part of the model design

Vocabulary size affects both token efficiency and the parameter budget of a small language model.

### Attention is only one part of the Transformer

A large part of the parameter count is also in feed-forward layers, embeddings, and the output projection.

### A working loss curve is not the same as a useful model

The first BorealLM model reduced validation loss well below the random baseline, but its generated language is still repetitive and unreliable.

### Small models make experiments easier to understand

At roughly 10M parameters, I can inspect architecture choices, parameter counts, generation behavior, and training dynamics without hiding everything behind a large pretrained system.

---

# Current limitations

BorealLM is still an early research prototype.

Important limitations include:

- only **38 extracted pilot papers** are currently used;
- the training split contains only about **297k tokens**;
- extraction artifacts remain in the corpus;
- one pilot XML document uses an unsupported/alternative structure;
- the validation and test splits contain only four papers each;
- the model has not been evaluated for factual scientific correctness;
- generation can be repetitive and grammatically weak;
- no claim is made that the model has scientific understanding;
- the current corpus is far too small to expect a strong 10M-parameter model trained from scratch.

Because of these limitations, the current model is best treated as a **from-scratch language-modeling baseline and learning platform**.

---

# Roadmap

## Data

- [x] Collect and organize OpenAlex candidate metadata
- [x] Deduplicate papers and preserve screening decisions
- [x] Create and review a 39-paper LPBF pilot
- [x] Prototype PDF and GROBID XML extraction
- [x] Separate identifiable figure content from main text
- [x] Build automated pilot XML acquisition/extraction
- [x] Extract 38 unique pilot articles into JSONL
- [x] Create reproducible train/validation/test splits
- [ ] Handle the alternative XML structure of `W4390731192`
- [ ] Add scalable quality gates
- [ ] Improve source-license verification
- [ ] Scale beyond the 38-paper pilot

## Tokenization

- [x] Train a 4,096-token byte-level BPE tokenizer
- [x] Evaluate tokenizer compression on train/validation/test
- [x] Inspect LPBF technical-term tokenization
- [x] Encode the dataset into token streams

## Model

- [x] Implement token + positional embeddings
- [x] Implement causal multi-head self-attention
- [x] Implement the feed-forward network
- [x] Implement Pre-LayerNorm Transformer blocks
- [x] Assemble a 10-layer decoder-only model
- [x] Reach the intended ~10M-parameter scale
- [x] Verify forward and backward passes

## Training and evaluation

- [x] Implement causal language-model loss
- [x] Implement AdamW optimization
- [x] Implement gradient clipping
- [x] Implement validation and best-checkpoint saving
- [x] Complete a one-epoch baseline
- [x] Generate the first BorealLM text sample
- [ ] Complete the controlled three-epoch experiment
- [ ] Compare fixed prompts across checkpoints
- [ ] Track train/validation behavior for overfitting
- [ ] Evaluate the held-out test set
- [ ] Scale training data before drawing strong conclusions
- [ ] Compare against a pretrained-model adaptation baseline

## Publication

- [ ] Add formal experiment tables and plots
- [ ] Add a pinned dependency/environment file
- [ ] Write a model card
- [ ] Write dataset documentation
- [ ] Publish reproducible checkpoints when appropriate
- [ ] Publish to Hugging Face if the results justify it

---

# Reproducibility and responsible data use

**Keep originals separate from transformations.**  
Raw PDFs/XML, extracted text, tokenized data, and model-ready arrays are different artifacts. Checksums and source identifiers help trace the path between them.

**Be transparent about limitations.**  
OpenAlex license metadata and downloadable full-text links are screening information, not a blanket guarantee that every source can be redistributed or used for every possible downstream purpose.

**Avoid uploading large or restricted corpora by default.**  
The public repository should focus on code, documentation, small metadata manifests where appropriate, and reproducible instructions.

**Do not confuse extraction success with scientific correctness.**  
A file that parses successfully can still contain missing equations, corrupted units, merged figure labels, or broken technical terminology.

**Do not confuse lower loss with scientific understanding.**  
A language model can learn strong statistical patterns while still producing incorrect scientific statements.

**Report what actually ran.**  
Completed experiments are marked as completed; planned or currently running experiments are labeled accordingly.

---

# Tools and references

- [OpenAlex](https://openalex.org/) — scientific literature discovery and metadata
- [GROBID](https://github.com/kermitt2/grobid) — structured parsing of scholarly documents into TEI XML
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF inspection and text extraction
- [Hugging Face Tokenizers](https://github.com/huggingface/tokenizers) — tokenizer training and evaluation
- [PyTorch](https://pytorch.org/) — model implementation, training, and inference
- I also learned all the concepts from Google deepmind 01 - 08 course series from Google Skills

---

# Final note

BorealLM started as an idea to build a small language model for additive manufacturing, but the project has become more useful to me as a way to understand the entire ML pipeline.

So far I have had to think about literature discovery, duplicate resolution, scientific-document structure, text quality, tokenization, dataset leakage, embeddings, attention, residual connections, optimization, validation, and generation.

The first generated text is far from good, and that is actually useful. It gives me a real baseline rather than a polished demo with no understanding of what is happening underneath.

The next questions are now experimental ones:

- Does training for more epochs improve validation loss or simply increase memorization?
- How much does scaling the corpus improve grammar and coherence?
- How strongly do preprocessing artifacts affect generated output?
- At what point does training from scratch become less useful than adapting a pretrained small model?
