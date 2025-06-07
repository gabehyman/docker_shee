from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def home():
    fact = requests.get("https://catfact.ninja/fact").json()["fact"]
    return f"<h1>Random Cat Fact</h1><p>{fact}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
