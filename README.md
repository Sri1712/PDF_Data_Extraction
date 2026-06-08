# 📄 Exploration of PDF Processing Tools

> A comprehensive benchmarking study evaluating open-source and commercial PDF extraction tools for AI/LLM pipelines — across 226 pages, 5 document categories, and 11 quality dimensions.

**Presented by:** Srilathaa VASU 

---

## 📌 Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Test Corpus](#test-corpus)
- [Tools Evaluated](#tools-evaluated)
- [Evaluation Methodology](#evaluation-methodology)
- [Results](#results)
- [Quality vs. Latency](#quality-vs-latency)
- [Recommendations](#recommendations)
- [Commercial Tool Pricing](#commercial-tool-pricing)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [License](#license)

---

## Overview

PDF extraction quality is a critical upstream factor in the performance of AI systems. This project benchmarks **9 PDF extraction tools** — 7 open-source and 2 commercial — against a curated 226-page corpus to determine which tools are best suited for downstream AI applications such as RAG pipelines, document Q&A, and financial analytics.

---

## The Problem

Poor PDF extraction directly degrades AI system performance. Common failure modes include:

| Extraction Failure | AI Impact |
|---|---|
| Broken table structures | Incorrect financial insights |
| Missing or skipped text | Hallucinated responses |
| Incorrect reading order | Poor search & retrieval |
| OCR inaccuracies | Reduced answer accuracy |
| Lost document hierarchy | Increased manual verification |

---

## Test Corpus

**Total: 226 pages across 5 document categories**

| # | Category | Pages | File | Key Characteristics | What It Tests |
|---|---|---|---|---|---|
| 1 | Financial Statement | 53 | `1_Rapport-financier-semestriel-AFD-2025` | Financial tables, KPIs, structured reports | Table extraction, numerical accuracy, row/column preservation |
| 2 | Pitch Deck / CIM | 16 | `2_perfect-pitch-deck` | Slides, diagrams, visual-heavy layouts | Reading order, layout understanding, text from graphics |
| 3 | Legal / Contract | 23 | `3_NVCA-Model-Voting-Agreement` | Dense clauses, references, nested sections | Hierarchy preservation, clause extraction, long-text parsing |
| 4 | Scanned Document | 10 | `4_scanned_document` | Low-quality scan, OCR-dependent content | OCR robustness, noise handling, missing text detection |
| 5 | Annual Report | 124 | `5_ibm-annual-report-2025` | Mixed text, tables, charts, multi-column | End-to-end extraction across complex enterprise documents |

---

## Tools Evaluated

### Open-Source Tools

| Tool | Type | Output | Notes |
|---|---|---|---|
| [**PyMuPDF4LLM**](https://pymupdf4llm.readthedocs.io) | Rule-based | Markdown | Reads PDF byte stream → glyph positions → font heuristics → MD |
| **Docling** (IBM) | Model-based | Structured JSON | DocLayNet layout model + TableFormer; MIT licensed |
| **Unstructured** | Hybrid Framework | Structured Elements | Detect file type → partition strategy → layout/OCR processing |
| **Marker-pdf** | Hybrid | Markdown | PdfConverter/OcrConverter → document processing → structured elements |
| **OpenDataLoader** | Hybrid | Document Objects | Structured content extraction pipeline |
| **pdftotext + Docling** | Hybrid Combo | Markdown / JSON | pdftotext extraction fed into Docling for structure analysis |
| **pdftotext + PyMuPDF** | Hybrid Combo | Markdown | pdftotext raw text + PyMuPDF positional data |

### Commercial Tools

| Tool | Provider | Output | Notes |
|---|---|---|---|
| **LlamaParse** | LlamaIndex | Markdown + Images | Cloud OCR, layout analysis, table detection, image extraction |
| **Azure Document Intelligence** | Microsoft | Markdown + CSV | Page-by-page OCR, layout analysis, bounding-box extraction |

---

## Evaluation Methodology

The evaluation followed a 4-stage pipeline:

```
Ground Truth PDFs  →  Run Tools  →  Collect & Score Outputs  →  Rank Tools
      📄                  ⚙️                   📊                    🏆
```

### Quality Dimensions (11 Total)

| # | Dimension | Description |
|---|---|---|
| D1 | Text Accuracy | Character & word fidelity against ground truth |
| D2 | Reading Order | Logical document flow and correct content sequence |
| D3 | Table Structure | Preservation of cells, spans, and headers |
| D4 | Table Content | Accuracy of numerical values within tables |
| D5 | Heading / Section Hierarchy | Correct detection and nesting of document sections |
| D6 | Figure / Image Handling | Extraction or referencing of visual content |
| D7 | OCR Quality | Accuracy on scanned or image-based pages |
| D8 | RAG Output Quality | Suitability of output for retrieval-augmented generation |
| D9 | Metadata Preservation | Font data, coordinates, and structural metadata |
| D10 | Header/Footer Suppression | Removal of non-content elements from extracted text |
| D11 | Output Format Quality | Quality and usability of Markdown or JSON output |

All dimensions scored **1–5** by evaluators. Final rank based on weighted composite score.

---

## Results

### Comparative Performance Matrix

| Tool | D1: Text | D2: Order | D3: Tbl Struct | D4: Tbl Content | D5: Heading | D6: Figures | D7: OCR | D8: RAG | D9: Meta | D10: H/F | **Score** | **Rank** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LlamaParse | 4.80 | 4.60 | 4.67 | 4.00 | 4.40 | 3.67 | 3.50 | 4.20 | 4.00 | 3.80 | **4.02** | 🥇 1 |
| Docling | 3.60 | 4.00 | 4.00 | 3.67 | 4.00 | 2.00 | 3.50 | 3.60 | 3.60 | 3.20 | **3.45** | 🥈 2 |
| Azure Doc Intelligence | 4.00 | 3.80 | 3.25 | 4.00 | 3.40 | 3.00 | 3.00 | 3.40 | 3.60 | 3.80 | **3.36** | 🥉 3 |
| Marker | 3.60 | 3.40 | 3.33 | 3.67 | 3.80 | 3.00 | 3.00 | 3.40 | 3.80 | 3.60 | **3.32** | 4 |
| pdftotext + pymupdf | 4.20 | 4.00 | 3.67 | 3.67 | 2.00 | 2.67 | 3.00 | 3.60 | 3.60 | 3.60 | **3.31** | 5 |
| pdftotext + docling | 3.60 | 3.20 | 3.33 | 3.67 | 3.80 | 3.33 | 3.50 | 3.60 | 3.00 | 3.20 | **3.29** | 6 |
| PyMuPDF4LLM | 3.60 | 4.00 | 3.00 | 3.00 | 3.80 | 3.33 | 3.50 | 3.40 | 4.00 | 3.60 | **3.27** | 7 |
| OpenDataLoader | 3.00 | 3.40 | 1.50 | 2.50 | 2.80 | 2.50 | 1.00 | 2.60 | 2.80 | 2.80 | **2.34** | 8 |
| Unstructured | 2.60 | 2.00 | 1.50 | 2.00 | 2.20 | 1.50 | 1.00 | 1.80 | 2.20 | 2.60 | **1.85** | 9 |

---

## Quality vs. Latency

| Tool | Quality Score | Avg. Latency | Profile |
|---|---|---|---|
| ⭐ **LlamaParse** | 4.02 | 49–78s | **Best balance** — highest quality, moderate latency |
| ⚡ **pdftotext + PyMuPDF** | 3.31 | 4–49s | **Fastest** — efficient lightweight alternative |
| 📘 **Docling** | 3.45 | 60–120s | Strong quality, slower on complex/scanned docs |
| ☁️ **Azure Doc Intelligence** | 3.36 | 99–165s | High latency without proportional quality gain |
| ⚖️ **PyMuPDF4LLM** | 3.27 | 60–150s | Good quality, higher latency limits large-scale use |
| 📂 **OpenDataLoader** | 2.34 | 7–21s | Low latency but quality drops on OCR-heavy docs |
| ⬇️ **Unstructured** | 1.85 | Low | Lowest quality despite low latency |

---

## Recommendations

### ⭐ Primary Recommendation — LlamaParse

**Best for:** Production AI pipelines, financial document processing, RAG systems

✅ Highest table structure score (4.67) — critical for financial docs  
✅ Best RAG output quality (4.20) — direct uplift for document Q&A  
✅ Only tool with no major failures across all 5 document types  
✅ LangChain-native — minimal integration effort  

⚠️ API-only — documents leave your perimeter  
⚠️ Cost scales with volume — monitor at production load  

---

### 🏆 Best Open-Source — Docling (Surprise Result)

**Best for:** Privacy-sensitive deployments, on-premises environments, cost-conscious teams

✅ Best open-source table structure (4.00) via TableFormer ML model  
✅ Fully local — sensitive documents stay on-premises  
✅ MIT license — zero commercial restrictions  
✅ Strong heading detection (4.00) — clean RAG chunking  

⚠️ Weak on figures/charts (2.00) — images not extracted  
⚠️ GPU recommended for acceptable speed on long documents  

---

### ⚡ Best for Speed — pdftotext + PyMuPDF

**Best for:** High-throughput pipelines, text-heavy documents, cost-sensitive use cases

✅ Fastest processing (4–49 seconds)  
✅ Solid overall quality (3.31/5)  
✅ Fully open-source, no API dependency  

---

## Commercial Tool Pricing

### LlamaParse

| Tier | Price |
|---|---|
| Free | 10,000 credits/month (~10k pages Fast / ~3,300 pages Cost-effective) |
| Fast (paid) | $1.25 / 1,000 pages (1 credit/page) *(used in this benchmark)*|
| Cost-effective | $3.75 / 1,000 pages (3 credits/page) |
| Premium / Agentic | Up to $75 / 1,000 pages (up to 60 credits/page) |

### Azure Document Intelligence

| Model | Price |
|---|---|
| Free (F0) | 500 pages/month free |
| Read Model (S0) | $1.50 / 1,000 pages |
| Layout Model (S0) | $10.00 / 1,000 pages *(used in this benchmark)* |
| Custom Extraction | $30–$50 / 1,000 pages |

---

## Project Structure

```
pdf-extraction-benchmark/
│
├── corpus/
│   ├── 1_Rapport-financier-semestriel-AFD-2025.pdf
│   ├── 2_perfect-pitch-deck.pdf
│   ├── 3_NVCA-Model-Voting-Agreement.pdf
│   ├── 4_scanned_document.pdf
│   └── 5_ibm-annual-report-2025.pdf
|
├── ground_truth/
│   ├── 1_Rapport-financier-semestriel-AFD-2025
│   ├── 2_perfect-pitch-deck
│   ├── 3_NVCA-Model-Voting-Agreement
│   ├── 4_scanned_document
│   └── 5_ibm-annual-report-2025
│
├── notebooks/
│   └── pdf_extraction.ipynb
|
├── outputs/
│   ├── azure_di/
│   ├── docling/
│   ├── llama_parse
│   ├── marker/
│   ├── opendataloader/
│   ├── pdftotext_docling/
│   ├── pdftotext_pymupdf/
│   ├── pymupdf4llm/
│   └── unstructured/
│  
│
├── report/
│   ├── PDF extraction ppt.pdf 
│   ├── PDF_Processing_Tools_Report.pdf
│   └── pdf_tool_benchmark_rubric.xlsx
│
└── README.md
```

---

## Getting Started

### Prerequisites

```bash
pip install pymupdf4llm docling unstructured marker-pdf opendataloader
```

For commercial tools, set up API keys:

```bash
# LlamaParse
export LLAMA_CLOUD_API_KEY=your_key_here

# Azure Document Intelligence
export AZURE_DOC_INTEL_ENDPOINT=your_endpoint
export AZURE_DOC_INTEL_KEY=your_key_here
```

### Running a Tool (Example: Docling)

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("data/1_Rapport-financier-semestriel-AFD-2025.pdf")
print(result.document.export_to_markdown())
```

### Running a Tool (Example: PyMuPDF4LLM)

```python
import pymupdf4llm

md_text = pymupdf4llm.to_markdown("data/1_Rapport-financier-semestriel-AFD-2025.pdf")
print(md_text)
```

---

## License

This project and evaluation report are prepared by **Srilathaa VASU**.  
Test documents used for benchmarking purposes only. Individual tool licenses apply — see each tool's repository for details.

---

