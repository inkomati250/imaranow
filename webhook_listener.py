import os
from flask import Flask, request
import subprocess
import hmac
import hashlib
from dotenv import load_dotenv

# Load .env
load_dotenv('/var/www/imaranow/.env')
SECRET = os.getenv("WEBHOOK_SECRET").encode()

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    header_signature = request.headers.get('X-Hub-Signature-256')
    if header_signature is None:
        return "No signature provided", 403

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha256':
        return "Unsupported hash", 501

    mac = hmac.new(SECRET, msg=request.data, digestmod=hashlib.sha256)

    if not hmac.compare_digest(mac.hexdigest(), signature):
        return "Invalid signature", 403

    subprocess.Popen(["/var/www/imaranow/deploy.sh"])
    return "Deploy triggered", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
