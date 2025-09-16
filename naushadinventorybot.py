# ================================
# 🤖 Telegram Inventory Bot (Hinglish/Hindi/English)
# Sheet: naushadinventory
# Mode: OPEN FOR ALL (CLIENT_ID = skip)
# ================================

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔐 Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
SHEET_NAME = "naushadinventory"  # <-- Aapki sheet ka naam
sheet = client.open(SHEET_NAME).sheet1

# 🌐 Language & User Storage
user_lang = {}

# 📝 Texts in 3 Languages
def reply_text(user_id, key):
    lang = user_lang.get(user_id, 'English')
    texts = {
        'welcome': {
            'हिंदी': 'स्वागत है! कृपया भाषा चुनें।',
            'English': 'Welcome! Please choose your language.',
            'Hinglish': 'Swagat hai! Kripya apni bhasha chunein.'
        },
        'lang_set': {
            'हिंदी': 'भाषा सेट हो गई: हिंदी। अब आप कमांड्स का उपयोग कर सकते हैं।',
            'English': 'Language set. You can now use commands like /additem, /viewstock.',
            'Hinglish': 'Bhasha set ho gayi! Ab aap /additem, /viewstock jaise commands use kar sakte hain.'
        },
        'add_usage': {
            'हिंदी': 'इस्तेमाल: /additem <नाम> <मात्रा> <कीमत>',
            'English': 'Usage: /additem <name> <quantity> <price>',
            'Hinglish': 'Istemaal: /additem <naam> <kitna> <daam>'
        },
        'item_added': {
            'हिंदी': '✅ आइटम सफलतापूर्वक जोड़ा गया!',
            'English': '✅ Item added successfully!',
            'Hinglish': '✅ Item add ho gaya boss!'
        },
        'no_items': {
            'हिंदी': 'अभी स्टॉक खाली है 😅',
            'English': 'No items in stock yet 😅',
            'Hinglish': 'Stock abhi khali hai yaar 😅'
        }
    }
    return texts[key][lang]

# 🎯 START COMMAND
def start(update: Update, context: CallbackContext):
    keyboard = [['हिंदी', 'English', 'Hinglish']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(reply_text(update.message.from_user.id, 'welcome'), reply_markup=markup)

# 🌍 LANGUAGE HANDLER
def set_language(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    choice = update.message.text
    if choice in ['हिंदी', 'English', 'Hinglish']:
        user_lang[user_id] = choice
        update.message.reply_text(reply_text(user_id, 'lang_set'))
    else:
        update.message.reply_text("❌ Invalid choice. Please choose again.")

# ➕ ADD ITEM
def add_item(update: Update, context: CallbackContext):
    try:
        _, name, qty, price = update.message.text.split(' ', 3)
        today = datetime.now().strftime("%Y-%m-%d")
        sheet.append_row([name, qty, price, today])
        update.message.reply_text(reply_text(update.message.from_user.id, 'item_added'))
    except Exception as e:
        print(e)
        update.message.reply_text(reply_text(update.message.from_user.id, 'add_usage'))

# 👀 VIEW STOCK
def view_stock(update: Update, context: CallbackContext):
    try:
        data = sheet.get_all_records()
        if not data:
            update.message.reply_text(reply_text(update.message.from_user.id, 'no_items'))
            return

        msg = "📦 *CURRENT STOCK*\n\n"
        for item in data:
            msg += f"• {item['Item Name']} — Qty: {item['Quantity']}, ₹{item['Price']}\n"
        update.message.reply_text(msg)
    except Exception as e:
        print(e)
        update.message.reply_text("❌ Error fetching stock. Check sheet permissions!")

# ⚙️ MAIN FUNCTION
def main():
    updater = Updater("7970461420:AAF7BIrNiMzFr9ldvZnm5rEyYvzV5utrmac", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^(हिंदी|English|Hinglish)$'), set_language))
    dp.add_handler(CommandHandler("additem", add_item))
    dp.add_handler(CommandHandler("viewstock", view_stock))

    print("✅ Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    main()
