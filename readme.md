# Research Pipeline: From BibTeX to Knowledge System

This repository contains a streamlined research pipeline that transforms BibTeX citations into a queryable knowledge system. It automates PDF retrieval, extracts structured text using GROBID, and builds a semantic search system using LlamaIndex for intelligent retrieval.

## Overview

The system works in three main stages:

1. **PDF Acquisition**: Automatically retrieves PDFs based on your BibTeX citations
2. **Structured Text Extraction**: Processes PDFs with GROBID to extract structured text
3. **Knowledge Indexing**: Creates a semantic vector database for intelligent querying

## Prerequisites

- Python 3.8+
- Conda (recommended for environment management)
- Docker (required for running GROBID)
- OpenAI API key (for LlamaIndex embeddings)

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/research-pipeline.git
cd research-pipeline
```

### 2. Create a dedicated environment

```bash
# Create a new environment
conda create --name research-pipeline python=3.10

# Activate the environment
conda activate research-pipeline

# Install required packages
pip install bibtexparser requests lxml tqdm beautifulsoup4 llama-index openai langchain
```

### 3. Set up GROBID with Docker

GROBID is required for extracting structured text from PDFs. The easiest way to run it is using Docker:

```bash
# Pull the GROBID Docker image
docker pull lfoppiano/grobid:0.7.2

# Run GROBID container
docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2
```

The GROBID server will be accessible at http://localhost:8070

### 4. Set your OpenAI API key

```bash
# For Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# For Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

## Step-by-Step Usage Guide

### Step 1: Export BibTeX from Your Reference Manager

Export your citations from Zotero, Mendeley, or other reference managers as a BibTeX file (`.bib`).

### Step 2: Run the PDF Retrieval and Processing Pipeline

```bash
# Make sure GROBID is running (in a separate terminal)
# docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2

# Basic usage
python bibtoxml.py path/to/your_references.bib output_directory

# With title-based filenames (more readable)
python bibtoxml.py path/to/your_references.bib output_directory --use-title-filenames

# If running GROBID on a different server
python bibtoxml.py path/to/your_references.bib output_directory --grobid_url http://your-grobid-server:8070
```

This script:
- Downloads PDFs for each citation using DOI, arXiv ID, URL, or title search
- Processes each PDF with GROBID to extract structured text
- Saves the results in the organized output directory

### Step 3: Build the Knowledge Index

```bash
# Create and initialize the research knowledge base
python build_index.py --text_dir output_directory/text --index_dir research_index
```

This builds a semantic vector database from your processed documents.

### Step 4: Query Your Research Collection

```bash
# Simple query interface
python query_research.py --index_dir research_index --query "What are the recent advances in liquid democracy?"
```

## Directory Structure

After running the pipeline, you'll have the following structure:

```
output_directory/
├── pdfs/                # Downloaded PDF files
├── tei/                 # XML files from GROBID processing
└── text/                # Extracted structured text

research_index/          # Vector index and metadata
```

## Troubleshooting

### Common Issues

1. **Docker/GROBID Issues**:
   - Error: "Cannot connect to GROBID"
   - Solution: Ensure Docker is running and the GROBID container is active. Check with `docker ps`

2. **PDF Retrieval Failures**:
   - Many papers may fail to download if they're behind paywalls
   - Solution: Add your institutional email when configuring Unpaywall in the script
   ```python
   # In bibtoxml.py, update around line 190:
   email = "your-institutional-email@university.edu"
   ```

3. **Memory Issues with Large Collections**:
   - When processing many papers, you might encounter memory errors
   - Solution: Process in smaller batches by splitting your BibTeX file

4. **OpenAI API Rate Limits**:
   - When building the index, you might hit API rate limits
   - Solution: Add a delay between embedding requests in `build_index.py`

5. **Missing Dependencies**:
   - If you see import errors, you might be missing dependencies
   - Solution: Install the specific package with `pip install package-name`

## Scripts Included

- `bibtoxml.py`: Main pipeline for PDF retrieval and GROBID processing
- `build_index.py`: Creates the vector index from processed texts
- `query_research.py`: Interface for querying the knowledge base
- `research_insights.py`: Generates synthesized insights across papers

## Required Modifications

Before running, update these files with your information:

1. In `bibtoxml.py`: Set your email for the Unpaywall API
   ```python
   # Around line 190
   email = "your-email@example.com"  # Replace with your actual email
   ```

2. In `build_index.py`: Ensure the OpenAI model is correctly specified
   ```python
   # Check the model name is current
   llm = OpenAI(temperature=0, model="gpt-4")
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- GROBID for PDF text extraction
- LlamaIndex for knowledge indexing capabilities
- All the open access publishers and repositories making research accessible