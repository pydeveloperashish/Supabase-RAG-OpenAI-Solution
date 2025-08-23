"""
MCP Tool Definitions for the RAG Application
"""
import re
import json
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web apps
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from typing import Dict, List, Any
from datetime import datetime, timedelta
import yfinance as yf

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
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
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
        
        # Create chart with smaller size for better Gradio compatibility
        plt.figure(figsize=(8, 6))
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


def get_financial_data(symbol: str, period: str = "1y", data_type: str = "stock") -> Dict[str, Any]:
    """
    Fetch financial data for stocks or crypto using Yahoo Finance
    
    Args:
        symbol: Stock/crypto symbol (e.g., 'TSLA', 'BTC-USD')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        data_type: Type of financial instrument ('stock', 'crypto')
        
    Returns:
        Dict containing financial data and metrics
    """
    try:
        # Format symbol for different data types
        if data_type.lower() == "crypto" and "-USD" not in symbol.upper():
            symbol = f"{symbol.upper()}-USD"
        
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {
                "error": f"No data found for symbol {symbol}",
                "symbol": symbol,
                "data_type": data_type
            }
        
        # Calculate key metrics
        current_price = float(hist['Close'].iloc[-1])
        start_price = float(hist['Close'].iloc[0])
        high_price = float(hist['High'].max())
        low_price = float(hist['Low'].min())
        volume_avg = float(hist['Volume'].mean())
        
        # Calculate percentage change
        pct_change = ((current_price - start_price) / start_price) * 100
        
        # Get basic info
        info = ticker.info
        company_name = info.get('longName', info.get('shortName', symbol))
        
        # Prepare time series data for charting
        price_data = []
        for date, row in hist.iterrows():
            price_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "price": float(row['Close']),
                "volume": float(row['Volume'])
            })
        
        # Create detailed analysis text
        analysis_text = f"""
## 📊 **{company_name} ({symbol})** - Financial Analysis

### **Key Performance Metrics**

| Metric | Value | Analysis |
|--------|-------|----------|
| **Current Price** | ${current_price:.2f} | Latest trading price |
| **Start Price ({period})** | ${start_price:.2f} | Price at beginning of period |
| **Price Change** | ${current_price - start_price:.2f} | Absolute price movement |
| **Percentage Change** | **{pct_change:+.2f}%** | {'🟢 Positive growth' if pct_change > 0 else '🔴 Decline' if pct_change < 0 else '🟡 Neutral'} |
| **52-Week High** | ${high_price:.2f} | Peak price in period |
| **52-Week Low** | ${low_price:.2f} | Lowest price in period |
| **Average Volume** | {volume_avg:,.0f} shares | Daily trading activity |
| **Volatility** | {float(hist['Close'].pct_change().std() * 100):.2f}% | Price fluctuation measure |

### **Performance Summary**
Over the past {period}, **{company_name}** has {'gained' if pct_change > 0 else 'lost'} **{abs(pct_change):.2f}%** in value. The stock has traded in a range from **${low_price:.2f}** to **${high_price:.2f}**, showing {'high' if float(hist['Close'].pct_change().std() * 100) > 3 else 'moderate' if float(hist['Close'].pct_change().std() * 100) > 1.5 else 'low'} volatility.

### **Recent Price Action**
- **Current Level**: ${current_price:.2f}
- **Distance from High**: {((high_price - current_price) / high_price * 100):.1f}% below peak
- **Distance from Low**: {((current_price - low_price) / low_price * 100):.1f}% above trough
- **Trading Volume**: {'Above average' if volume_avg > 50000000 else 'Moderate' if volume_avg > 10000000 else 'Light'} volume suggests {'strong' if volume_avg > 50000000 else 'moderate' if volume_avg > 10000000 else 'limited'} investor interest
"""

        return {
            "symbol": symbol,
            "company_name": company_name,
            "data_type": data_type,
            "period": period,
            "current_price": current_price,
            "start_price": start_price,
            "price_change": current_price - start_price,
            "percentage_change": pct_change,
            "high_price": high_price,
            "low_price": low_price,
            "average_volume": volume_avg,
            "data_points": len(hist),
            "volatility": float(hist['Close'].pct_change().std() * 100),
            "analysis_text": analysis_text,
            "metrics": {
                "current_price": current_price,
                "percentage_change": pct_change,
                "volatility": float(hist['Close'].pct_change().std() * 100),
                "volume_avg": volume_avg
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to fetch financial data: {str(e)}",
            "symbol": symbol,
            "data_type": data_type
        }


def compare_financial_assets(symbols: List[str], period: str = "1y", data_types: List[str] = None) -> Dict[str, Any]:
    """
    Compare multiple financial assets and create comparative analysis
    
    Args:
        symbols: List of symbols to compare
        period: Time period for comparison
        data_types: List of data types for each symbol (defaults to 'stock' for all)
        
    Returns:
        Dict containing comparison data and analysis
    """
    try:
        if not symbols or len(symbols) < 2:
            return {"error": "Need at least 2 symbols for comparison"}
        
        if data_types is None:
            data_types = ["stock"] * len(symbols)
        elif len(data_types) != len(symbols):
            data_types = ["stock"] * len(symbols)
        
        # Fetch data for all symbols
        assets_data = []
        for symbol, data_type in zip(symbols, data_types):
            data = get_financial_data(symbol, period, data_type)
            if "error" not in data:
                assets_data.append(data)
        
        if len(assets_data) < 2:
            return {"error": "Could not fetch data for enough symbols"}
        
        # Create comparison metrics
        comparison_data = []
        for asset in assets_data:
            comparison_data.append({
                "name": f"{asset['company_name']} ({asset['symbol']})",
                "symbol": asset['symbol'],
                "metrics": {
                    "percentage_change": asset['percentage_change'],
                    "volatility": asset['metrics']['volatility'],
                    "current_price": asset['current_price']
                },
                "performance": asset['percentage_change']
            })
        
        # Sort by performance
        comparison_data.sort(key=lambda x: x['performance'], reverse=True)
        
        # Create detailed comparison table
        comparison_text = f"""
## 📈 **Financial Assets Comparison** ({period})

### **Performance Ranking**

| Rank | Company | Symbol | Performance | Current Price | Volatility | Status |
|------|---------|--------|-------------|---------------|------------|--------|"""
        
        for i, asset in enumerate(comparison_data, 1):
            status = "🟢 Winner" if i == 1 else "🔴 Loser" if i == len(comparison_data) else "🟡 Middle"
            comparison_text += f"""
| **{i}** | {asset['name'].split('(')[0].strip()} | {asset['symbol']} | **{asset['performance']:+.2f}%** | ${asset['metrics']['current_price']:.2f} | {asset['metrics']['volatility']:.2f}% | {status} |"""

        comparison_text += f"""

### **Key Insights**

- **🏆 Best Performer**: **{comparison_data[0]['name']}** with **{comparison_data[0]['performance']:+.2f}%** gain
- **📉 Worst Performer**: **{comparison_data[-1]['name']}** with **{comparison_data[-1]['performance']:+.2f}%** change
- **📊 Performance Spread**: {(comparison_data[0]['performance'] - comparison_data[-1]['performance']):.2f} percentage points between best and worst
- **⚖️ Market Sentiment**: {'Bullish overall' if sum(asset['performance'] for asset in comparison_data) > 0 else 'Bearish overall' if sum(asset['performance'] for asset in comparison_data) < 0 else 'Mixed sentiment'}

### **Volatility Analysis**

| Asset | Volatility | Risk Level |
|-------|------------|------------|"""
        
        for asset in comparison_data:
            vol = asset['metrics']['volatility']
            risk_level = "🔴 High Risk" if vol > 4 else "🟡 Medium Risk" if vol > 2 else "🟢 Low Risk"
            comparison_text += f"""
| {asset['symbol']} | {vol:.2f}% | {risk_level} |"""

        comparison_text += f"""

**Analysis Period**: {period} | **Assets Compared**: {len(comparison_data)}
"""
        
        return {
            "comparison_data": comparison_data,
            "period": period,
            "best_performer": comparison_data[0],
            "worst_performer": comparison_data[-1],
            "total_assets": len(comparison_data),
            "comparison_text": comparison_text,
            "analysis_summary": f"Compared {len(comparison_data)} assets over {period}"
        }
        
    except Exception as e:
        return {"error": f"Financial comparison failed: {str(e)}"}


def create_financial_chart(symbol: str = None, period: str = "1y", chart_type: str = "price", title: str = None, financial_data: Dict = None) -> Dict[str, Any]:
    """
    Create financial charts from financial data
    
    Args:
        symbol: Stock symbol (if financial_data not provided)
        period: Time period (if financial_data not provided) 
        chart_type: Type of chart ('price', 'comparison', 'performance')
        title: Chart title
        financial_data: Pre-fetched financial data (optional)
        
    Returns:
        Dict containing chart data and base64 image
    """
    try:
        # If no financial_data provided, fetch it using symbol and period
        if financial_data is None:
            if symbol is None:
                return {"error": "Either financial_data or symbol must be provided"}
            financial_data = get_financial_data(symbol, period)
            if "error" in financial_data:
                return {"error": f"Failed to fetch financial data: {financial_data['error']}"}
        
        plt.style.use('default')
        
        if chart_type == "comparison" and "comparison_data" in financial_data:
            # Create comparison chart
            data = financial_data["comparison_data"]
            names = [item["name"] for item in data]
            performances = [item["performance"] for item in data]
            
            plt.figure(figsize=(8, 6))
            colors = ['#2E8B57' if p >= 0 else '#DC143C' for p in performances]
            bars = plt.bar(range(len(names)), performances, color=colors, alpha=0.7)
            
            plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            plt.xlabel('Assets')
            plt.ylabel('Performance (%)')
            plt.title(title or f"Financial Performance Comparison ({financial_data.get('period', 'N/A')})")
            plt.xticks(range(len(names)), names, rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, performances):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1.5),
                        f'{value:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
                        
            plt.tight_layout()
            
        elif chart_type == "price" and "price_data" in financial_data:
            # Create price chart
            price_data = financial_data["price_data"]
            dates = [item["date"] for item in price_data]
            prices = [item["price"] for item in price_data]
            
            plt.figure(figsize=(8, 5))
            plt.plot(range(len(dates)), prices, linewidth=2, color='#1f77b4')
            plt.fill_between(range(len(dates)), prices, alpha=0.3, color='#1f77b4')
            
            plt.xlabel('Time')
            plt.ylabel('Price ($)')
            plt.title(title or f"{financial_data.get('company_name', 'Asset')} Price Chart")
            plt.xticks(range(0, len(dates), max(1, len(dates)//10)), 
                      [dates[i] for i in range(0, len(dates), max(1, len(dates)//10))], 
                      rotation=45)
            plt.grid(alpha=0.3)
            plt.tight_layout()
            
        else:
            return {"error": f"Unsupported chart type '{chart_type}' or missing required data"}
        
        # Save chart as both base64 and file for better compatibility
        import os
        import tempfile
        
        # Create temp file
        temp_dir = tempfile.gettempdir()
        chart_filename = f"financial_chart_{hash(str(financial_data))}.png"
        chart_path = os.path.join(temp_dir, chart_filename)
        
        # Save as file
        plt.savefig(chart_path, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        
        # Also create base64 for backward compatibility
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            "chart_type": chart_type,
            "chart_base64": chart_base64,
            "chart_path": chart_path,
            "title": title or "Financial Chart",
            "success": True
        }
        
    except Exception as e:
        return {"error": f"Financial chart creation failed: {str(e)}"}


# ====================================================================
# 🔧 TOOL REGISTRY
# ====================================================================

TOOL_FUNCTIONS = {
    "search_documents": search_documents,
    "search_web": search_web, 
    "extract_performance_metrics": extract_performance_metrics,
    "create_performance_comparison": create_performance_comparison,
    "create_performance_chart": create_performance_chart,
    "synthesize_research_report": synthesize_research_report,
    "get_financial_data": get_financial_data,
    "compare_financial_assets": compare_financial_assets
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
