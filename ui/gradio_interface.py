"""
Gradio UI components for the MCP RAG Application
"""
import gradio as gr
from typing import Callable, AsyncGenerator, Generator
import asyncio

from config import CHAT_LINES, CHAT_SCALE, SIDEBAR_SCALE, EXAMPLE_QUERIES
from supabase_db import get_chat_messages, get_all_chats


class GradioInterface:
    """Manages the Gradio user interface"""
    
    def __init__(self, chat_handler):
        self.chat_handler = chat_handler
        self.demo = None
        self._create_interface()
    
    def _create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(theme=gr.themes.Soft()) as demo:
            # Header
            gr.Markdown("## 🤖 AI Research Assistant (MCP + Function Calling)")
            gr.Markdown("*Ask me to compare technologies, analyze performance, or research latest developments!*")
            
            # Main layout
            with gr.Row():
                # Chat area
                with gr.Column(scale=CHAT_SCALE):
                    chat_window = gr.Chatbot(label="Chat", height=600, container=True)
                
                # Sidebar
                with gr.Column(scale=SIDEBAR_SCALE):
                    gr.Markdown("### 💬 Chat History")
                    chat_selector = gr.Dropdown(
                        choices=self._get_chat_titles(), 
                        label="Chats", 
                        interactive=True
                    )
                    new_btn = gr.Button("➕ New Chat")
                    
                    gr.Markdown("### 🔧 Available Tools")
                    gr.Markdown("""
                    - 📚 **Document Search** - Search PDF database
                    - 🌐 **Web Search** - Current information  
                    - 📊 **Performance Analysis** - Extract metrics
                    - ⚖️ **Comparison Tools** - Compare technologies
                    - 📈 **Chart Generation** - Create visual comparisons
                    - 📋 **Report Generation** - Synthesize findings
                    """)
                    
                    gr.Markdown("### 💡 Example Queries")
                    for query in EXAMPLE_QUERIES:
                        gr.Markdown(f"- *{query}*")
            
            # Query input
            query_box = gr.Textbox(
                label="Your Question", 
                placeholder="e.g., 'Compare LSTM with latest Transformers and create performance analysis'"
            )
            
            # Event handlers
            query_box.submit(self._respond, [query_box, chat_window], chat_window)
            chat_selector.change(self._select_chat, chat_selector, chat_window)
            new_btn.click(self._new_chat, None, [chat_window, chat_selector])
        
        self.demo = demo
    
    def _respond(self, user_input: str, history: list) -> Generator[list, None, None]:
        """Handle user input and stream response for Chatbot component"""
        try:
            # Convert history to proper format if needed
            if history is None:
                history = []
            
            # Add user message to history
            history = history + [[user_input, None]]
            yield history
            
            # Get bot response
            async def get_response():
                bot_response = ""
                async for partial in self.chat_handler.stream_answer_with_tools(user_input):
                    bot_response += partial
                    # Update the last message (bot response) in history
                    current_history = history[:-1] + [[user_input, bot_response]]
                    yield current_history
            
            # Use asyncio.run for simple execution
            async def collect_all():
                results = []
                async for chunk in get_response():
                    results.append(chunk)
                return results
            
            results = asyncio.run(collect_all())
            for result in results:
                yield result
                
        except Exception as e:
            error_history = history[:-1] + [[user_input, f"Error: {str(e)}"]]
            yield error_history
    
    def _select_chat(self, title: str) -> list:
        """Select an existing chat"""
        try:
            for chat in get_all_chats():
                if chat["title"] == title:
                    self.chat_handler.set_current_chat_id(chat["id"])
                    break
            return self._load_chat_history_as_list()
        except Exception as e:
            return [["System", f"Error loading chat: {str(e)}"]]
    
    def _new_chat(self) -> tuple:
        """Create a new chat"""
        try:
            self.chat_handler.create_new_chat()
            return [], gr.update(choices=self._get_chat_titles())
        except Exception as e:
            return [["System", f"Error creating chat: {str(e)}"]], gr.update(choices=[])
    
    def _load_chat_history(self) -> str:
        """Load chat history for current chat (legacy method)"""
        try:
            current_chat_id = self.chat_handler.get_current_chat_id()
            if current_chat_id:
                msgs = get_chat_messages(current_chat_id)
                formatted = ""
                for m in msgs:
                    role = "🧑 **You:**" if m["role"] == "user" else "🤖 **Bot:**"
                    formatted += f"{role} {m['content']}\n\n"
                return formatted
            return "No messages yet."
        except Exception as e:
            return f"Error loading chat history: {str(e)}"
    
    def _load_chat_history_as_list(self) -> list:
        """Load chat history as list for Chatbot component"""
        try:
            current_chat_id = self.chat_handler.get_current_chat_id()
            if current_chat_id:
                msgs = get_chat_messages(current_chat_id)
                history = []
                i = 0
                while i < len(msgs):
                    if msgs[i]["role"] == "user":
                        user_msg = msgs[i]["content"]
                        bot_msg = ""
                        # Look for corresponding bot message
                        if i + 1 < len(msgs) and msgs[i + 1]["role"] == "bot":
                            bot_msg = msgs[i + 1]["content"]
                            i += 2
                        else:
                            i += 1
                        history.append([user_msg, bot_msg])
                    else:
                        i += 1
                return history
            return []
        except Exception as e:
            return [["System", f"Error loading chat history: {str(e)}"]]
    
    def _get_chat_titles(self) -> list:
        """Get list of chat titles"""
        try:
            return [c["title"] for c in get_all_chats()]
        except Exception as e:
            print(f"Error getting chat titles: {e}")
            return []
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
        if self.demo is None:
            raise RuntimeError("Interface not initialized")
        
        self.demo.queue()
        return self.demo.launch(**kwargs)
    
    def get_demo(self):
        """Get the Gradio demo object"""
        return self.demo
