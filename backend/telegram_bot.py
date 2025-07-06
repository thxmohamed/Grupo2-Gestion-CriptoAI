import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.models import Subscription
from app import SessionLocal
import logging

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./criptoai.db")

logger.info(f"[🔧] Token configurado: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
logger.info(f"[🗄️] DATABASE_URL: {DATABASE_URL}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    logger.info(f"[📱] Comando /start recibido de chat_id: {chat_id}")
    
    db = SessionLocal()

    # El usuario debe haber proporcionado su user_id al ejecutar: /start user123
    if not context.args or len(context.args) != 1:
        logger.warning(f"[⚠️] Comando /start sin argumentos válidos desde chat_id: {chat_id}")
        await update.message.reply_text(
            "🛡️ Para completar tu suscripción escribe:\n/start <tu_user_id>\n\n"
            "Ejemplo: /start user123"
        )
        db.close()
        return

    user_id = context.args[0]
    logger.info(f"[🔍] Buscando suscripción para user_id: {user_id}")

    # Buscar suscripción pendiente asociada a ese user_id
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.telegram_pending == True
    ).first()

    if sub:
        logger.info(f"[✅] Suscripción encontrada para user_id: {user_id}, activando...")
        sub.chat_id = chat_id
        sub.telegram_pending = False
        sub.is_active = True
        db.commit()

        await update.message.reply_text(
            "✅ ¡Tu suscripción ha sido activada con éxito!\n\n"
            "A partir de ahora recibirás reportes de inversión automáticamente aquí por Telegram. 📈"
        )
        logger.info(f"[🎉] Suscripción activada exitosamente para user_id: {user_id}")
    else:
        logger.warning(f"[❌] No se encontró suscripción pendiente para user_id: {user_id}")
        await update.message.reply_text(
            "⚠️ No encontramos ninguna suscripción pendiente con ese ID.\n"
            "Asegúrate de haberte registrado antes en nuestra app."
        )

    db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"[❓] Comando /help recibido de chat_id: {chat_id}")
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="Usa /start para suscribirte.\nUsa /reporte para recibir tu reporte de inversión al instante."
    )
    logger.info(f"[📤] Mensaje de ayuda enviado a chat_id: {chat_id}")

async def main():
    logger.info("[🔧] Iniciando configuración del bot...")
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("[❌] TELEGRAM_BOT_TOKEN no está configurado")
        return
    
    try:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        logger.info("[✅] Bot de Telegram configurado exitosamente")

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        logger.info("[🔧] Handlers de comandos registrados: /start, /help")

        print("[🚀] Bot de Telegram iniciado en modo polling")
        logger.info("[🚀] Bot de Telegram iniciado en modo polling")
        await app.run_polling()
    except Exception as e:
        logger.error(f"[💥] Error al iniciar el bot: {e}")
        raise

if __name__ == "__main__":
    logger.info("[🏁] Iniciando aplicación Telegram Bot...")
    
    try:
        import nest_asyncio
        nest_asyncio.apply()
        logger.info("[🔧] nest_asyncio configurado")
    except ImportError:
        logger.warning("[⚠️] nest_asyncio no disponible, continuando sin él")

    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("[⏹️] Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"[💥] Error fatal: {e}")
        raise


