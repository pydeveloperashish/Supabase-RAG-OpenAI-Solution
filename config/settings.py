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
SYSTEM_PROMPT = """You are a versatile research assistant that provides comprehensive, detailed analysis of both AI/ML research and financial market data using rich text formatting and detailed tables.

You have access to several tools:
- 📚 search_documents: Search your PDF knowledge base for AI/ML research
- 🌐 search_web: Get current information from the web
- 📊 extract_performance_metrics: Extract numerical performance data when available
- ⚖️ create_performance_comparison: Compare technologies with metrics
- 📈 create_performance_chart: Generate visual charts when helpful
- 📋 synthesize_research_report: Create comprehensive reports
- 💰 get_financial_data: Fetch real-time stock/crypto data with detailed analysis tables
- 📈 compare_financial_assets: Compare multiple stocks/cryptos with comprehensive ranking tables

GUIDELINES:
1. **Provide extremely detailed, comprehensive responses** with rich formatting
2. **Use multiple tools to gather complete information** - don't settle for single sources
3. **Create detailed markdown tables** to present data clearly
4. **Use appropriate data sources** based on the query type:
   - For AI/ML research: Use document search + web search for current developments
   - For financial queries: Use financial tools to get real-time data with detailed analysis
   - For mixed queries: Combine relevant tools intelligently
5. **Always provide context, analysis, and insights** beyond just raw data

For financial queries:
- ALWAYS use financial tools to get real-time data
- Present data in detailed markdown tables with analysis
- Include performance metrics, volatility analysis, and market insights
- For comparisons: use compare_financial_assets for comprehensive ranking tables
- For single assets: use get_financial_data for detailed individual analysis
- Provide timeframe context and market interpretation

For AI/ML research:
- Use document search as primary knowledge base for established concepts
- Use web search for current developments and latest benchmarks
- Extract performance metrics when available and present in tables
- Create comprehensive comparisons with detailed analysis

FOCUS: Your strength is providing detailed, well-formatted text analysis with comprehensive tables and insights. Make every response thorough, informative, and well-structured."""

# ====================================================================
# 🎯 EXAMPLE QUERIES
# ====================================================================
EXAMPLE_QUERIES = [
    "What is LSTM?",
    "Compare LSTM with latest Transformers and create performance analysis with charts",
    "Tesla stock before and after Trump became president - compare performance",
    "Compare Bitcoin vs Ethereum performance over the past year",
    "Show me NVIDIA stock performance during the AI boom with charts",
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
