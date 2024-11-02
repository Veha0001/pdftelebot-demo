import os
from pdf2image import convert_from_path
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")


# Replace 'YOUR_BOT_TOKEN' with your actual bot token
if BOT_TOKEN is None:
    raise ValueError("No any bot TOKEN added.")
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hello! Send me a PDF file, and I’ll convert each page to PNG image.",
    )


@bot.message_handler(content_types=["document"])
def handle_document(message):
    if message.document.mime_type == "application/pdf":
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        original_file_name = (
            message.document.file_name
        )  # Use the original PDF file name

        # Download the PDF
        if file_path is None:
            raise ValueError("file_path cannot be None")
        downloaded_file = bot.download_file(file_path)
        pdf_file_name = f"{file_id}.pdf"
        with open(pdf_file_name, "wb") as pdf_file:
            pdf_file.write(downloaded_file)

        try:
            # Convert PDF to high-quality PNG images
            # No page limit, convert all pages
            pages = convert_from_path(pdf_file_name, dpi=200)
            for i, page in enumerate(pages):
                image_path = f"{original_file_name.split('.')[0]}_page_{
                    i + 1}.png"  # Retain original name

                # Save as PNG with high quality
                page.save(image_path, "PNG")  # PNG inherently has good quality

                # Notify the user that uploading is in progress
                bot.send_chat_action(message.chat.id, "upload_document")

                # Send each page as a PNG document
                with open(image_path, "rb") as image_file:
                    bot.send_document(
                        message.chat.id, image_file, visible_file_name=image_path
                    )

                # Remove the image file after sending
                os.remove(image_path)
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")
        finally:
            # Clean up the PDF file
            os.remove(pdf_file_name)


bot.polling()
