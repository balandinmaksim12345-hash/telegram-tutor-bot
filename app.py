from flask import Flask
import threading
import asyncio
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

# ===== ЗАПУСК БОТА =====
def run_bot():
    try:
        logger.info("Функция run_bot вызвана! Начинаю импорт...")
        from tg_bot import main
        logger.info("Импорт прошел успешно. Запускаю main()...")
        
        # СОЗДАЁМ НОВЫЙ ЦИКЛ СОБЫТИЙ ДЛЯ ПОТОКА
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        logger.info("main() завершила работу.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

# ===== ЗАПУСК БОТА ПРИ СТАРТЕ GUNICORN =====
logger.info("Инициализация бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("Бот запущен в фоновом потоке")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
