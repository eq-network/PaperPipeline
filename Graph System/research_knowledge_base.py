from modules.processing.document_manager import DocumentManager
from modules.indexing.index_manager import IndexManager
from modules.retrieval.research_query_engine import ResearchQueryEngine
from modules.synthesis.insight_generator import InsightGenerator

class ResearchKnowledgeBase:
    """Unified interface for the research knowledge system."""
    
    def __init__(self, processed_dir: str, storage_dir: str):
        self.document_manager = DocumentManager(processed_dir)
        self.index_manager = IndexManager(storage_dir)
        self.query_engine = ResearchQueryEngine(self.index_manager)
        self.insight_generator = InsightGenerator(self.index_manager)
        
    def initialize(self, force_rebuild=False):
        """Initialize the knowledge base."""
        # Load documents
        documents = self.document_manager.load_documents()
        
        # Create/load index
        self.index_manager.create_index(documents, force_rebuild=force_rebuild)
        
    def search(self, query_text, num_results=5, **filters):
        """Search for relevant papers."""
        return self.query_engine.query_papers(query_text, num_results, filters)
    
    def generate_literature_review(self, topic):
        """Generate a synthesized literature review on a topic."""
        return self.insight_generator.generate_literature_review(topic)
    
    def identify_research_gaps(self, topic):
        """Identify potential research gaps in the literature."""
        return self.insight_generator.identify_gaps(topic)