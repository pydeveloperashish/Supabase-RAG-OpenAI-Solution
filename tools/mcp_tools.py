"""
MCP Tool Definitions for the RAG Application
"""
import re
import json
import base64
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from typing import Dict, List, Any
from datetime import datetime

from config import METRIC_PATTERNS, DEFAULT_SEARCH_RESULTS


def search_documents(query: str, num_results: int = DEFAULT_SEARCH_RESULTS, retriever=None) -> Dict[str, Any]:
    """
    Search through vectorized PDF documents for relevant information
    
    Args:
        query: The search query to find relevant document chunks
        num_results: Number of relevant chunks to retrieve (default: 5)
        retriever: Vector store retriever instance
        
    Returns:
        Dict containing search results and sources
    """
    if not retriever:
        raise ValueError("Retriever instance is required")
        
    try:
        # Use existing vector store retriever
        docs = retriever.get_relevant_documents(query)[:num_results]
        
        results = []
        sources = set()
        
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "Unknown")
            })
            if doc.metadata.get("source"):
                sources.add(doc.metadata.get("source"))
        
        return {
            "results": results,
            "sources": list(sources),
            "total_found": len(results),
            "query": query
        }
    except Exception as e:
        return {
            "error": f"Document search failed: {str(e)}",
            "results": [],
            "sources": [],
            "total_found": 0,
            "query": query
        }


def search_web(query: str, num_results: int = DEFAULT_SEARCH_RESULTS) -> Dict[str, Any]:
    """
    Search the web for current information about a topic
    
    Args:
        query: The search query
        num_results: Number of results to return
        
    Returns:
        Dict containing web search results
    """
    try:
        # Using DuckDuckGo search (free alternative)
        import duckduckgo_search
        with duckduckgo_search.DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "snippet": result.get("body", ""),
                "url": result.get("href", ""),
                "source": "Web Search"
            })
            
        return {
            "results": formatted_results,
            "total_found": len(formatted_results),
            "query": query,
            "search_type": "web"
        }
    except ImportError:
        return {
            "error": "Web search not available. Install duckduckgo-search: pip install duckduckgo-search",
            "results": [],
            "total_found": 0,
            "query": query
        }
    except Exception as e:
        return {
            "error": f"Web search failed: {str(e)}",
            "results": [],
            "total_found": 0,
            "query": query
        }


def extract_performance_metrics(text: str, technology: str) -> Dict[str, Any]:
    """
    Extract performance metrics from text about a specific technology
    
    Args:
        text: Text containing performance information
        technology: Name of the technology being analyzed
        
    Returns:
        Dict containing extracted metrics
    """
    try:
        # Simple metric extraction using patterns
        metrics = {}
        
        text_lower = text.lower()
        for metric, pattern in METRIC_PATTERNS.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    metrics[metric] = float(matches[0])
                except ValueError:
                    pass
        
        return {
            "name": technology,
            "metrics": metrics,
            "source_text_length": len(text),
            "metrics_found": len(metrics)
        }
        
    except Exception as e:
        return {
            "name": technology,
            "metrics": {},
            "error": f"Metric extraction failed: {str(e)}"
        }


def create_performance_comparison(data1: Dict, data2: Dict, title: str = "Performance Comparison") -> Dict[str, Any]:
    """
    Create a performance comparison between two technologies/methods with visual chart
    
    Args:
        data1: First dataset with metrics
        data2: Second dataset with metrics  
        title: Chart title
        
    Returns:
        Dict containing comparison analysis and chart
    """
    try:
        # Extract metrics for comparison
        metrics1 = data1.get("metrics", {})
        metrics2 = data2.get("metrics", {})
        
        # Common metrics to compare
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())
        
        if not common_metrics:
            return {
                "error": "No common metrics found for comparison",
                "analysis": "Cannot compare - no overlapping metrics"
            }
        
        # Generate text analysis
        analysis_points = []
        for metric in common_metrics:
            val1, val2 = metrics1[metric], metrics2[metric]
            if val1 > val2:
                analysis_points.append(f"{data1.get('name', 'Method 1')} performs better in {metric}")
            elif val2 > val1:
                analysis_points.append(f"{data2.get('name', 'Method 2')} performs better in {metric}")
            else:
                analysis_points.append(f"Similar performance in {metric}")
        
        # Create visual chart
        chart_data = None
        chart_base64 = None
        
        try:
            # Prepare data for plotting
            metrics_list = list(common_metrics)
            values1 = [metrics1[m] for m in metrics_list]
            values2 = [metrics2[m] for m in metrics_list]
            
            # Create comparison chart
            plt.figure(figsize=(10, 6))
            x = range(len(metrics_list))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], values1, width, 
                   label=data1.get('name', 'Method 1'), alpha=0.8, color='#1f77b4')
            plt.bar([i + width/2 for i in x], values2, width, 
                   label=data2.get('name', 'Method 2'), alpha=0.8, color='#ff7f0e')
            
            plt.xlabel('Metrics')
            plt.ylabel('Performance Values')
            plt.title(title)
            plt.xticks(x, metrics_list, rotation=45, ha='right')
            plt.legend()
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Convert chart to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            chart_data = {
                "metrics": metrics_list,
                "values1": values1,
                "values2": values2,
                "chart_base64": chart_base64
            }
            
        except Exception as chart_error:
            print(f"Chart creation failed: {chart_error}")
        
        return {
            "analysis": " | ".join(analysis_points),
            "title": title,
            "metrics_compared": len(common_metrics),
            "data1_name": data1.get("name", "Method 1"),
            "data2_name": data2.get("name", "Method 2"),
            "chart_data": chart_data,
            "has_chart": chart_data is not None
        }
        
    except Exception as e:
        return {
            "error": f"Comparison creation failed: {str(e)}",
            "analysis": "Analysis failed"
        }


