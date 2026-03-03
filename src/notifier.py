import os
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

class TelegramApprover:
    def __init__(self):
        self.token = os.getenv("8519510123:AAE4Cmf5NNCPcB9NFmnyTD7BvfqJ5AWz_KU")
        self.chat_id = os.getenv("6438159817")
        self.last_post_path = None

    async def send_for_approval(self, file_path):
        """Envía el post al capitán Morgan para su revisión."""
        self.last_post_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        message = f"📢 *NUEVA PROPUESTA DE POST*\nArchivo: `{os.path.basename(file_path)}`\n\n---\n\n{content}\n\n---\nResponde con:\n✅ `/confirmar` para publicar\n📝 Escribe cualquier corrección para re-generar."
        
        bot = Bot(token=self.token)
        await bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')

# Esta lógica se integrará en el main.py para manejar la respuesta