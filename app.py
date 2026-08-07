import os
import threading
from flask import Flask
from tg_bot import main

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    main()

if __name__ == "__main__":
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))