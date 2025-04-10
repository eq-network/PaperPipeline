# BibToXML: Academic PDF Retrieval and Processing Pipeline

This repository contains a streamlined pipeline for retrieving academic paper PDFs from BibTeX citations and extracting their structured content using GROBID. The system automates the tedious process of finding and processing research papers, saving you significant time when building a research corpus.

## Overview

The system works in two main stages:

1. **PDF Acquisition**: Automatically retrieves PDF files based on your BibTeX citations
2. **Structured Text Extraction**: Processes PDFs with GROBID to extract structured text in XML and plain text formats

## Prerequisites

- Python 3.8+
- Conda (recommended for environment management)
- Docker (required for running GROBID)

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/bibtoxml.git
cd bibtoxml
```

### 2. Create a dedicated environment

```bash
# Create a new environment
conda create --name bibtoxml python=3.10

# Activate the environment
conda activate bibtoxml

# Install required packages
pip install bibtexparser requests lxml tqdm beautifulsoup4
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

## Usage Guide

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

## Directory Structure

After running the pipeline, you'll have the following structure:

```
output_directory/
├── pdfs/                # Downloaded PDF files
├── tei/                 # XML files from GROBID processing
└── text/                # Extracted structured text in markdown format
```

## How It Works

The pipeline uses a multi-strategy approach to retrieve PDFs:

1. First tries to get the PDF using the paper's DOI through Unpaywall
2. If that fails, it checks for URLs in the BibTeX entry
3. Then tries to find ar