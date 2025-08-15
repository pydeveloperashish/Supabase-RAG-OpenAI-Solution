"""
Chat handling logic for the MCP RAG Application
"""
import json
import re
from typing import AsyncGenerator, Dict, Any
from openai import OpenAI

from config import OPENAI_MODEL, SYSTEM_PROMPT
from tools import execute_function_call, AVAILABLE_TOOLS
from supabase_db import create_chat, add_message, update_chat_title


class ChatHandler:
    """Handles chat interactions with OpenAI function calling"""
    
    def __init__(self, openai_client: OpenAI, retriever=None):
        self.client = openai_client
        self.retriever = retriever
        self.current_chat_id = None
    
    async def stream_answer_with_tools(self, user_msg: str) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI function calling"""
        
        if self.current_chat_id is None:
            self.current_chat_id = create_chat("New Chat")
        
        add_message(self.current_chat_id, "user", user_msg)
        yield f"🧑 **You:** {user_msg}\n\n🤖 **Bot:** "
        
        try:
            # Create messages for conversation
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
            
            # Step 1: Get initial response with potential function calls
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=AVAILABLE_TOOLS,
                tool_choice="auto"
            )
            
            initial_message = response.choices[0].message
            function_calls_made = []
            
            # Step 2: Handle function calls if any
            if initial_message.tool_calls:
                yield "🔧 **Executing tools...**\n\n"
                
                # Execute each function call
                for tool_call in initial_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    yield f"📋 **{function_name}**: {arguments.get('query', 'Executing...')}\n"
                    
                    # Execute the function with retriever if needed
                    kwargs = {}
                    if function_name == "search_documents" and self.retriever:
                        kwargs["retriever"] = self.retriever
                    
                    result = execute_function_call(function_name, arguments, **kwargs)
                    function_calls_made.append({
                        "function": function_name,
                        "arguments": arguments,
                        "result": result
                    })
                    
                    # Add function call and result to messages
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                yield "✅ **Tool execution complete. Checking for additional tools needed...**\n\n"
                
                # Step 3: Check if more function calls are needed (iterative function calling)
                max_iterations = 3  # Prevent infinite loops
                iteration = 0
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    # Get response (check if more tools needed)
                    response = self.client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=messages,
                        tools=AVAILABLE_TOOLS,
                        tool_choice="auto"
                    )
                    
                    # Check if more function calls are requested
                    if response.choices[0].message.tool_calls:
                        yield f"🔄 **Additional tools needed (iteration {iteration})...**\n\n"
                        
                        # Execute additional function calls
                        for tool_call in response.choices[0].message.tool_calls:
                            function_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)
                            
                            yield f"🛠️ **Calling:** {function_name}\n"
                            
                            # Execute the function
                            kwargs = {}
                            if function_name == "search_documents" and self.retriever:
                                kwargs["retriever"] = self.retriever
                            
                            result = execute_function_call(function_name, arguments, **kwargs)
                            function_calls_made.append({
                                "function": function_name,
                                "arguments": arguments,
                                "result": result
                            })
                            
                            # Add to messages
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call]
                            })
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result)
                            })
                    else:
                        # No more tools needed, generate final response
                        break
                
                yield "✅ **Generating final response...**\n\n"
                
                # Final response with streaming
                final_response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    stream=True
                )
                
                full_response = ""
                for chunk in final_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response += token
                        yield token
            
            else:
                # No function calls, just stream the regular response
                full_response = initial_message.content or ""
                yield full_response
            
            # Save to database
            add_message(self.current_chat_id, "bot", full_response)
            
            # Update chat title on first query
            short_title = " ".join(re.findall(r"\w+", user_msg)[:4])
            update_chat_title(self.current_chat_id, short_title)
            
            # Add function call summary and sources if any were made
            if function_calls_made:
                # Map function names to user-friendly descriptions
                tool_name_map = {
                    'search_documents': '📚 Document Search',
                    'search_web': '🌐 Web Search',
                    'extract_performance_metrics': '📊 Performance Analysis',
                    'create_performance_comparison': '⚖️ Performance Comparison',
                    'create_performance_chart': '📈 Chart Generation',
                    'synthesize_research_report': '📋 Report Synthesis'
                }
                
                # Get unique friendly names (avoid duplicates)
                friendly_names = []
                seen_functions = set()
                for fc in function_calls_made:
                    func_name = fc['function']
                    if func_name not in seen_functions:
                        friendly_name = tool_name_map.get(func_name, func_name)
                        friendly_names.append(friendly_name)
                        seen_functions.add(func_name)
                
                yield f"\n\n🧰 **Tools used:** {', '.join(friendly_names)}"
                
                # Extract and display sources from all searches
                doc_sources = set()
                web_sources = set()
                
                for fc in function_calls_made:
                    if fc['result'].get('success'):
                        data = fc['result'].get('data', {})
                        
                        # Document sources
                        if fc['function'] == 'search_documents' and data.get('sources'):
                            doc_sources.update(data['sources'])
                        
                        # Web sources  
                        elif fc['function'] == 'search_web' and data.get('results'):
                            for result in data['results'][:3]:  # Limit to top 3 web sources
                                if result.get('url'):
                                    web_sources.add(result['url'])
                
                # Display sources in separate lines (each source on its own line)
                if doc_sources:
                    yield f"\n\n📚 **Sources:**"
                    for source in sorted(doc_sources):
                        yield f"\nSource: {source}"
                
                if web_sources:
                    yield f"\n\n🌐 **Web Sources:**"
                    for source in list(web_sources)[:3]:
                        yield f"\nSource: {source}"
                
                # Display charts if any were created
                for fc in function_calls_made:
                    if fc['result'].get('success'):
                        data = fc['result'].get('data', {})
                        
                        # Check for chart data in comparison results
                        if fc['function'] == 'create_performance_comparison' and data.get('has_chart'):
                            chart_base64 = data.get('chart_data', {}).get('chart_base64')
                            if chart_base64:
                                yield f"\n\n📊 **Performance Comparison Chart:**\n![Performance Chart](data:image/png;base64,{chart_base64})"
                        
                        # Check for standalone chart results
                        elif fc['function'] == 'create_performance_chart' and data.get('chart_base64'):
                            chart_base64 = data.get('chart_base64')
                            title = data.get('title', 'Performance Chart')
                            yield f"\n\n📊 **{title}:**\n![{title}](data:image/png;base64,{chart_base64})"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield error_msg
            add_message(self.current_chat_id, "bot", error_msg)
    
    def get_current_chat_id(self) -> str:
        """Get the current chat ID"""
        return self.current_chat_id
    
    def set_current_chat_id(self, chat_id: str):
        """Set the current chat ID"""
        self.current_chat_id = chat_id
    
    def create_new_chat(self) -> str:
        """Create a new chat and set it as current"""
        self.current_chat_id = create_chat("New Chat")
        return self.current_chat_id
