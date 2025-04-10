from llama_index import Document
from typing import List, Dict, Any

class DocumentManager:
    """Manages the processing of extracted research papers into LlamaIndex documents."""
    
    def __init__(self, processed_dir):
        self.processed_dir = processed_dir
        
    def load_documents(self) -> List[Document]:
        """Load all processed papers and convert to LlamaIndex Documents with metadata."""
        documents = []
        
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.processed_dir, filename)
                
                # Extract paper details from the structured text
                title, authors, publication_year, content = self._parse_structured_text(filepath)
                
                # Create document with rich metadata
                doc = Document(
                    text=content,
                    metadata={
                        "title": title,
                        "authors": authors,
                        "year": publication_year,
                        "filename": filename,
                        "source_type": "research_paper"
                    }
                )
                documents.append(doc)
                
        return documents
    
    def _parse_structured_text(self, filepath):
        """Parse the structured text from GROBID into components."""
        # Implementation to extract title, authors, etc. from your structured format
        # ...