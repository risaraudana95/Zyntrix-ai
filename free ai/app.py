from flask import Flask, request, render_template
from openai import OpenAI
import requests

app = Flask(__name__)

client = OpenAI(
    api_key="",
    base_url="https://api.groq.com/openai/v1"
)

SERPER_API_KEY = "3c2605613a47c4fc49e2d2f29d5484f4ba0a9cf4"

memory = []

def ai_chat(msg):
    global memory

    # Save the user's message
    memory.append({
        "role": "user",
        "content": msg
    })

    # Keep only the last 20 messages
    if len(memory) > 20:
        memory = memory[-20:]

    try:
        response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": (
                "You are Zyntrix AI, a helpful, intelligent, and friendly AI assistant. "
                "You were developed by Risara Udana. "
                "If anyone asks who made you, who created you, who developed you, "
                "or who is your developer, always answer: "
                "'I was developed by Risara Udana.' "
                "You use an AI language model to generate responses, but the Zyntrix AI application was developed by Risara Udana. "
                "Remember information the user tells you during the current conversation and use it to answer future questions."
            )
        }
    ] + memory
)

        answer = response.choices[0].message.content

        # Save the AI's reply
        memory.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        return f"AI Error: {e}"

def web_search(query):
    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        r = requests.post(url, json={"q": query}, headers=headers)
        data = r.json()

        if "organic" not in data:
            return "No results found."

        result = ""
        for item in data["organic"][:5]:
            result += f"<b>{item['title']}</b><br>{item['link']}<br><br>"

        return result
    except:
        return "Search error"

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    answer = ""
    typing = False

    if request.method == "POST":
        msg = request.form["message"]
        action = request.form.get("action")

        typing = True

        if action == "search":
            answer = web_search(msg)
        else:
            answer = ai_chat(msg)

    return render_template("index.html", msg=msg, answer=answer, typing=typing)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
