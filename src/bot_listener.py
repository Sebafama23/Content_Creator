import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from src.publisher import LinkedInPublisher
from src.generator import LocalContentGenerator

class BotListener:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.publisher = LinkedInPublisher()
        self.generator = LocalContentGenerator()

    async def handle_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        
        if user_text.lower() == "confirmado":
            await update.message.reply_text("🚀 ¡Entendido! Publicando en LinkedIn...")
            # Aquí llamamos al publisher con el último archivo generado
            # ... lógica de publicación ...
        else:
            await update.message.reply_text(f"📝 Recibido. Re-generando con tus notas: {user_text}")
            # Aquí re-inyectamos al generator para la v2
            # ... lógica de re-generación ...

    def start(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        app.run_polling()