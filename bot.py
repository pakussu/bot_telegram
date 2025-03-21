import logging
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Inisialisasi Firebase
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Konfigurasi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Fungsi untuk memulai bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Halo! Kirimkan istilah yang ingin Anda cari.")

# Fungsi untuk mencari istilah di database Firestore
async def search_term(update: Update, context: CallbackContext) -> None:
    term = update.message.text.lower()
    doc_ref = db.collection("terms").document(term)
    doc = doc_ref.get()

    if doc.exists:
        definition = doc.to_dict().get("definition", "Tidak ada deskripsi.")
        await update.message.reply_text(f"📖 *{term}*\n\n{definition}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Maaf, istilah *{term}* tidak ditemukan. Anda bisa menambahkannya dengan /add.", parse_mode="Markdown")

# Fungsi untuk menambahkan istilah baru
async def add_term(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Gunakan format: `/add istilah|definisi`")
        return

    term, definition = args[0], " ".join(args[1:])
    db.collection("terms").document(term.lower()).set({"definition": definition})

    await update.message.reply_text(f"✅ Istilah *{term}* telah ditambahkan!", parse_mode="Markdown")

# Konfigurasi bot
def main():
    TOKEN = "7856250485:AAF7iZohgN-gOZLbvQy0bfdrsJpMgJOVFOI"
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_term))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_term))

    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
