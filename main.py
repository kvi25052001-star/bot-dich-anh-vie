import telebot
import requests
from flask import Flask
from threading import Thread
import time
import urllib.parse

# 1. CẤU HÌNH BOT TELEGRAM
# ⚠️ HÃY THAY MÃ TOKEN MỚI TINH BẠN VỪA LẤY TỪ BOTFATHER VÀO ĐÂY NHÉ:
BOT_TOKEN = 'ĐIỀN_TOKEN_MỚI_CỦA_BẠN_VÀO_ĐÂY'
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot Dịch Anh - Việt đang online ổn định!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Hàm gọi API Google Translate để dịch từ Anh (sl=en) sang Việt (tl=vi)
def translate_en_to_vi(text):
    try:
        # Mã hóa văn bản tránh lỗi ký tự đặc biệt
        encoded_text = urllib.parse.quote(text)
        
        # Cấu hình API: sl=en (English), tl=vi (Vietnamese)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q={encoded_text}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10).json()
        
        # Ghép các câu đã dịch lại thành đoạn hoàn chỉnh
        translated_text = ""
        for sentence in response[0]:
            if sentence[0]:
                translated_text += sentence[0]
                
        return translated_text
    except Exception as e:
        print(f"Lỗi hệ thống dịch: {e}")
        return None

# Lệnh /start khi người dùng mới bấm vào bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 Welcome! Tôi là Bot Dịch Thuật Anh - Việt tự động.\n\n"
        "📥 Bạn chỉ cần gửi hoặc dán bất kỳ đoạn văn bản, câu thoại bằng **Tiếng Anh** nào vào đây, "
        "tôi sẽ dịch ngay sang **Tiếng Việt** cho bạn trong chớp mắt!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# Xử lý tất cả các tin nhắn văn bản thông thường
@bot.message_handler(func=lambda message: True)
def handle_translation(message):
    user_text = message.text
    
    # Bỏ qua nếu là lệnh hệ thống bắt đầu bằng dấu /
    if user_text.startswith('/'):
        return
        
    # Phản hồi trạng thái đang xử lý
    msg = bot.reply_to(message, "🔄 Translating, please wait...")
    
    # Thực hiện dịch từ Anh sang Việt
    result = translate_en_to_vi(user_text)
    
    if result:
        # Trả về kết quả và xóa tin nhắn chờ
        bot.edit_message_text(f"🇻🇳 **Bản dịch Tiếng Việt của bạn:**\n\n{result}", message.chat.id, msg.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ Cổng dịch thuật đang bận hoặc văn bản có lỗi. Vui lòng thử lại!", message.chat.id, msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    
    # Xóa webhook cũ tích tụ
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
    except Exception:
        pass

    print("Bot Dịch Anh-Việt đã sẵn sàng nhận lệnh!")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
