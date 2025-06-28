import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.models import Subscription
from app import SessionLocal

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    db = SessionLocal()

    # El usuario debe haber proporcionado su user_id al ejecutar: /start user123
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "🛡️ Para completar tu suscripción escribe:\n/start <tu_user_id>\n\n"
            "Ejemplo: /start user123"
        )
        db.close()
        return

    user_id = context.args[0]

    # Buscar suscripción pendiente asociada a ese user_id
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.telegram_pending == True
    ).first()

    if sub:
        sub.chat_id = chat_id
        sub.telegram_pending = False
        sub.is_active = True
        db.commit()

        await update.message.reply_text(
            "✅ ¡Tu suscripción ha sido activada con éxito!\n\n"
            "A partir de ahora recibirás reportes de inversión automáticamente aquí por Telegram. 📈"
        )
    else:
        await update.message.reply_text(
            "⚠️ No encontramos ninguna suscripción pendiente con ese ID.\n"
            "Asegúrate de haberte registrado antes en nuestra app."
        )

    db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Usa /start para suscribirte.\nUsa /reporte para recibir tu reporte de inversión al instante."
    )

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))


    print("[🚀] Bot de Telegram iniciado en modo polling")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.get_event_loop().run_until_complete(main())


