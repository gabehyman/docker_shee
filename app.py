from flask import Flask, request, render_template_string
import subprocess
import threading
import datetime
import html

app = Flask(__name__)
logs = []  # This will store all messages and outputs

@app.route("/")
def home():
    html_page = """
    <h1>📬 Message Log</h1>
    {% for log in logs %}
        <div style="padding:10px; border-bottom:1px solid #ccc;">
            <code>({{ log['time'] }}) {{ log['from'] }}: {{ log['input'] }} → {{ log['output'] }}</code>
        </div>
    {% else %}
        <p>No messages yet.</p>
    {% endfor %}
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
