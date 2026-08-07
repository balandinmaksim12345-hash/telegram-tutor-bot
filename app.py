from flask import Flask
import logging
import os
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ===== ЗАПУСКАЕМ БОТА СРАЗУ ПРИ ИМПОРТЕ =====
logger.info("Запуск бота...")
from tg_bot import main
main()
# ===========================================
