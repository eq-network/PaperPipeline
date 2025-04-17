from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from .models import Document, Concept, Claim

class Agent(ABC):
    """Base class for all knowledge processing agents."""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inputs according to the agent's specialized function.
        
        Args:
            inputs: Dictionary of input parameters
            
        Returns:
            Dictionary of output results
        """
        pass

class LibrarianAgent(Agent):
    """
    Agent responsible for document retrieval and organization.
    """
    
    def __init__(self):
        super().__init__("librarian")
        
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        documents = inputs.get("documents", [])
        
        # Simple relevance-based retrieval
        relevant_docs = []
        for doc in documents:
            if self._calculate_relevance(query, doc) > 0.5:
                relevant_docs.append(doc)
                
        return {
            "relevant_documents": relevant_docs,
            "query": query
        }
        
    def _calculate_relevance(self, query: str, document: Document) -> float:
        """
        Calculate the relevance score between a query and document.
        
        A production implementation would use vector embeddings or more
        sophisticated relevance models.
        """
        # Simple term frequency implementation
        query_terms = set(query.lower().split())
        doc_content = document.content.lower()
        
        term_matches = sum(1 for term in query_terms if term in doc_content)
        if not query_terms:
            return 0.0
            
        return term_matches / len(query_terms)

class AnalystAgent(Agent):
    """
    Agent responsible for pattern recognition and concept extraction.
    """
    
    def __init__(self):
        super().__init__("analyst")
        
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        documents = inputs.get("relevant_documents", [])
        query = inputs.get("query", "")
        
        # Extract concepts from documents
        concepts = self._extract_concepts(documents)
        
        # Identify relationships between concepts
        concept_relationships = self._identify_relationships(concepts)
        
        # Extract claims from documents
        claims = self._extract_claims(documents)
        
        return {
            "concepts": concepts,
            "concept_relationships": concept_relationships,
            "claims": claims
        }
        
    def _extract_concepts(self, documents: List[Document]) -> List[Concept]:
        """
        Extract key concepts from a collection of documents.
        
        A production implementation would use NLP techniques like
        named entity recognition, keyphrase extraction, etc.
        """
        # Simple implementation that treats frequent terms as concepts
        term_frequency = {}
        
        for doc in documents:
            terms = [term.lower() for term in doc.content.split() 
                    if len(term) > 4]  # Simple filtering of short words
            
            for term in set(terms):  # Count each term once per document
                if term not in term_frequency:
                    term_frequency[term] = 0
                term_frequency[term] += 1
        
        # Create concepts for frequent terms
        concepts = []
        for term, frequency in term_frequency.items():
            if frequency >= 2:  # Appears in at least 2 documents
                concept = Concept(name=term)
                
                # Record occurrences
                for doc in documents:
                    if term.lower() in doc.content.lower():
                        concept.add_occurrence(doc.id, doc.content.lower().index(term.lower()))
                        
                concepts.append(concept)
                
        return concepts
        
    def _identify_relationships(self, concepts: List[Concept]) -> Dict[str, List[str]]:
        """
        Identify relationships between concepts based on co-occurrence.
        
        A production implementation would use more sophisticated
        co-occurrence analysis, knowledge graphs, etc.
        """
        relationships = {}
        
        for i, concept1 in enumerate(concepts):
            related = []
            for j, concept2 in enumerate(concepts):
                if i != j:
                    # Check for document overlap
                    common_docs = set(concept1.document_occurrences.keys()) & set(concept2.document_occurrences.keys())
                    if common_docs:
                        related.append(concept2.id)
            
            relationships[concept1.id] = related
            
        return relationships
        
    def _extract_claims(self, documents: List[Document]) -> List[Claim]:
        """
        Extract claims from documents.
        
        A production implementation would use NLP techniques for
        claim detection and attribution.
        """
        # Simple implementation that treats sentences ending with periods as claims
        claims = []
        
        for doc in documents:
            # Very basic sentence splitting - would be more sophisticated in production
            sentences = [s.strip() for s in doc.content.split('.') if s.strip()]
            
            for i, sentence in enumerate(sentences):
                # Heuristic: longer sentences that aren't questions might be claims
                if len(sentence) > 30 and not sentence.endswith('?'):
                    position = doc.content.find(sentence)
                    if position >= 0:
                        claim = Claim(
                            text=sentence,
                            source_document_id=doc.id,
                            source_position=position,
                            confidence=0.6  # Default confidence
                        )
                        claims.append(claim)
                        
        return claims