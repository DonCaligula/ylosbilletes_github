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
openai.api_key = OPENAI_API_KEY

# Función principal para procesar la imagen
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{image_base64}"

    try:
        # Llamada a GPT-4o con un prompt personalizado y formato fijo
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
Analiza el ticket de retiro de efectivo que te mostraré a continuación y responde **solo en este formato exacto**:

RETIRO DE EFECTIVO

- FECHA:
- HORA:
- ANFITRIÓN:
- PARCIAL NÚMERO:
- EFECTIVO MXN:
- BILLETES AGREGADOS:
  - BILLETES DE 500:
  - BILLETES DE 1000:

No incluyas ninguna explicación ni texto adicional. Si un dato no se encuentra visible, indícalo como \"No visible\".
"""},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]}
            ]
        )

        result = response.choices[0].message.content
        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Inicialización y ejecución del bot de Telegram
if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
