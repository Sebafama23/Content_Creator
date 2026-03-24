import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

from src.researcher import Researcher
from src.generator import LocalContentGenerator
from src.editor import ContentEditor
from src.publisher import LinkedInPublisher
from src.analyzer import VisionAnalyzer

load_dotenv()

class ContentFactoryOrchestrator:
    def __init__(self):
        self.researcher = Researcher()
        self.generator = LocalContentGenerator()
        self.editor = ContentEditor()
        self.publisher = LinkedInPublisher()
        self.analyzer = VisionAnalyzer()
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.current_trends = None
        self.last_version_path = None
        self.app = None
        self.active_flow = None  # Trackea qué flujo está corriendo

    # ─────────────────────────────────────────
    # COMANDOS — Entry points del bot
    # ─────────────────────────────────────────

    async def handle_texto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /command2 [tema]
        Busca tendencias sobre el tema y genera un post de texto.
        """
        topic = " ".join(context.args) if context.args else None
        if not topic:
            await update.message.reply_text(
                "⚠️ Indicá un tema. Ejemplo:\n/command2 automatización industrial con LLMs"
            )
            return

        self.active_flow = "texto"
        await update.message.reply_text(f"🔍 Investigando tendencias sobre: *{topic}*...", parse_mode="Markdown")

        try:
            df = self.researcher.fetch_trends(topic)
            self.current_trends = df.to_json(orient="records")

            await update.message.reply_text("✍️ Generando borrador...")
            draft = self.generator.generate_full_content(self.current_trends)
            await self.process_new_version(draft)

        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")
            self.active_flow = None
        except (ConnectionError, TimeoutError, RuntimeError) as e:
            await self._notify_error(f"🔴 Error en /command2:\n`{e}`")
            self.active_flow = None

    async def handle_tendencias(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /tendencias [tema]
        Igual que /texto pero el mensaje deja claro que arranca desde tendencias frescas.
        """
        # Por ahora mismo flujo que /texto — se puede diferenciar después
        await self.handle_texto(update, context)

    async def handle_analizar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /command1
        Pide al usuario que suba una foto para analizarla.
        """
        self.active_flow = "analizar"
        await update.message.reply_text("📸 Por favor, enviá la foto (como imagen normal) que querés analizar.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la recepción de fotos cuando hay un flujo activo de 'analizar'."""
        if self.active_flow != "analizar":
            await update.message.reply_text("ℹ️ Si querés analizar una foto, usa el comando /command1 primero.")
            return
            
        await update.message.reply_text("🧠 Recibiendo imagen... Preparando análisis de OCR y contexto (esto puede tardar varios minutos).")
        
        photo = update.message.photo[-1] # Obtiene la máxima resolución
        file = await context.bot.get_file(photo.file_id)
        
        import base64
        import datetime
        
        try:
            # Guardamos
            os.makedirs("files", exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"files/analisis_{timestamp}.jpg"
            
            await file.download_to_drive(filename)
            print(f"📸 Imagen guardada en: {filename}")
            
            with open(filename, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Paso 1: Analizar imagen (OCR y Contexto) con modelo de Visión
            await update.message.reply_text("🔍 Extrayendo información técnica con Qwen2.5...")
            image_context = self.analyzer.analyze_image(base64_image)
            
            # Guardamos el contexto como "tendencias" por si necesita refinar el texto luego
            self.current_trends = image_context 
            
            # Paso 2: Generar el borrador final del post con Gemma
            await update.message.reply_text("✍️ Redactando el borrador del post con Gemma...")
            draft = self.generator.generate_from_image_context(image_context)
            
            await self.process_new_version(draft)

        except Exception as e:
            await self._notify_error(f"🔴 Error al procesar imagen:\n`{e}`")
            self.active_flow = None

    async def handle_cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /command4
        Aborta el flujo activo y resetea el estado.
        """
        if not self.active_flow:
            await update.message.reply_text("ℹ️ No hay ningún flujo activo en este momento.")
            return

        self.active_flow = None
        self.current_trends = None
        self.last_version_path = None
        await update.message.reply_text(
            "🛑 Flujo cancelado. El agente queda en espera.\n"
            "Usá /command1, /command2 o /command3 para arrancar uno nuevo."
        )
        print("🛑 Flujo cancelado por el usuario.")

    async def handle_ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /ayuda
        Muestra los comandos disponibles.
        """
        await update.message.reply_text(
            "🤖 *Content Creator Agent*\n\n"
            "Comandos disponibles:\n\n"
            "/command1 — Envia una imagen para extraer contexto y crear post\n"
            "/command2 [tema] — Busca tendencias y genera un post\n"
            "/command3 [tema] — Genera una imagen _(próximamente)_\n"
            "/command4 — Aborta el flujo activo\n"
            "/ayuda — Muestra este mensaje",
            parse_mode="Markdown"
        )

    # ─────────────────────────────────────────
    # FLUJO DE REVISIÓN — Igual que antes
    # ─────────────────────────────────────────

    async def process_new_version(self, draft_text):
        clean_post = self.editor.clean_draft(draft_text)
        self.last_version_path, v = self.editor.save_versioned_post(clean_post)

        message = (
            f"📝 PROPUESTA v{v}\n\n"
            f"{clean_post}\n\n"
            "---\n"
            "✅ Respondé 'confirmado' para publicar.\n"
            "📝 O escribí tus correcciones para ajustar.\n"
            "🛑 O usá /cancelar para abortar."
        )
        await self.app.bot.send_message(chat_id=self.chat_id, text=message)
        print(f"📱 Versión {v} enviada. Esperando aprobación...")

    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja respuestas de texto libre durante un flujo activo."""

        # Si no hay flujo activo, ignorar mensajes de texto
        if not self.active_flow:
            await update.message.reply_text(
                "ℹ️ No hay un flujo activo. Usá /ayuda para ver los comandos disponibles."
            )
            return

        user_feedback = update.message.text

        if user_feedback.lower() == "confirmado":
            if not self.last_version_path or not os.path.exists(self.last_version_path):
                await update.message.reply_text("❌ No hay ningún post guardado para publicar.")
                return

            with open(self.last_version_path, "r", encoding="utf-8") as f:
                final_content = f.read()

            if final_content.startswith("Error") or len(final_content) < 50:
                await update.message.reply_text("❌ El post parece inválido. Reiniciá el flujo.")
                return

            await update.message.reply_text("🚀 Publicando en LinkedIn...")
            status, msg = self.publisher.publish(final_content)

            if status in [200, 201]:
                await update.message.reply_text("✅ ¡Post publicado con éxito!")
                print("🏁 Proceso finalizado exitosamente.")
            else:
                await update.message.reply_text(f"❌ Error al publicar: {status} - {msg}")

            self.active_flow = None

        else:
            await update.message.reply_text("🔄 Ajustando con tus comentarios...")
            try:
                with open(self.last_version_path, "r", encoding="utf-8") as f:
                    previous_post = f.read()

                new_draft = self.generator.refine_content(
                    previous_post, user_feedback, self.current_trends
                )
                await self.process_new_version(new_draft)

            except (ConnectionError, TimeoutError, RuntimeError) as e:
                await self._notify_error(f"🔴 Error al regenerar:\n`{e}`")

    async def _notify_error(self, message: str):
        print(f"❌ {message}")
        await self.app.bot.send_message(
            chat_id=self.chat_id,
            text=message
        )

    # ─────────────────────────────────────────
    # ARRANQUE
    # ─────────────────────────────────────────

    def run(self):
        self.app = Application.builder().token(self.token).build()

        # Comandos
        self.app.add_handler(CommandHandler("command2", self.handle_texto))
        self.app.add_handler(CommandHandler("command1", self.handle_analizar))
        self.app.add_handler(CommandHandler("command4", self.handle_cancelar))
        self.app.add_handler(CommandHandler("ayuda", self.handle_ayuda))

        # Foto — para flujo de analizar
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

        # Texto libre — solo activo durante un flujo
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback)
        )

        print("👂 Agente en espera. Mandá /ayuda para ver los comandos.")
        self.app.run_polling()


if __name__ == "__main__":
    print("🟢 Iniciando Content Factory...")
    factory = ContentFactoryOrchestrator()
    factory.run()


"""
Los cambios clave respecto al `main.py` anterior:

| Antes | Ahora |
|---|---|
| Arrancaba solo con `post_init` | Ocioso hasta que mandás un comando |
| Un solo flujo hardcodeado | Router con `/texto`, `/tendencias`, `/cancelar`, `/ayuda` |
| Sin tracking de estado | `self.active_flow` sabe qué está corriendo |
| Texto libre siempre activo | Texto libre solo responde si hay flujo activo |

Acordate de registrar los comandos nuevos en BotFather:
```
texto - Busca tendencias y genera un post
tendencias - Busca tendencias sobre un tema
cancelar - Aborta el flujo activo
ayuda - Muestra los comandos disponibles
"""