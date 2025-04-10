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

### 4. Configure the application

Create a `config.py` file based on the template provided. This file contains all the configurable settings for the application:

```bash
# Copy the template configuration file
cp config_template.py config.py

# Edit the configuration file with your preferred editor
nano config.py  # or use any text editor
```

Make sure to update:
- Your email address for API services
- Path to your Zotero storage (if applicable)
- Enable/disable different retrieval sources
- Adjust other settings as needed

## Usage Guide

### Step 1: Export BibTeX from Your Reference Manager

Export your citations from Zotero, Mendeley, or other reference managers as a BibTeX file (`.bib`).

### Step 2: Run the PDF Retrieval and Processing Pipeline

```bash
# Make sure GROBID is running (in a separate terminal)
# docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2

# Basic usage
python bibtex_to_structure.py path/to/your_references.bib output_directory

# If running GROBID on a different server
python bibtex_to_structure.py path/to/your_references.bib output_directory --grobid_url http://your-grobid-server:8070
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

1. First checks if the PDF is already available in your local Zotero storage
2. Then tries to get the PDF using the paper's DOI through Unpaywall
3. If that fails, it checks for URLs in the BibTeX entry
4. Then tries to find arXiv papers using arXiv IDs
5. Finally, searches for the paper by title using Semantic Scholar

The configuration file allows you to enable or disable specific retrieval sources.

## Configuration Options

The `config.py` file contains several settings you can customize:

- **User Information**: Email address for API services
- **Paths**: Location of Zotero storage directory
- **Network Settings**: User agent for HTTP requests
- **API Configuration**: Service-specific settings
- **Processing Settings**: Rate limits, filename length, etc.
- **Retrieval Sources**: Enable/disable different PDF sources
- **Service URLs**: API endpoints for various services

## Troubleshooting

### Common Issues

1. **GROBID Connection Errors**
   - Make sure GROBID is running and accessible at the configured URL
   - Check if the port (default: 8070) is not blocked by a firewall

2. **PDF Retrieval Failures**
   - Verify your internet connection
   - Check if your API email is correctly configured
   - Some papers may be behind paywalls and inaccessible

3. **Configuration Problems**
   - Ensure you've created a `config.py` file based on the template
   - Verify all paths and URLs are correctly configured

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [GROBID](https://github.com/kermitt2/grobid) for PDF processing
- [Unpaywall](https://unpaywall.org/) and [Semantic Scholar](https://www.semanticscholar.org/) for open access paper retrieval
- The academic community's ongoing efforts toward open science and accessible research