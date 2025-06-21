from flask import request, Response
from handlers.flinky import append_request
import time
import subprocess
import datetime
import html

def webhook_parser(data, logs, is_github):
    if is_github:
        # GitHub webhook logic
        if data.get("ref") == "refs/heads/main":
            subprocess.Popen(["./deploy.sh"])
            return '', 200
        else:
            return '', 400  # Unexpected JSON
    else:
        # Twilio SMS webhook logic
        sender = data.get("From", "").strip()
        body = data.get("Body", "").strip()

        if sender and body:
            print(sender)
            print(body)
            timestamp = int(time.time())

            dt = datetime.datetime.fromtimestamp(timestamp)
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            result = "dummy"  # Replace with real logic

            append_request('logs.jsonl', timestamp, sender, body, result.strip())

            logs.append({
                "time": timestamp,
                "sender": sender,
                "input": body,
                "output": result.strip()
            })

            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                <Response>
                    <Message>{html.escape(result.strip())}</Message>
                </Response>"""

            return Response(response_xml, status=200, mimetype="application/xml")

        return '', 400  # Malformed Twilio form data
