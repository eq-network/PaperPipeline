from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.node_parser import SimpleNodeParser
from typing import List, Optional

class IndexManager:
    """Manages the creation and access of vector indices for research papers."""
    
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.index = None
        
    def create_index(self, documents: List[Document], force_rebuild: bool = False) -> None:
        """Create or load the vector index for the documents."""
        index_exists = os.path.exists(os.path.join(self.storage_dir, "docstore.json"))
        
        if index_exists and not force_rebuild:
            # Load existing index
            storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
            self.index = load_index_from_storage(storage_context)
        else:
            # Create nodes with metadata preservation
            parser = SimpleNodeParser.from_defaults()
            nodes = parser.get_nodes_from_documents(documents)
            
            # Create and persist index
            self.index = GPTVectorStoreIndex(nodes)
            self.index.storage_context.persist(persist_dir=self.storage_dir)
    
    def get_index(self):
        """Get the current index."""
        if not self.index:
            if os.path.exists(os.path.join(self.storage_dir, "docstore.json")):
                storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
                self.index = load_index_from_storage(storage_context)
            else:
                raise ValueError("Index not created yet")
        return self.index