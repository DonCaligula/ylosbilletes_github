import os
import openai
import base64
from io import BytesIO
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Carga variables del archivo .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{image_base64}"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extrae los datos clave de este ticket de retiro de efectivo."},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_data_url}}]}
            ]
        )
        result = response.choices[0].message.content
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
