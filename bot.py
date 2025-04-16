import os
import openai
import base64
from io import BytesIO
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GRUPO_CHAT_ID = int(os.getenv("GRUPO_CHAT_ID"))  # Asegúrate de agregar esto en tu .env

openai.api_key = OPENAI_API_KEY

# Función principal para procesar la imagen
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{image_base64}"

    try:
        # Llamada a GPT-4o con un prompt detallado y formato estricto
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
Analiza cuidadosamente el contenido del ticket de retiro de efectivo y los billetes visibles en la imagen proporcionada. Extrae los datos con precisión y responde solo en el siguiente formato estandarizado y claro:

RETIRO DE EFECTIVO

- FECHA: (formato YYYY-MM-DD)
- HORA: (formato HH:MM:SS)
- ANFITRIÓN: (nombre completo visible o "No visible")
- PARCIAL NÚMERO: (número visible o "No visible")
- EFECTIVO MXN: (monto total extraído, ejemplo: $2000.00)
- BILLETES AGREGADOS:
  - BILLETES DE 500: (cantidad si es visible o "No visible")
  - BILLETES DE 1000: (cantidad si es visible o "No visible")
- NÚMEROS DE SERIE DETECTADOS:
  - (Escribe cada número de serie visible en los billetes, uno por línea. Si no hay ninguno legible, escribe "No visibles")

Asegúrate de ser exacto, sin explicaciones ni frases adicionales. No inventes datos. Si un campo no es claramente legible, indica "No visible".
"""},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]}
            ]
        )

        result = response.choices[0].message.content

        # Responder al usuario
        await update.message.reply_text("✅ Análisis procesado. Enviando al grupo...")

        # Enviar imagen original al grupo con análisis como caption
        await context.bot.send_photo(
            chat_id=GRUPO_CHAT_ID,
            photo=image_bytes,
            caption=result
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Inicialización y ejecución del bot de Telegram
if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
