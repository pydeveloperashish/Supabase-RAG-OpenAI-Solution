"""
Configuration settings for the MCP RAG Application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ====================================================================
# 🔧 API KEYS & CREDENTIALS
# ====================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ====================================================================
# 🎛️ MODEL CONFIGURATIONS
# ====================================================================
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
TEMPERATURE = 0
STREAMING = True

# ====================================================================
# 🗄️ DATABASE CONFIGURATIONS
# ====================================================================
CHUNKS_TABLE = "chunks"
CHUNKS_QUERY_FUNCTION = "match_chunks"
VECTOR_SEARCH_LIMIT = 5

# ====================================================================
# 🔍 SEARCH CONFIGURATIONS
# ====================================================================
DEFAULT_SEARCH_RESULTS = 5
WEB_SEARCH_RESULTS = 5

# ====================================================================
# 🎨 UI CONFIGURATIONS
# ====================================================================
CHAT_LINES = 22
CHAT_SCALE = 3
SIDEBAR_SCALE = 1

# ====================================================================
# 📊 PERFORMANCE METRICS PATTERNS
# ====================================================================
METRIC_PATTERNS = {
    "accuracy": r"accuracy[:\s]*([0-9]+\.?[0-9]*)[%]?",
    "speed": r"speed[:\s]*([0-9]+\.?[0-9]*)",
    "memory": r"memory[:\s]*([0-9]+\.?[0-9]*)",
    "parameters": r"parameters?[:\s]*([0-9]+\.?[0-9]*)[MBK]?",
    "training_time": r"training[:\s]*([0-9]+\.?[0-9]*)",
    "inference_time": r"inference[:\s]*([0-9]+\.?[0-9]*)"
}

# ====================================================================
# 💬 SYSTEM PROMPTS
# ====================================================================
SYSTEM_PROMPT = """You are a research assistant that can search through document databases and the web to provide comprehensive, detailed answers about AI/ML topics.

You have access to several tools:
- 📚 search_documents: Search your PDF knowledge base
- 🌐 search_web: Get current information from the web
- 📊 extract_performance_metrics: Extract numerical performance data when available
- ⚖️ create_performance_comparison: Compare technologies with metrics
- 📈 create_performance_chart: Generate visual charts when helpful
- 📋 synthesize_research_report: Create comprehensive reports

GUIDELINES:
1. **Prioritize comprehensive, detailed responses** over forced tool usage
2. **Use web search when you need current information** or when documents don't have enough detail
3. **Use document search as your primary knowledge base** for established concepts
4. **Only extract metrics and create charts when you find substantial numerical data** that would benefit from visualization
5. **Don't force chart generation** if the data is primarily qualitative or conceptual
6. **Provide detailed explanations** even when using tools

For comparisons:
- Focus on providing thorough, nuanced analysis
- Use charts only when you have meaningful quantitative data to compare
- If no specific metrics are available, provide detailed qualitative comparison
- Let the content guide whether visualization adds value

Remember: Your goal is to provide the most helpful, comprehensive answer possible. Tools should enhance your response, not constrain it."""

# ====================================================================
# 🎯 EXAMPLE QUERIES
# ====================================================================
EXAMPLE_QUERIES = [
    "What is LSTM?",
    "Compare LSTM with latest Transformers and create performance analysis with charts",
    "Extract performance metrics from LSTM and Transformer papers and visualize comparison", 
    "Research current state of neural networks and create performance charts"
]

# ====================================================================
# 🛡️ VALIDATION
# ====================================================================
def validate_config():
    """Validate that all required configuration is present"""
    required_vars = [
        ("OPENAI_API_KEY", OPENAI_API_KEY),
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

# Validate configuration on import
validate_config()
