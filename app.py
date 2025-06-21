from flask import Flask, request, render_template, jsonify
from handlers.flinky import get_requests
from webhook_listener import webhook_parser

app = Flask(__name__, static_folder="static", static_url_path="/static")
logs = []

@app.route("/")
def home():
    # read in previous queries from logs
    logs = get_requests('logs.jsonl')
    return render_template("home.html", logs=logs)

@app.route("/webhook", methods=["POST"])
def webhook():
    # from GitHub
    if request.is_json:
        return webhook_parser(request.get_json(), logs, is_github=True)
    # from Twillio
    else:
        return webhook_parser(request.form, logs, is_github=False)


@app.route("/logs.jsonl")
def get_logs_json():
    since = int(request.args.get("since", 0))
    logs = get_requests("logs.jsonl")
    return jsonify(logs[since:])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
