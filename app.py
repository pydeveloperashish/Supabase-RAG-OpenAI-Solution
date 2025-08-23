"""
Main application entry point for the MCP RAG System
"""
from core import ChatHandler, VectorStoreManager
from ui import GradioInterface


def main():
    """Initialize and launch the application"""
    
    # Initialize vector store and components
    print("🔧 Initializing vector store...")
    vector_manager = VectorStoreManager()
    
    # Initialize chat handler
    print("💬 Initializing chat handler...")
    chat_handler = ChatHandler(
        openai_client=vector_manager.get_openai_client(),
        retriever=vector_manager.get_retriever()
    )
    
    # Initialize UI
    print("🎨 Initializing user interface...")
    ui = GradioInterface(chat_handler)
    
    # Launch application
    print("🚀 Launching application...")
    ui.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
