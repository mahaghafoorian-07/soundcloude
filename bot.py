import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import yt_dlp

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = "8247667091:AAHTYTD5OMEa2Hkvr4825enY7dudv7txm60"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_name = update.effective_user.first_name
  await update.message.reply_text(
      f"سلام {user_name} عزیز! 🎵\n"
      "لینک آهنگ ساندکلاد رو بفرست تا با کیفیت مناسب برات دانلود کنم."
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  url = update.message.text.strip()

  if "soundcloud.com" not in url:
    await update.message.reply_text(
        "❌ لطفاً یک لینک معتبر از ساندکلاد ارسال کنید."
    )
    return

  status_message = await update.message.reply_text(
      "⏳ در حال دانلود موزیک از ساندکلاد..."
  )

  ydl_opts = {
      "format": "bestaudio/best",
      "outtmpl": "audio_temp.%(ext)s",
      "quiet": True,
  }

  try:
    file_path = None
    title = "SoundCloud Track"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      title = info.get("title", "SoundCloud Track")
      ext = info.get("ext", "mp3")
      file_path = f"audio_temp.{ext}"

    if not os.path.exists(file_path):
      for e in ["mp3", "m4a", "webm", "opus", "mp4"]:
        if os.path.exists(f"audio_temp.{e}"):
          file_path = f"audio_temp.{e}"
          break

    if file_path and os.path.exists(file_path):
      await status_message.edit_text("📤 در حال ارسال فایل به تلگرام...")

      with open(file_path, "rb") as audio_file:
        await update.message.reply_audio(
            audio=audio_file,
            title=title,
            performer="SoundCloud Bot",
            read_timeout=120,
            write_timeout=120,
            connect_timeout=60,
        )

      os.remove(file_path)
      await status_message.delete()
    else:
      await status_message.edit_text("❌ خطا در پیدا کردن فایل دانلود شده.")

  except Exception as e:
    logger.error(f"Error: {e}")
    await status_message.edit_text("❌ مشکلی در دانلود این لینک پیش آمد.")


def main():
  application = (
      ApplicationBuilder()
      .token(TOKEN)
      .read_timeout(30)
      .write_timeout(30)
      .connect_timeout(30)
      .pool_timeout(30)
      .build()
  )

  application.add_handler(CommandHandler("start", start))
  application.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
  )

  print("🤖 ربات با موفقیت روشن شد و آماده دریافت لینک است...")
  application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
  main()
