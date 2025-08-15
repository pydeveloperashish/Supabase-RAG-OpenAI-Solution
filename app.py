import gradio as gr
import os
import re
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase_db import create_chat, add_message, get_chat_messages, get_all_chats, update_chat_title, supabase
from dotenv import load_dotenv

# ✅ Load .env variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ LangChain Components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = SupabaseVectorStore(client=supabase, table_name="chunks", query_name="match_chunks", embedding=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff", return_source_documents=True)

# ✅ Global State
current_chat_id = None

# ✅ Streaming Answer Generator
async def stream_answer(user_msg):
    global current_chat_id
    if current_chat_id is None:
        current_chat_id = create_chat("New Chat")

    add_message(current_chat_id, "user", user_msg)
    yield f"🧑 **You:** {user_msg}\n\n🤖 **Bot:** "

    async for chunk in qa_chain.astream({"query": user_msg}):
        token = chunk.get("result", "")
        if token:
            yield token

    # Final Answer + Save
    final = await qa_chain.acall({"query": user_msg})
    answer = final["result"]
    add_message(current_chat_id, "bot", answer)

    # Sources Inline
    sources = [doc.metadata.get("source") for doc in final["source_documents"] if doc.metadata.get("source")]
    if sources:
        answer += f"\n\n_Source: {', '.join(set(sources))}_"

    # Auto-generate chat title on first query
    short_title = " ".join(re.findall(r"\w+", user_msg)[:4])
    update_chat_title(current_chat_id, short_title)

    yield answer

# ✅ Load Chat History
def load_chat_history():
    if current_chat_id:
        msgs = get_chat_messages(current_chat_id)
        formatted = ""
        for m in msgs:
            role = "🧑 **You:**" if m["role"] == "user" else "🤖 **Bot:**"
            formatted += f"{role} {m['content']}\n\n"
        return formatted
    return "No messages yet."

# ✅ Get Chat Titles
def get_chat_titles():
    return [c["title"] for c in get_all_chats()]

# ✅ Select Existing Chat
def select_chat(title):
    global current_chat_id
    for c in get_all_chats():
        if c["title"] == title:
            current_chat_id = c["id"]
            break
    return load_chat_history()

# ✅ Create New Chat
def new_chat():
    global current_chat_id
    current_chat_id = create_chat("New Chat")
    return "", gr.update(choices=get_chat_titles())

# ✅ Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🤖 Chatbot (Supabase + OpenAI)")

    with gr.Row():
        with gr.Column(scale=3):
            chat_window = gr.Textbox(value="", label="Chat", lines=22)
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Chat History")
            chat_selector = gr.Dropdown(choices=get_chat_titles(), label="Chats", interactive=True)
            new_btn = gr.Button("➕ New Chat")

    query_box = gr.Textbox(label="Your Question", placeholder="Type your question...")

    # ✅ Respond Function with Streaming
    async def respond(user_input, history):
        history = load_chat_history() + f"🧑 **You:** {user_input}\n\n🤖 **Bot:** "
        async for partial in stream_answer(user_input):
            yield history + partial

    # ✅ Events
    query_box.submit(respond, [query_box, chat_window], chat_window)
    chat_selector.change(select_chat, chat_selector, chat_window)
    new_btn.click(new_chat, None, [chat_window, chat_selector])

demo.queue()
demo.launch()
