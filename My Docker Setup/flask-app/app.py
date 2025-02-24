import os
import time

from redis import Redis
from flask import Flask


redis_port = os.getenv('redis_port') # in conjunction with the import OS line at the very top, it allows you to retrieve environment variables set in the system

app = Flask(__name__)
redis = Redis(host='redis', port=redis_port)

@app.route("/")
def home():
    html = """
<html>
<head>
    <title>Welcome to Juned's Counter Page</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
            color: #333;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: auto;
            text-align: center;
        }

        .container {
            background-color: #fff;
            padding: 40px 50px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 600px;
            margin: 20px auto;
        }

        h1 {
            color: #333;
            font-size: 36px;
            margin-bottom: 10px;
        }

        h3 {
            color: #555;
            font-size: 24px;
            margin-top: 0;
        }

        p {
            font-size: 16px;
            color: #666;
            line-height: 1.6;
            margin: 20px 0;
        }

        .button {
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            text-align: center;
            font-size: 18px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
            transition: background-color 0.3s ease;
        }

        .button:hover {
            background-color: #0056b3;
        }

        .linkedin-box {
            background-color: #f1f9fc;
            border: 1px solid #0077b5;
            padding: 30px;
            border-radius: 10px;
            margin-top: 40px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 80%;
            margin: 30px auto 20px auto;  /* Adjusted the margin to bring it closer */
        }

        .linkedin-box h4 {
            color: #0077b5;
            font-size: 24px;
            margin-bottom: 10px;
        }

        .linkedin-box p {
            color: #333;
            font-size: 16px;
            margin-bottom: 20px;
        }

        .linkedin-link {
            font-size: 18px;
            color: #0077b5;
            text-decoration: none;
            font-weight: bold;
        }

        .linkedin-link:hover {
            text-decoration: underline;
        }

    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Juned's Counter Page</h1>
        <h3>Hi there, Visitor!</h3>
        <p>Thanks for visiting! Click the button below to see the current visit count.</p>
        <p><em>"This page is being load balanced to ensure it's always available (well, at least 99.9% of the time)!"</em></p>
        <a class="button" href="/count">Go to Visit Count</a>
    </div>

    <!-- LinkedIn Reach Out Section -->
    <div class="linkedin-box">
        <h4>Let's Connect!</h4>
        <p>If you'd like to connect or if you have any questions, feel free to reach out!</p>
        <a href="https://www.linkedin.com/in/juned-connect" class="linkedin-link" target="_blank">Here's my Linkedin</a>
    </div>
</body>
</html>
    """
    return html

@app.route("/count")
def count():
    visits = redis.incr('counter')
    html = f"""
    <html>
    <head>
        <title>Visit Count</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4; }}
            h3 {{ color: #333; }}
            .button {{
                background-color: #008CBA; 
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                margin-top: 20px;
                cursor: pointer;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
            }}
            .button:hover {{ background-color: #005f75; }}
        </style>
    </head>
    <body>
        <h3>Visit Count</h3>
        <p>This page has been visited {visits} times.</p>
        <a class="button" href="/">Go Back</a>
    </body>
    </html>
    """
    return html




flask_port = os.getenv('flask_app_port') # in conjunction with the import OS line at the very top, it allows you to retrieve environment variables set in the system

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=flask_port)
