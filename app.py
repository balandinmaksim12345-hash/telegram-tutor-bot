from flask import Flask
import threading
import asyncio
import logging

# Настраиваем логирование СРАЗУ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

# ===== ОДНА ПРАВИЛЬНАЯ ФУНКЦИЯ run_bot =====
def run_bot():
    try:
        logger.info("Функция run_bot вызвана! Начинаю импорт...")
        from tg_bot import main
        logger.info("Импорт прошел успешно. Запускаю main()...")
        asyncio.run(main())
        logger.info("main() завершила работу.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

# ===== ЗАПУСК =====
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Flask сервер запускается...")
    app.run(host='0.0.0.0', port=10000)
