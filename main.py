import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

from src.researcher import Researcher
from src.generator import LocalContentGenerator
from src.editor import ContentEditor
from src.publisher import LinkedInPublisher

load_dotenv()

class ContentFactoryOrchestrator:
    def __init__(self):
        self.researcher = Researcher()
        self.generator = LocalContentGenerator()
        self.editor = ContentEditor()
        self.publisher = LinkedInPublisher()
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.current_trends = None
        self.last_version_path = None
        self.app = None

    async def _on_startup(self, app: Application):
        print("🚀 Bot iniciado. Arrancando flujo...")
        await self.start_flow()

    async def start_flow(self):
        try:
            print("🔍 Paso 1: Investigando tendencias...")
            df = self.researcher.fetch_trends()
            self.current_trends = df.to_json(orient="records")

            print("✍️ Paso 2: Generando Borrador v1...")
            draft = self.generator.generate_full_content(self.current_trends)
            await self.process_new_version(draft)

        except (ConnectionError, TimeoutError, RuntimeError) as e:
            await self._notify_error(f"🔴 *Error en generación inicial:*\n`{e}`")

    async def process_new_version(self, draft_text):
        clean_post = self.editor.clean_draft(draft_text)
        self.last_version_path, v = self.editor.save_versioned_post(clean_post)

        message = (
            f"📝 PROPUESTA v{v}\n\n"
            f"{clean_post}\n\n"
            "---\n"
            "✅ Respondé 'confirmado' para publicar.\n"
            "📝 O escribí tus correcciones para ajustar."
        )
        await self.app.bot.send_message(
            chat_id=self.chat_id,
            text=message
            # ✅ Sin parse_mode — Telegram recibe texto plano sin interpretar nada
        )
        print(f"📱 Versión {v} enviada a Telegram. Esperando aprobación...")

    async def handle_telegram_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_feedback = update.message.text

        if user_feedback.lower() == "confirmado":
            if not self.last_version_path or not os.path.exists(self.last_version_path):
                await update.message.reply_text("❌ No hay ningún post guardado para publicar.")
                return

            await update.message.reply_text("🚀 ¡Recibido! Publicando en LinkedIn...")
            with open(self.last_version_path, "r", encoding="utf-8") as f:
                final_content = f.read()

            if final_content.startswith("Error") or len(final_content) < 50:
                await update.message.reply_text("❌ El post guardado parece inválido. Reiniciá el flujo.")
                return

            status, msg = self.publisher.publish(final_content)
            if status in [200, 201]:
                await update.message.reply_text("✅ ¡Post publicado con éxito!")
                print("🏁 Proceso finalizado exitosamente.")
            else:
                await update.message.reply_text(f"❌ Error al publicar: {status} - {msg}")

        else:
            await update.message.reply_text("🔄 Ajustando el post con tus comentarios...")
            try:
                with open(self.last_version_path, "r", encoding="utf-8") as f:
                    previous_post = f.read()

                refinement_prompt = (
                    f"Basándote en este post anterior:\n{previous_post}\n\n"
                    f"Aplicá las siguientes correcciones: {user_feedback}\n\n"
                    f"Mantené el contexto de estas tendencias: {self.current_trends}"
                )
                new_draft = self.generator.refine_content(previous_post, user_feedback, self.current_trends)
                await self.process_new_version(new_draft)

            except (ConnectionError, TimeoutError, RuntimeError) as e:
                await self._notify_error(f"🔴 *Error al regenerar:*\n`{e}`")

    async def _notify_error(self, message: str):
        print(f"❌ {message}")
        await self.app.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="Markdown"
        )

    # ✅ AGREGÁ ESTO
    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.current_trends = None
        self.last_version_path = None
        await update.message.reply_text(
            "🛑 Operación cancelada.\n"
            "El flujo fue detenido. Reiniciá el contenedor cuando quieras comenzar de nuevo."
        )
        print("🛑 Operación cancelada por el usuario vía Telegram.")

    def run(self):
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_telegram_response)
        )
        # ✅ Nuevo: comando /cancelar
        self.app.add_handler(
            CommandHandler("cancelar", self.handle_cancel)
        )
        self.app.post_init = self._on_startup
        print("👂 Sistema operativo y escuchando...")
        self.app.run_polling()


if __name__ == "__main__":
    print("🟢 Iniciando Content Factory...")
    factory = ContentFactoryOrchestrator()
    print("🟢 Orquestador creado. Llamando a run()...")
    factory.run()