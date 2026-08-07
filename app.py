from flask import Flask
import threading
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    try:
        logger.info("Запуск бота...")
        from tg_bot import main
        main()
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")
        import traceback
        traceback.print_exc()

# Запускаем бота в фоновом потоке
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Flask-сервер запускается в основном потоке
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
