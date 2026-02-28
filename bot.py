import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from video_converter import convert_to_video_note_async

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start", "help"))
async def send_welcome(message: Message):
    await message.reply(
        "Salut! Trimite-mi un videoclip și eu îl voi converti într-un mesaj video rotund (Video Note).\n"
        "Asigură-te că videoclipul nu este foarte lung."
    )

@dp.message(F.video | F.document)
async def handle_video(message: Message):
    # Check if document is actually a video
    video = message.video
    if not video and message.document and message.document.mime_type and message.document.mime_type.startswith('video/'):
        video = message.document

    if not video:
        # Ignore other documents without sending an error, as those are just normal messages
        return
        
    processing_msg = await message.reply("⏳ Procesez videoclipul...")
    
    # Download the video file
    file_id = video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    
    input_file_name = f"downloaded_{file_id}.mp4"
    
    try:
        await bot.download_file(file_path, input_file_name)
        
        # Convert the video
        output_file_name = await convert_to_video_note_async(input_file_name)
        
        # Send as video note
        video_note = FSInputFile(output_file_name)
        await message.reply_video_note(video_note)
        
        # Clean up output file
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await message.reply("❌ A apărut o eroare la procesarea videoclipului.")
    finally:
        # Clean up input file
        if os.path.exists(input_file_name):
            os.remove(input_file_name)
            
        # Try to delete the processing message to clean up chat
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except Exception as e:
            logger.warning(f"Could not delete processing message: {e}")

async def main():
    logger.info("Starting up Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
