from flask import Flask
from tg_bot import main
import threading

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

# Запускаем бота в отдельном потоке, чтобы Flask мог работать
def start_bot():
    main()

if __name__ == "__main__":
    # Запускаем бота в фоне
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    # Запускаем Flask
    app.run(host='0.0.0.0', port=10000)
