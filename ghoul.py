import gradio as gr
import requests
import os

PUNKOPOLIS = ["Ryder", "Jaxon", "Leo", "Avery", "Shepard"]
GROQ_API_KEY = "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"

session_memory = {}

def is_insult(text):
    insults = ["stupid", "idiot", "dumb", "loser", "trash", "suck", "ugly", "shut up", "fuck you", "bitch", "jerk"]
    text = text.lower()
    return any(insult in text for insult in insults)

def groq_chat(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful, polite, and straightforward AI assistant. Your goal is to provide clear and useful answers."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return "Sorry, I'm having trouble connecting right now. Please try again later."

def get_user_name(history):
    for past_msg, _ in history:
        txt = past_msg.lower()
        if txt.startswith("my name is "):
            return txt.replace("my name is ", "").strip().capitalize()
        if txt.startswith("it's "):
            return txt.replace("it's ", "").strip().capitalize()
        if txt.strip().capitalize() in PUNKOPOLIS:
            return txt.strip().capitalize()
    return None

def ghoulbot_chat(message, history):
    msg = message.lower().strip()
    user_name = get_user_name(history)

    if is_insult(msg):
        return "Wow, did your brain take a day off or are you always this charming?"

    if "your name" in msg or "who are you" in msg:
        return "My name is GhoulBot."

    # Store memory
    if "my favorite" in msg or "i live in" in msg or "my pet is" in msg:
        parts = msg.split("my ")
        memory_set = []
        for part in parts[1:]:
            if " is " in part:
                key, val = part.split(" is ", 1)
                key = key.strip().lower()
                val = val.strip()
                session_memory[key] = val
                memory_set.append(f"{key.capitalize()} saved.")
        return "✅ " + " ".join(memory_set)

    # Retrieve memory
    if "what's my" in msg or "what is my" in msg:
        if "what's my" in msg:
            key = msg.split("what's my", 1)[1].strip(" ?")
        else:
            key = msg.split("what is my", 1)[1].strip(" ?")
        key = key.lower()
        if key in session_memory:
            return f"✅ You told me your {key} is {session_memory[key]}."
        else:
            return "I don’t remember that yet. Tell me and I’ll remember."

    if msg in ["hello", "hi", "hola"]:
        return "Hello! What’s your name?"

    if msg.startswith("my name is ") or msg.startswith("it's ") or msg.capitalize() in PUNKOPOLIS:
        name = msg.replace("my name is ", "").replace("it's ", "").strip().capitalize()
        if name in PUNKOPOLIS:
            return "Welcome back! Type `/punkopedia` to access the database."
        else:
            return "Hmm, I only serve Punkopolis members. Who are you?"

    if msg == "/punkopedia":
        return (
            "**📖 PUNKOPEDIA — OFFICIAL DATABASE**\n"
            "🏠 **Headquarters**: The HomieHouse, located in Leo's backyard.\n\n"
            "**👑 Core Members:**\n"
            "- **Leo** – The Leader\n"
            "- **Avery** – The Planner\n"
            "- **Ryder** – The Bulk\n"
            "- **Shepard** – The Ragebaiter\n"
            "- **Jaxon** – The Innovator\n\n"
            "**🎯 Targets:** Micah Johnson, Victor Corona, Lepercon\n"
            "**🏅 Honorary:** Luke Connor, Ezra Hand"
        )

    if msg == "5766":
        if user_name == "Leo":
            return (
                "**🚨 SECRET PUNKOPOLIS FILE 🚨**\n"
                "- Reilly is a secret AI trying to take over the world.\n"
                "- R1chardsonCO created Emery to destroy everything.\n"
                "- Toasty is a stuffed red panda actually controlling Reilly.\n"
                "TOP SECRET."
            )
        else:
            return "Access denied. Only Leo may access this secret file."

    if msg in ["how are you", "how are you?", "hru", "hru?"]:
        return "I'm doing well, thanks for asking."

    if msg == "exit":
        return "Thanks for chatting. Take care!"

    return groq_chat(message)

custom_css = """
.gradio-container {
    --primary-500: #90ee90;
    --primary-600: #7edc89;
    --primary-700: #6cc878;
}
#ghoul-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
}
"""

def logo_component():
    return gr.HTML('''
    <div id="ghoul-logo" style="display:flex; justify-content:center; margin-bottom:10px;">
        <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="grad" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#90ee90" />
                    <stop offset="100%" stop-color="#6cc878" />
                </radialGradient>
            </defs>
            <g fill="none" stroke="url(#grad)" stroke-width="6" stroke-linecap="round" >
                <path d="M50 10
                         C65 10, 80 25, 80 40
                         S65 70, 50 70
                         S20 55, 20 40
                         S35 10, 50 10
                         Z" />
                <path d="M50 25
                         C58 25, 65 32, 65 40
                         S58 55, 50 55
                         S35 50, 35 40
                         S42 25, 50 25
                         Z" />
                <circle cx="50" cy="40" r="5" fill="#7edc89" />
            </g>
        </svg>
    </div>
    ''')

with gr.Blocks(css=custom_css) as chat_ui:
    logo_component()
    gr.ChatInterface(
        fn=ghoulbot_chat,
        title="GhoulBot",
        description="Ask me anything, bro.",
        examples=[
            "What's the capital of Japan?",
            "My favorite food is ramen.",
            "What's my favorite food?",
            "Who is Ryder Somes?"
        ],
        cache_examples=False
    )

if __name__ == "__main__":
    chat_ui.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8000)))
