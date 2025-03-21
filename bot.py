import logging
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Inisialisasi Firebase dengan kredensial yang diberikan
CREDENTIALS_PATH = "infrapedia-bot-firebase-adminsdk-fbsvc-5a0da43b44.json"

try:
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("Firebase berhasil diinisialisasi.")
except Exception as e:
    logging.error(f"Error inisialisasi Firebase: {e}")

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Fungsi untuk memulai bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Halo! Kirimkan istilah yang ingin Anda cari atau gunakan /help untuk melihat panduan."
    )

# Fungsi untuk mencari istilah di database Firestore
async def search_term(update: Update, context: CallbackContext) -> None:
    term = update.message.text.strip().lower()
    logging.info(f"Mencari istilah: {term}")

    doc_ref = db.collection("terms").document(term)
    doc = doc_ref.get()

    if doc.exists:
        definition = doc.to_dict().get("definition", "Tidak ada deskripsi.")
        logging.info(f"Ditemukan: {term} -> {definition}")
        await update.message.reply_text(f"📖 *{term}*\n\n{definition}", parse_mode="Markdown")
    else:
        logging.info(f"Istilah tidak ditemukan: {term}")
        await update.message.reply_text(
            f"Maaf, istilah *{term}* tidak ditemukan. Anda bisa menambahkannya dengan `/add istilah|definisi`.",
            parse_mode="Markdown",
        )

# Fungsi untuk menambahkan istilah baru
async def add_term(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("Gunakan format: `/add istilah|definisi`")
        return

    input_text = " ".join(context.args)
    
    if "|" not in input_text:
        await update.message.reply_text("Gunakan format yang benar: `/add istilah|definisi`")
        return

    term, definition = map(str.strip, input_text.split("|", 1))

    if not term or not definition:
        await update.message.reply_text("Istilah dan definisi tidak boleh kosong.")
        return

    db.collection("terms").document(term.lower()).set({"definition": definition})
    logging.info(f"Istilah ditambahkan: {term} -> {definition}")

    await update.message.reply_text(f"✅ Istilah *{term}* telah ditambahkan!", parse_mode="Markdown")

# Fungsi untuk menampilkan panduan penggunaan bot
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
🔹 *Cara Menggunakan Bot* 🔹

✅ *Cari Istilah:*  
Ketik langsung istilah yang ingin Anda cari.

✅ *Tambah Istilah Baru:*  
Gunakan format:  
`/add istilah|definisi`

✅ *Mulai Ulang:*  
Gunakan perintah:  
`/start`
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Konfigurasi bot
def main():
    TOKEN = "7856250485:AAF7iZohgN-gOZLbvQy0bfdrsJpMgJOVFOI"

    app = Application.builder().token(TOKEN).build()

    # Tambahkan handler untuk command dan pesan
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add_term))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_term))

    logging.info("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    logging.info("Memulai bot...")
    main()
