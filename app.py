from flask import Flask
import threading
import time
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

# Отдельная функция для запуска бота
def run_bot():
    try:
        logger.info("Пытаюсь запустить бота...")
        # ИМПОРТ ВНУТРИ ФУНКЦИИ — это важно!
        from tg_bot import main
        main()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Даём небольшую задержку перед запуском бота
    time.sleep(2)
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Flask сервер запускается...")
    app.run(host='0.0.0.0', port=10000)
