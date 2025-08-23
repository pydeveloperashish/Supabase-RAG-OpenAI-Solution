"""
OpenAI Tool Definitions for Function Calling
"""

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search through the PDF document database for relevant information about ML/AI topics",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant document chunks"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of relevant chunks to retrieve (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "search_web",
            "description": "Search the web for current information about AI/ML topics, latest research, benchmarks",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for current information"
                    },
                    "num_results": {
                        "type": "integer", 
                        "description": "Number of search results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_performance_metrics", 
            "description": "Extract numerical performance metrics (accuracy, speed, memory, etc.) from text when quantitative data is available for analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text containing performance information"
                    },
                    "technology": {
                        "type": "string",
                        "description": "Name of the technology being analyzed"
                    }
                },
                "required": ["text", "technology"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_performance_comparison",
            "description": "Create a visual performance comparison chart between two technologies when meaningful quantitative metrics are available.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "data1": {
                        "type": "object",
                        "description": "First dataset with metrics and name"
                    },
                    "data2": {
                        "type": "object", 
                        "description": "Second dataset with metrics and name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title",
                        "default": "Performance Comparison"
                    }
                },
                "required": ["data1", "data2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_performance_chart",
            "description": "Create visual charts for performance comparisons when structured metrics data would benefit from visualization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics_data": {
                        "type": "array",
                        "description": "List of datasets with name and metrics for comparison",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "metrics": {"type": "object"}
                            }
                        }
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title",
                        "default": "Performance Chart"
                    }
                },
                "required": ["metrics_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize_research_report",
            "description": "Create a comprehensive report from document and web search results",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_results": {
                        "type": "object",
                        "description": "Results from document search"
                    },
                    "web_results": {
                        "type": "object",
                        "description": "Results from web search"
                    },
                    "comparison_data": {
                        "type": "object",
                        "description": "Optional comparison analysis data"
                    }
                },
                "required": ["document_results", "web_results"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_data",
            "description": "Fetch real-time financial data for stocks or cryptocurrencies including prices, performance metrics, and historical data",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., 'TSLA', 'AAPL') or crypto symbol (e.g., 'BTC', 'ETH')"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for data ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')",
                        "default": "1y"
                    },
                    "data_type": {
                        "type": "string", 
                        "description": "Type of financial instrument ('stock' or 'crypto')",
                        "default": "stock"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_financial_assets",
            "description": "Compare multiple stocks or cryptocurrencies to analyze relative performance and create comparison data",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of symbols to compare (e.g., ['TSLA', 'NVDA'] or ['BTC', 'ETH'])"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for comparison ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')",
                        "default": "1y"
                    },
                    "data_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data types for each symbol (['stock', 'crypto', ...]). Defaults to 'stock' for all."
                    }
                },
                "required": ["symbols"]
            }
        }
    }
]
