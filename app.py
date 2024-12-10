from flask import Flask, request, render_template_string, redirect, url_for, flash
import time
from instagram_private_api import Client, ClientError
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Instagram Login Function
def login_instagram(username, password):
    try:
        api = Client(username, password)
        return api
    except ClientError as e:
        print(f"[ERROR] Instagram Login Failed: {e.msg}")
        return None

# Fetch Group Chats
def fetch_group_chats(api):
    try:
        inbox = api.direct_v2_inbox()
        group_threads = [
            {"name": thread["thread_title"], "thread_id": thread["thread_id"]}
            for thread in inbox["inbox"]["threads"] if thread["thread_type"] == "group"
        ]
        return group_threads
    except Exception as e:
        print(f"[ERROR] Unable to fetch group chats: {e}")
        return []

# Send Messages to Group
def send_messages(api, thread_id, messages, delay):
    for message in messages:
        try:
            api.direct_v2_message(text=message, thread_ids=[thread_id])
            print(f"[SUCCESS] Message sent: {message}")
            time.sleep(delay)
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            delay = int(request.form["delay"])
            thread_id = request.form["thread_id"]
            message_file = request.files["message_file"]

            # Read messages from file
            messages = message_file.read().decode("utf-8").splitlines()
            if not messages:
                flash("Message file is empty!", "error")
                return redirect(url_for("home"))

            # Login to Instagram
            api = login_instagram(username, password)
            if not api:
                flash("Instagram login failed!", "error")
                return redirect(url_for("home"))

            # Send messages to the selected group
            send_messages(api, thread_id, messages, delay)
            flash("Messages sent successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
        return redirect(url_for("home"))

    return render_template_string(HTML_TEMPLATE)

# HTML Template with Background Wallpaper
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Chat Automation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-image: url('https://i.ibb.co/fFqG2rr/Picsart-24-07-11-17-16-03-306.jpg');
            background-size: cover;
            color: #fff;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 10px;
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #ff69b4;
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin: 10px 0 5px;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        input:focus, button:focus {
            outline: none;
            border-color: #ff69b4;
        }
        button {
            background-color: #ff69b4;
            color: #fff;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #e60073;
        }
        .message {
            color: red;
            font-size: 14px;
            text-align: center;
        }
        .success {
            color: green;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Chat Automation</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID" required>

            <label for="message_file">Message File:</label>
            <input type="file" id="message_file" name="message_file" accept=".txt" required>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
