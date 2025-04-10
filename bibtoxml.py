"""
BibTeX to Structured Text Pipeline

This script implements a streamlined pipeline for:
1. Retrieving PDFs based on BibTeX metadata
2. Processing PDFs with GROBID to extract structured text

Usage:
    python bibtex_to_structure.py path/to/bibtex.bib output_directory [grobid_url]

Requirements:
    - bibtexparser
    - requests
    - lxml
    - tqdm
"""

import os
import sys
import json
import time
import hashlib
import argparse
import bibtexparser
import requests
from lxml import etree
from tqdm import tqdm
import logging
from bs4 import BeautifulSoup
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BibTexToStructurePipeline:
    def __init__(self, bibtex_path, output_dir, grobid_url="http://localhost:8070"):
        """
        Initialize the pipeline with a BibTeX file and output directory.
        
        Args:
            bibtex_path: Path to the BibTeX file
            output_dir: Directory to save outputs
            grobid_url: URL of the GROBID service
        """
        self.bibtex_path = bibtex_path
        self.output_dir = output_dir
        self.grobid_url = grobid_url
        
        # Create necessary directories
        self.pdf_dir = os.path.join(output_dir, "pdfs")
        self.tei_dir = os.path.join(output_dir, "tei")
        self.txt_dir = os.path.join(output_dir, "text")
        
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.tei_dir, exist_ok=True)
        os.makedirs(self.txt_dir, exist_ok=True)
        
        # Load bibtex entries
        self.entries = self._load_bibtex()
        logger.info(f"Loaded {len(self.entries)} entries from BibTeX")

    def _title_to_filename(self, title):
        """Convert a paper title to a clean filename."""
        if not title:
            return None
        
        # Replace invalid filename characters
        import re
        title = re.sub(r'[/\\:*?"<>|]', ' ', title)
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        
        # Limit length and replace spaces with underscores
        if len(title) > 100:
            title = title[:100]
        title = title.replace(' ', '_')
        
        return title + ".pdf"
    
    def _load_bibtex(self):
        """Load and parse the BibTeX file."""
        with open(self.bibtex_path, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
            return bib_database.entries
    
    def _check_local_zotero_storage(self, entry):
        """Check if the PDF is already available in Zotero's storage folder."""
        import shutil
        import re
        
        # Get the Zotero storage path
        zotero_base_dir = os.path.join(os.path.expanduser("~"), "Zotero", "storage")
        if not os.path.exists(zotero_base_dir):
            logger.info("Zotero storage directory not found")
            return None
        
        # Get entry identifiers
        title = entry.get('title', '')
        doi = entry.get('doi', '').lower().strip()
        
        # Clean the title for matching
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        
        # Target path for this entry
        target_filename = self._title_to_filename(title) or f"{self._entry_to_filename(entry)}.pdf"
        target_path = os.path.join(self.pdf_dir, target_filename)
        
        # Method 1: Try to match by DOI
        if doi:
            for root, dirs, files in os.walk(zotero_base_dir):
                for file in files:
                    if file.endswith('.pdf') and doi in file.lower():
                        source_path = os.path.join(root, file)
                        shutil.copy2(source_path, target_path)
                        logger.info(f"Found PDF matching DOI: {source_path}")
                        return target_path
        
        # Method 2: Simple title matching
        if clean_title:
            # Get the first few words of the title (up to 3)
            title_start = ' '.join(clean_title.split()[:3])
            if len(title_start) >= 10:  # Only if we have enough text to be specific
                for root, dirs, files in os.walk(zotero_base_dir):
                    for file in files:
                        if file.endswith('.pdf') and title_start in file.lower():
                            source_path = os.path.join(root, file)
                            shutil.copy2(source_path, target_path)
                            logger.info(f"Found PDF matching title start: {source_path}")
                            return target_path
        
        logger.info(f"No matching PDF found in Zotero for: {title}")
        return None

    def _entry_to_filename(self, entry):
        """Create a safe filename from a BibTeX entry."""
        # Use the ID as the primary identifier
        entry_id = entry.get('ID', '')
        
        # If no ID, create one from title and year
        if not entry_id:
            title = entry.get('title', 'unknown')
            year = entry.get('year', '')
            entry_id = f"{title}_{year}"
        
        # Hash the ID to create a safe filename
        hash_object = hashlib.md5(entry_id.encode())
        return hash_object.hexdigest()
    
    def retrieve_pdfs(self):
        """Retrieve PDFs for each entry in the BibTeX file."""
        success_count = 0
        
        for entry in tqdm(self.entries, desc="Retrieving PDFs"):
            title = entry.get('title', '')
            
            # Try to use title for filename, fall back to ID-based name
            filename = self._title_to_filename(title)
            if not filename:
                # Use the original ID-based filename if title is not available
                safe_id = self._entry_to_filename(entry)
                filename = f"{safe_id}.pdf"
                
            pdf_path = os.path.join(self.pdf_dir, filename)
            
            # Skip if already downloaded
            if os.path.exists(pdf_path):
                logger.info(f"PDF already exists for {entry.get('title', 'Unknown Title')}")
                success_count += 1
                continue
            
            # Try to find in Zotero storage first (add this section)
            local_path = self._check_local_zotero_storage(entry)
            if local_path:
                # If we found a PDF in Zotero, it should already be copied to pdf_path
                logger.info(f"Using locally available PDF from Zotero for {entry.get('title', 'Unknown Title')}")
                success_count += 1
                continue
            
            # Rest of the method remains the same
            if self._retrieve_by_doi(entry, pdf_path):
                success_count += 1
                continue
            
            if self._retrieve_by_url(entry, pdf_path):
                success_count += 1
                continue
            
            if self._retrieve_by_arxiv(entry, pdf_path):
                success_count += 1
                continue
            
            if self._retrieve_by_title(entry, pdf_path):
                success_count += 1
                continue
            
            logger.warning(f"Could not retrieve PDF for {entry.get('title', 'Unknown Title')}")
        
        logger.info(f"Retrieved {success_count} PDFs out of {len(self.entries)} entries")
        return success_count
    
    def _retrieve_by_doi(self, entry, pdf_path):
        """Try to retrieve PDF using DOI."""
        doi = entry.get('doi')
        if not doi:
            return False
        
        # Try Unpaywall
        try:
            logger.info(f"Trying Unpaywall for DOI: {doi}")
            # Replace with your email for the Unpaywall API
            email = "your-email@example.com"
            response = requests.get(f"https://api.unpaywall.org/v2/{doi}?email={email}")
            
            if response.status_code == 200:
                data = response.json()
                best_oa_location = None
                
                # Find the best OA location
                if data.get('best_oa_location'):
                    best_oa_location = data['best_oa_location'].get('url_for_pdf')
                
                # If no direct PDF URL, try the landing page URL
                if not best_oa_location and data.get('best_oa_location'):
                    best_oa_location = data['best_oa_location'].get('url')
                
                # If we found a URL, download it
                if best_oa_location:
                    pdf_response = requests.get(best_oa_location, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        logger.info(f"Downloaded PDF for DOI {doi}")
                        return True
        except Exception as e:
            logger.error(f"Error retrieving PDF by DOI {doi}: {str(e)}")
        
        # Try SciHub as a fallback (note: legal status varies by country)
        # This is commented out but included as a reference
        try:
            logger.info(f"Trying alternative sources for DOI: {doi}")
            scihub_url = f"https://sci-hub.se/{doi}"
            
            # Use a session with a user agent to avoid blocks
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            response = session.get(scihub_url)
            
            # Extract the PDF URL from the SciHub page
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                iframe = soup.find('iframe', id='pdf')
                
                if iframe and iframe.get('src'):
                    pdf_url = iframe['src']
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                    
                    pdf_response = session.get(pdf_url)
                    if pdf_response.status_code == 200:
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        logger.info(f"Downloaded PDF for DOI {doi} from alternative source")
                        return True
        except Exception as e:
            logger.error(f"Error retrieving PDF from alternative source for DOI {doi}: {str(e)}")
        
        return False
    
    def _retrieve_by_arxiv(self, entry, pdf_path):
        """Try to retrieve PDF using arXiv ID."""
        # Extract arXiv ID if it exists in the entry
        arxiv_id = None
        
        # Check eprint field which often contains arXiv ID
        eprint = entry.get('eprint', '')
        if eprint and ('arxiv' in eprint.lower() or len(eprint.split('.')) == 2):
            # Try to extract the arXiv ID pattern
            import re
            match = re.search(r'(\d+\.\d+|[a-z\-]+/\d+v?\d*)', eprint)
            if match:
                arxiv_id = match.group(0)
        
        # Also check journal, note, and url fields
        for field in ['journal', 'note', 'url']:
            value = entry.get(field, '')
            if isinstance(value, str) and 'arxiv' in value.lower():
                import re
                match = re.search(r'(\d+\.\d+|[a-z\-]+/\d+v?\d*)', value)
                if match:
                    arxiv_id = match.group(0)
                    break
        
        if not arxiv_id:
            return False
        
        try:
            logger.info(f"Trying arXiv for ID: {arxiv_id}")
            # Clean the arXiv ID
            arxiv_id = arxiv_id.strip()
            if arxiv_id.startswith('arxiv:'):
                arxiv_id = arxiv_id[6:]
            
            # Form the arXiv PDF URL
            arxiv_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            # Download the PDF
            pdf_response = requests.get(arxiv_pdf_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                logger.info(f"Downloaded PDF for arXiv ID {arxiv_id}")
                return True
        except Exception as e:
            logger.error(f"Error retrieving PDF by arXiv ID {arxiv_id}: {str(e)}")
        
        return False
    
    def _retrieve_by_url(self, entry, pdf_path):
        """Try to retrieve PDF using URL directly from the BibTeX entry."""
        # Check various fields that might contain URLs
        url_fields = ['url', 'link', 'pdf', 'file']
        
        for field in url_fields:
            url = entry.get(field)
            if not url:
                continue
            
            # Clean up the URL
            url = url.strip()
            
            # Remove common prefixes like 'url = {' or unwanted characters
            if url.startswith('{') and url.endswith('}'):
                url = url[1:-1]
            
            # Skip if URL is not valid
            if not url.startswith(('http://', 'https://')):
                continue
            
            try:
                logger.info(f"Trying direct URL download: {url}")
                
                # If URL doesn't end with .pdf, it might be a landing page
                if not url.lower().endswith('.pdf'):
                    # Try to download anyway, it might redirect to a PDF
                    pdf_response = requests.get(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    # Check if it's a PDF
                    if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        logger.info(f"Downloaded PDF from URL: {url}")
                        return True
                    else:
                        # If it's not a PDF, try to extract PDF link from the page
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(pdf_response.text, 'html.parser')
                            
                            # Look for PDF links in the page
                            pdf_links = []
                            for a_tag in soup.find_all('a', href=True):
                                href = a_tag['href']
                                if href.lower().endswith('.pdf'):
                                    pdf_links.append(href)
                                elif 'pdf' in href.lower() or 'fulltext' in href.lower() or 'download' in href.lower():
                                    pdf_links.append(href)
                            
                            # Try each PDF link
                            for pdf_link in pdf_links:
                                # Handle relative URLs
                                if pdf_link.startswith('/'):
                                    from urllib.parse import urlparse
                                    base_url = urlparse(url)
                                    pdf_link = f"{base_url.scheme}://{base_url.netloc}{pdf_link}"
                                elif not pdf_link.startswith(('http://', 'https://')):
                                    # If it's not an absolute URL and not starting with /
                                    pdf_link = url.rstrip('/') + '/' + pdf_link
                                
                                try:
                                    pdf_response = requests.get(pdf_link, headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                                    })
                                    
                                    if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                                        with open(pdf_path, 'wb') as f:
                                            f.write(pdf_response.content)
                                        logger.info(f"Downloaded PDF from extracted link: {pdf_link}")
                                        return True
                                except Exception as e:
                                    logger.error(f"Error downloading PDF from extracted link {pdf_link}: {str(e)}")
                        except ImportError:
                            logger.warning("BeautifulSoup is not installed, skipping HTML parsing")
                        except Exception as e:
                            logger.error(f"Error parsing HTML from URL {url}: {str(e)}")
                else:
                    # Direct PDF URL
                    pdf_response = requests.get(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        logger.info(f"Downloaded PDF from direct URL: {url}")
                        return True
            except Exception as e:
                logger.error(f"Error retrieving PDF from URL {url}: {str(e)}")
        
        return False

    def _retrieve_by_title(self, entry, pdf_path):
        """Try to retrieve PDF using title search."""
        title = entry.get('title')
        if not title:
            return False
        
        # Try using Semantic Scholar API
        try:
            logger.info(f"Searching for title: {title}")
            
            # Clean the title
            import re
            title = re.sub(r'[^\w\s]', '', title)
            title = title.strip()
            
            # Search using Semantic Scholar API
            search_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=title,url,openAccessPdf"
            response = requests.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                
                # Try to find a matching paper with PDF URL
                for paper in papers:
                    if paper.get('openAccessPdf', {}).get('url'):
                        pdf_url = paper['openAccessPdf']['url']
                        
                        # Download the PDF
                        pdf_response = requests.get(pdf_url, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        })
                        
                        if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_response.content)
                            logger.info(f"Downloaded PDF for title: {title}")
                            return True
        except Exception as e:
            logger.error(f"Error retrieving PDF by title for {title}: {str(e)}")
        
        return False
    
    def process_with_grobid(self):
        """Process downloaded PDFs with GROBID to extract structured text."""
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        success_count = 0
        
        for pdf_file in tqdm(pdf_files, desc="Processing with GROBID"):
            pdf_path = os.path.join(self.pdf_dir, pdf_file)
            tei_path = os.path.join(self.tei_dir, pdf_file.replace('.pdf', '.tei.xml'))
            txt_path = os.path.join(self.txt_dir, pdf_file.replace('.pdf', '.txt'))
            
            # Skip if already processed
            if os.path.exists(tei_path) and os.path.exists(txt_path):
                logger.info(f"Already processed {pdf_file}")
                success_count += 1
                continue
            
            # Process with GROBID
            try:
                # Check if GROBID is running
                try:
                    health_check = requests.get(f"{self.grobid_url}/api/isalive")
                    if health_check.status_code != 200:
                        logger.error(f"GROBID is not running at {self.grobid_url}. Please start GROBID.")
                        return False
                except requests.exceptions.ConnectionError:
                    logger.error(f"Cannot connect to GROBID at {self.grobid_url}. Please check if GROBID is running.")
                    return False
                
                # Process with GROBID
                if not os.path.exists(tei_path):
                    self._process_pdf_with_grobid(pdf_path, tei_path)
                
                # Extract text from TEI XML
                if not os.path.exists(txt_path):
                    structured_text = self._extract_text_from_tei(tei_path)
                    
                    # Save the extracted text
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(structured_text)
                
                logger.info(f"Processed {pdf_file}")
                success_count += 1
                
                # Respect GROBID rate limits (adjust as needed)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing {pdf_file} with GROBID: {str(e)}")
        
        logger.info(f"Processed {success_count} PDFs out of {len(pdf_files)}")
        return success_count
    
    def _process_pdf_with_grobid(self, pdf_path, output_path):
        """Process a PDF with GROBID and save the TEI XML."""
        try:
            # Prepare the files for the request
            with open(pdf_path, 'rb') as pdf_file:
                files = {
                    'input': (os.path.basename(pdf_path), pdf_file, 'application/pdf')
                }
                
                # Make the request to GROBID
                response = requests.post(
                    f"{self.grobid_url}/api/processFulltextDocument",
                    files=files
                )
                
                if response.status_code == 200:
                    # Save the TEI XML response
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    return True
                else:
                    raise Exception(f"GROBID returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error in GROBID processing: {str(e)}")
            raise
    
    def _extract_text_from_tei(self, tei_path):
        """Extract structured text from TEI XML file."""
        try:
            # Parse the XML
            tree = etree.parse(tei_path)
            root = tree.getroot()
            
            # Define the namespaces
            namespaces = {
                'tei': 'http://www.tei-c.org/ns/1.0'
            }
            
            # Initialize the structured text
            structured_text = ""
            
            # Extract title
            title = root.xpath('//tei:titleStmt/tei:title/text()', namespaces=namespaces)
            if title:
                structured_text += f"# {title[0]}\n\n"
            
            # Extract authors
            authors = []
            for author in root.xpath('//tei:sourceDesc//tei:author', namespaces=namespaces):
                forename = author.xpath('.//tei:forename/text()', namespaces=namespaces)
                surname = author.xpath('.//tei:surname/text()', namespaces=namespaces)
                if forename and surname:
                    authors.append(f"{forename[0]} {surname[0]}")
                elif surname:
                    authors.append(surname[0])
            
            if authors:
                structured_text += f"## Authors\n{', '.join(authors)}\n\n"
            
            # Extract abstract
            abstract = root.xpath('//tei:profileDesc/tei:abstract//text()', namespaces=namespaces)
            if abstract:
                abstract_text = ' '.join([text.strip() for text in abstract if text.strip()])
                structured_text += f"## Abstract\n{abstract_text}\n\n"
            
            # Extract body text with section information
            structured_text += "## Content\n\n"
            
            for section in root.xpath('//tei:body/tei:div', namespaces=namespaces):
                section_title = section.xpath('./tei:head/text()', namespaces=namespaces)
                section_title = section_title[0] if section_title else 'Unnamed Section'
                
                structured_text += f"### {section_title}\n\n"
                
                section_text = section.xpath('.//text()[not(parent::tei:head)]', namespaces=namespaces)
                section_text = ' '.join([text.strip() for text in section_text if text.strip()]) if section_text else ''
                
                structured_text += f"{section_text}\n\n"
            
            # Extract bibliographic references
            refs = root.xpath('//tei:listBibl/tei:biblStruct', namespaces=namespaces)
            if refs:
                structured_text += "## References\n\n"
                
                for i, ref in enumerate(refs, 1):
                    ref_title = ref.xpath('.//tei:title[@type="main"]/text()', namespaces=namespaces)
                    ref_title = ref_title[0] if ref_title else "Untitled"
                    
                    ref_authors = []
                    for author in ref.xpath('.//tei:author', namespaces=namespaces):
                        forename = author.xpath('.//tei:forename/text()', namespaces=namespaces)
                        surname = author.xpath('.//tei:surname/text()', namespaces=namespaces)
                        if forename and surname:
                            ref_authors.append(f"{forename[0]} {surname[0]}")
                        elif surname:
                            ref_authors.append(surname[0])
                    
                    ref_date = ref.xpath('.//tei:date/@when', namespaces=namespaces)
                    ref_date = ref_date[0] if ref_date else ""
                    
                    ref_text = f"{i}. "
                    if ref_authors:
                        ref_text += f"{', '.join(ref_authors)}. "
                    if ref_date:
                        ref_text += f"({ref_date[:4]}). "
                    ref_text += f"{ref_title}."
                    
                    structured_text += f"{ref_text}\n"
            
            return structured_text
        except Exception as e:
            logger.error(f"Error extracting text from TEI: {str(e)}")
            return f"Error extracting text: {str(e)}"
    
    def run_pipeline(self):
        """Run the complete pipeline."""
        logger.info("Starting the BibTeX to Structured Text Pipeline")
        
        # Step 1: Retrieve PDFs
        logger.info("Step 1: Retrieving PDFs")
        pdf_count = self.retrieve_pdfs()
        
        # Check if we have any PDFs to process
        if pdf_count == 0:
            logger.warning("No PDFs retrieved. Stopping pipeline.")
            return False
        
        # Step 2: Process with GROBID
        logger.info("Step 2: Processing PDFs with GROBID")
        processed_count = self.process_with_grobid()
        
        logger.info(f"Pipeline completed: {processed_count} PDFs processed successfully")
        return processed_count > 0

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Process BibTeX entries to structured text using GROBID.')
    parser.add_argument('bibtex_path', help='Path to the BibTeX file')
    parser.add_argument('output_dir', help='Directory to save outputs')
    parser.add_argument('--grobid_url', default='http://localhost:8070', help='URL of the GROBID service')
    
    args = parser.parse_args()
    
    pipeline = BibTexToStructurePipeline(args.bibtex_path, args.output_dir, args.grobid_url)
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()