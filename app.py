from flask import Flask, request, render_template_string
import subprocess
import threading
import datetime
import html

app = Flask(__name__, static_folder="static", static_url_path="/static")
logs = []  # This will store all messages and outputs

@app.route("/")
def home():
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>📽️ SMS Log</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                font-family: "Segoe UI", sans-serif;
                color: white;
                overflow: auto;
                background-color: black;
            }
            .bg-video {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                object-fit: cover;
                z-index: -100;
                filter: brightness(40%);
                pointer-events: none;
            }
            .container {
                position: relative;
                padding: 40px;
                max-width: 900px;
                margin: auto;
            }
            h1 {
                font-size: 3rem;
                text-align: center;
                margin-bottom: 30px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
            }
            .log-card {
                background: rgba(0, 0, 0, 0.6);
                border-left: 4px solid #FFD700;
                padding: 15px 20px;
                margin-bottom: 15px;
                border-radius: 6px;
                font-size: 1.1rem;
                line-height: 1.5;
                white-space: pre-wrap;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            }
        </style>
    </head>
    <body>
        <video autoplay muted loop playsinline preload="auto" class="bg-video">
            <source src="{{ url_for('static', filename='popcorn.mp4') }}" type="video/mp4">
        </video>
        <div class="container">
            <h1>🎬 content requests</h1>
            {% for log in logs %}
                <div class="log-card">
                    <strong>({{ log['time'] }})</strong><br>
                    <span><strong>{{ log['from'] }}</strong>: {{ log['input'] }}</span><br>
                    <span>→ <code>{{ log['output'] }}</code></span>
                </div>
            {% else %}
                <p>no requests yet.</p>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_page, logs=logs)


def handle_task(user_input, phone_number):
    try:
        subprocess.run(["bash", "../orchestrator.sh", json_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{threading.get_ident()}] Script error: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.form.get("From", "").strip()
    body = request.form.get("Body", "").strip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # try:
    #     result = threading.Thread(
    #     target=handle_task,
    #     args=(user_input, phone_number),
    #     daemon=True
    # ).start()  # can/does the thread return the output? dont think so
    # except subprocess.CalledProcessError as e:
    #     result = f"[ERROR] {e.output.strip()}"

    result = "dummy"

    # Append log entry
    logs.append({
        "time": timestamp,
        "from": from_number,
        "input": body,
        "output": result.strip()
    })

    # Twilio expects an XML response
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{html.escape(result.strip())}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
