from flask import Flask
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

# ЗАПУСКАЕМ БОТА ПРЯМО ЗДЕСЬ (в главном потоке)
logger.info("Запуск бота...")
from tg_bot import main
main()
