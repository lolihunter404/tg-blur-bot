import os
import io
import asyncio
from PIL import Image, ImageFilter
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Хранилище для альбомов (media groups)
media_groups = {}

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Если это альбом — собираем
    if message.media_group_id:
        group_id = message.media_group_id
        media_groups.setdefault(group_id, []).append(message)

        # ждём, пока придут все фото альбома
        await asyncio.sleep(1)

        if group_id in media_groups:
            messages = media_groups.pop(group_id)
            for msg in messages:
                await process_single_photo(msg)
    else:
        await process_single_photo(message)

async def process_single_photo(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    data = await bot.download_file(file.file_path)

    img = Image.open(io.BytesIO(data.read())).convert("RGB")
    blurred = img.filter(ImageFilter.GaussianBlur(radius=20))

    buf_blur = io.BytesIO()
    blurred.save(buf_blur, format="JPEG", quality=95)
    buf_blur.seek(0)

    buf_orig = io.BytesIO()
    img.save(buf_orig, format="JPEG", quality=95)
    buf_orig.seek(0)

    await message.answer_photo(buf_blur, caption="Blur")
    await message.answer_photo(buf_orig, caption="Original")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
