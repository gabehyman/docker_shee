from flask import Flask, request, render_template_string, jsonify
import subprocess
import threading
import datetime
import html

app = Flask(__name__, static_folder="static", static_url_path="/static")
logs = []  # this will store all shee

@app.route("/")
def home():
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>📽️ content requests</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            html, body {
                height: 100%;
                font-family: "Segoe UI", sans-serif;
                overflow-x: hidden;
                position: relative;
                background: transparent;
            }
            .bg-wrapper {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                overflow: hidden;
            }
            .bg-video {
                width: 100%;
                height: 100%;
                object-fit: cover;
                filter: brightness(40%);
                pointer-events: none;
            }
            .container {
                position: relative;
                z-index: 1;
                padding: 40px;
                max-width: 900px;
                margin: auto;
            }
            h1 {
                font-size: 5rem;
                text-align: center;
                margin-bottom: 30px;
                color: white;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
            }
            p {
                font-size: 1.6rem;
                color: white;
                text-align: center;
                margin-top: 50px;
                text-shadow: 0 1px 8px rgba(0, 0, 0, 0.7);
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
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="bg-wrapper">
            <video autoplay muted loop playsinline preload="auto" class="bg-video">
                <source src="{{ url_for('static', filename='popcorn.mp4') }}" type="video/mp4">
            </video>
        </div>
        <div class="container">
            <h1>🎬 content requests</h1>
            <div id="log-container">
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
        </div>
        <script>
            let lastLogCount = {{ logs|length }};

            function fetchLogs() {
                fetch("/logs.json")
                    .then(res => res.json())
                    .then(data => {
                        if (data.length > lastLogCount) {
                            const newLogs = data.slice(lastLogCount);
                            const container = document.getElementById("log-container");

                            newLogs.forEach(log => {
                                const div = document.createElement("div");
                                div.className = "log-card";
                                div.innerHTML = `
                                    <strong>(${log.time})</strong><br>
                                    <span><strong>${log.from}</strong>: ${log.input}</span><br>
                                    <span>→ <code>${log.output}</code></span>
                                `;
                                container.appendChild(div);
                            });

                            lastLogCount = data.length;
                        }
                    });
            }

            setInterval(fetchLogs, 5000); // check every 5 seconds
        </script>
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
    timestamp = datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")

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

@app.route("/logs.json")
def get_logs_json():
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
