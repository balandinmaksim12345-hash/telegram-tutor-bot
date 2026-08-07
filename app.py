from flask import Flask
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    try:
        logger.info("Функция run_bot вызвана! Начинаю импорт...")
        from tg_bot import main
        logger.info("Импорт прошел успешно. Запускаю main()...")
        main()
        logger.info("main() завершила работу.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

logger.info("Инициализация бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("Бот запущен в фоновом потоке")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
