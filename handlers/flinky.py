import json
import subprocess
import threading
import datetime
import tempfile

def create_user_input_file():
    with tempfile.NamedTemporaryFile(
        prefix='user_input_',
        suffix='.json',
        mode='w',
        delete=False
    ) as tmp:
        json.dump({}, tmp)
        return tmp.name
    
import datetime
import json

def get_requests(file_path, since=0):
    print('Reading logs from line', since)
    requests = []

    try:
        with open(file_path, "r") as f:
            for i, line in enumerate(f):
                if i < since:
                    continue  # Skip lines before 'since'

                try:
                    entry = json.loads(line)
                    dt = datetime.datetime.fromtimestamp(int(entry.get("time", 0)))
                    request = {
                        "time": dt.strftime("%B %d, %Y @%H:%M:%S"),
                        "sender": entry.get("sender", ""),
                        "input": entry.get("input", ""),
                        "output": entry.get("output", "")
                    }
                    requests.append(request)
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed line: {e}")
    except FileNotFoundError as e:
        print(f"Log file not found: {e}")

    return requests


def append_request(file_path, time, sender, input_text, output_text):
    log_entry = {
        "time": time,       # Unix timestamp
        "sender": sender,
        "input": input_text,
        "output": output_text
    }

    with open(file_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    

def invoke_flinky(user_input, phone_number):
    # make json of input
    data = {"userInput": user_input, "phone": [phone_number]}
    json_path = create_user_input_file()
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    # Fire the script
    print(f"DEBUG → calling orchestrator.sh with: {json_path!r}")

    try:
        subprocess.run(["bash", "../orchestrator.sh", json_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{threading.get_ident()}] Script error: {e}")

