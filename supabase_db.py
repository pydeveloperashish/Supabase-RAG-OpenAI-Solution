from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uuid

# ✅ Load .env variables
load_dotenv()

# ✅ Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ✅ Create a new chat session
def create_chat(title="New Chat"):
    response = supabase.table("chats").insert({"title": title}).execute()
    return response.data[0]["id"]

# ✅ Insert a message into chat_messages
def add_message(chat_id, role, content):
    supabase.table("chat_messages").insert({
        "chat_id": chat_id,
        "role": role,
        "content": content
    }).execute()

# ✅ Fetch all chats (for sidebar)
def get_all_chats():
    response = supabase.table("chats").select("*").order("created_at").execute()
    return response.data

# ✅ Fetch all messages for a given chat
def get_chat_messages(chat_id):
    response = supabase.table("chat_messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
    return response.data

# ✅ New: Update chat title
def update_chat_title(chat_id, new_title):
    supabase.table("chats").update({"title": new_title}).eq("id", chat_id).execute()


# ✅ Example Usage
if __name__ == "__main__":
    # 1. Create a new chat
    chat_id = create_chat("LSTM Basics")
    print("New Chat ID:", chat_id)

    # 2. Add messages
    add_message(chat_id, "user", "What is LSTM?")
    add_message(chat_id, "bot", "LSTM is a type of RNN that handles long-term dependencies.")

    # 3. Fetch chats
    chats = get_all_chats()
    print("Chats:", chats)

    # 4. Fetch messages for this chat
    messages = get_chat_messages(chat_id)
    for m in messages:
        print(f"{m['role']}: {m['content']}")
