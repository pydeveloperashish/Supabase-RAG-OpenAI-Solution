"""
Vector store initialization and management
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL, 
    CHUNKS_TABLE,
    CHUNKS_QUERY_FUNCTION,
    VECTOR_SEARCH_LIMIT
)
from supabase_db import supabase


class VectorStoreManager:
    """Manages vector store and retriever initialization"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        self.openai_client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize all components"""
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Initialize vector store
        self.vector_store = SupabaseVectorStore(
            client=supabase, 
            table_name=CHUNKS_TABLE, 
            query_name=CHUNKS_QUERY_FUNCTION, 
            embedding=self.embeddings
        )
        
        # Initialize retriever
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": VECTOR_SEARCH_LIMIT}
        )
    
    def get_retriever(self):
        """Get the vector store retriever"""
        return self.retriever
    
    def get_vector_store(self):
        """Get the vector store instance"""
        return self.vector_store
    
    def get_embeddings(self):
        """Get the embeddings instance"""
        return self.embeddings
    
    def get_openai_client(self):
        """Get the OpenAI client"""
        return self.openai_client