def synthesize_research_report(document_results: Dict, web_results: Dict, comparison_data: Dict = None) -> str:
    """
    Synthesize a comprehensive research report from multiple sources
    
    Args:
        document_results: Results from document search
        web_results: Results from web search
        comparison_data: Optional comparison analysis
        
    Returns:
        Formatted research report
    """
    try:
        report_sections = []
        
        # Header
        report_sections.append("# 📊 Comprehensive Research Report")
        report_sections.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Document findings
        if document_results.get("results"):
            report_sections.append("## 📚 Document Database Findings")
            report_sections.append(f"Found {document_results['total_found']} relevant documents.")
            
            for i, result in enumerate(document_results["results"][:3], 1):
                content_preview = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                report_sections.append(f"**{i}. {result['source']}**")
                report_sections.append(content_preview)
                report_sections.append("")
        
        # Web findings
        if web_results.get("results"):
            report_sections.append("## 🌐 Current Web Information")
            report_sections.append(f"Found {web_results['total_found']} current sources.")
            
            for i, result in enumerate(web_results["results"][:3], 1):
                report_sections.append(f"**{i}. {result['title']}**")
                report_sections.append(result["snippet"])
                report_sections.append(f"*Source: {result['url']}*")
                report_sections.append("")
        
        # Comparison analysis
        if comparison_data and comparison_data.get("analysis"):
            report_sections.append("## ⚖️ Performance Analysis")
            report_sections.append(comparison_data["analysis"])
        
        # Sources summary
        all_sources = []
        if document_results.get("sources"):
            all_sources.extend(document_results["sources"])
        if web_results.get("results"):
            all_sources.extend([r["url"] for r in web_results["results"]])
        
        if all_sources:
            report_sections.append("## 📖 Sources")
            for source in set(all_sources):
                report_sections.append(f"- {source}")
        
        return "\n".join(report_sections)
        
    except Exception as e:
        return f"Report synthesis failed: {str(e)}"


def create_performance_chart(metrics_data: List[Dict], title: str = "Performance Chart") -> Dict[str, Any]:
    """
    Create a standalone performance chart from metrics data
    
    Args:
        metrics_data: List of dictionaries with 'name' and 'metrics' keys
        title: Chart title
        
    Returns:
        Dict containing chart data and base64 image
    """
    try:
        if not metrics_data or len(metrics_data) < 2:
            return {"error": "Need at least 2 datasets to create comparison chart"}
        
        # Extract all metrics across datasets
        all_metrics = set()
        for data in metrics_data:
            all_metrics.update(data.get("metrics", {}).keys())
        
        if not all_metrics:
            return {"error": "No metrics found in provided data"}
        
        # Create chart
        plt.figure(figsize=(12, 8))
        metrics_list = sorted(list(all_metrics))
        x = range(len(metrics_list))
        width = 0.8 / len(metrics_data)
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, data in enumerate(metrics_data):
            name = data.get("name", f"Method {i+1}")
            metrics = data.get("metrics", {})
            values = [metrics.get(m, 0) for m in metrics_list]
            
            offset = (i - len(metrics_data)/2 + 0.5) * width
            plt.bar([j + offset for j in x], values, width, 
                   label=name, alpha=0.8, color=colors[i % len(colors)])
        
        plt.xlabel('Performance Metrics')
        plt.ylabel('Values')
        plt.title(title)
        plt.xticks(x, metrics_list, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            "title": title,
            "chart_base64": chart_base64,
            "metrics_included": metrics_list,
            "datasets_compared": len(metrics_data)
        }
        
    except Exception as e:
        return {"error": f"Chart creation failed: {str(e)}"}


# ====================================================================
# 🔧 TOOL REGISTRY
# ====================================================================

TOOL_FUNCTIONS = {
    "search_documents": search_documents,
    "search_web": search_web, 
    "extract_performance_metrics": extract_performance_metrics,
    "create_performance_comparison": create_performance_comparison,
    "create_performance_chart": create_performance_chart,
    "synthesize_research_report": synthesize_research_report
}


def execute_function_call(function_name: str, arguments: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute a function call and return the result"""
    
    if function_name not in TOOL_FUNCTIONS:
        return {"error": f"Function {function_name} not found"}
    
    try:
        # Add any additional kwargs (like retriever) to arguments
        arguments.update(kwargs)
        result = TOOL_FUNCTIONS[function_name](**arguments)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": f"Function execution failed: {str(e)}"}
