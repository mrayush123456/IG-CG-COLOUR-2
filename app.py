from flask import Flask, request, render_template_string, flash, redirect, url_for
import time
from instagram_private_api import Client, ClientError  # Install with pip install instagram-private-api

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# HTML Template with UI customization
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Chat Messenger</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-image: url('https://i.ibb.co/fFqG2rr/Picsart-24-07-11-17-16-03-306.jpg');
            background-size: cover;
            background-position: center;
            margin: 0;
            padding: 0;
            color: #ffffff;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4);
            max-width: 500px;
            margin: 50px auto;
        }
        h1 {
            text-align: center;
            color: #ff69b4;
        }
        label {
            display: block;
            margin: 10px 0 5px;
            font-weight: bold;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        input[type="text"], input[type="password"], input[type="file"], input[type="number"] {
            background-color: #222;
            color: #fff;
        }
        input:focus {
            outline: none;
            border: 1px solid #ff69b4;
        }
        button {
            background-color: #ff69b4;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #ff85c1;
        }
        .message {
            color: red;
            text-align: center;
        }
        .success {
            color: green;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Messenger</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter Group Thread ID" required>

            <label for="message_file">Upload Message File:</label>
            <input type="file" id="message_file" name="message_file" accept=".txt" required>

            <label for="delay">Delay Between Messages (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Function to log in to Instagram
def instagram_login(username, password):
    try:
        api = Client(username, password)
        print("[SUCCESS] Logged in to Instagram!")
        return api
    except ClientError as e:
        print(f"[ERROR] Login failed: {e.msg}")
        return None

# Function to send messages to a group
def send_messages(api, thread_id, messages, delay):
    for message in messages:
        try:
            print(f"[INFO] Sending message to thread {thread_id}: {message}")
            api.direct_v2_message(text=message, thread_ids=[thread_id])
            print("[SUCCESS] Message sent!")
            time.sleep(delay)
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")

# Main route to render the form and handle submissions
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Collect form data
        username = request.form.get("username")
        password = request.form.get("password")
        thread_id = request.form.get("thread_id")
        delay = int(request.form.get("delay"))
        message_file = request.files["message_file"]

        # Read messages from the uploaded file
        messages = message_file.read().decode("utf-8").splitlines()
        if not messages:
            flash("The message file is empty!", "message")
            return redirect(url_for("home"))

        # Log in to Instagram
        api = instagram_login(username, password)
        if not api:
            flash("Login failed. Please check your credentials.", "message")
            return redirect(url_for("home"))

        # Send messages to the group
        try:
            send_messages(api, thread_id, messages, delay)
            flash("All messages sent successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "message")
        return redirect(url_for("home"))

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
