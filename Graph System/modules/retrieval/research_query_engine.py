from typing import List, Dict, Any

class ResearchQueryEngine:
    """Specialized query engine for academic research retrieval."""
    
    def __init__(self, index_manager):
        self.index_manager = index_manager
        
    def query_papers(self, query_text: str, num_results: int = 5, 
                    filter_criteria: Optional[Dict[str, Any]] = None):
        """Query the research papers with advanced filtering capabilities."""
        index = self.index_manager.get_index()
        
        # Configure retrieval parameters with metadata filtering
        if filter_criteria:
            # E.g., filter by year, authors, etc.
            metadata_filter = lambda meta: all(
                meta.get(key) == value for key, value in filter_criteria.items()
            )
        else:
            metadata_filter = None
        
        # Create the query engine with appropriate settings
        query_engine = index.as_query_engine(
            similarity_top_k=num_results,
            node_postprocessors=[metadata_filter] if metadata_filter else None
        )
        
        # Execute query and process results
        response = query_engine.query(query_text)
        
        # Format and return results
        results = []
        for node in response.source_nodes:
            results.append({
                "title": node.metadata.get("title", "Unknown"),
                "authors": node.metadata.get("authors", "Unknown"),
                "year": node.metadata.get("year", "Unknown"),
                "relevance_score": node.score,
                "content_preview": node.text[:300] + "..." if len(node.text) > 300 else node.text
            })
            
        return results