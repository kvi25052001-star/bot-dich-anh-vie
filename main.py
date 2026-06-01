import telebot
import requests
from flask import Flask
from threading import Thread
import time
import urllib.parse

# 1. CẤU HÌNH BOT TELEGRAM
# Thay mã Token mới tinh của con bot dịch thuật vào đây bạn nhé:
BOT_TOKEN = 'ĐIỀN_TOKEN_MỚI_CỦA_BẠN_VÀO_ĐÂY'
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot Dịch Song Ngữ Anh - Việt đang online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Hàm thông minh: Tự động nhận diện ngôn ngữ và dịch đảo chiều
def translate_smart(text):
    try:
        encoded_text = urllib.parse.quote(text)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        # Bước 1: Thử dịch sang tiếng Việt trước để mượn Google nhận diện ngôn ngữ gốc (sl=auto)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=vi&dt=t&q={encoded_text}"
        response = requests.get(url, headers=headers, timeout=10).json()
        
        # Google trả về ngôn ngữ gốc được phát hiện ở vị trí response[2]
        detected_lang = response[2] 
        
        # Bước 2: Cài đặt logic đảo chiều
        if detected_lang == 'vi':
            # Nếu người dùng nhập tiếng Việt -> Dịch sang tiếng Anh (tl=en)
            url_en = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=en&dt=t&q={encoded_text}"
            response = requests.get(url_en, headers=headers, timeout=10).json()
            target_label = "🇬🇧 **Bản dịch Tiếng Anh (English):**"
        else:
            # Nếu nhập tiếng Anh (hoặc ngôn ngữ khác) -> Giữ nguyên kết quả dịch sang tiếng Việt ở Bước 1
            target_label = "🇻🇳 **Bản dịch Tiếng Việt:**"
            
        # Bước 3: Ghép các câu kết quả lại
        translated_text = ""
        for sentence in response[0]:
            if sentence[0]:
                translated_text += sentence[0]
                
        return translated_text, target_label
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")
        return None, None

# Lệnh /start chào hỏi bằng cả 2 thứ tiếng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 Welcome! Tôi là Bot dịch thuật Song ngữ thông minh.\n\n"
        "📥 Bạn chỉ cần gửi tin nhắn vào đây:\n"
        "▪️ Gửi **Tiếng Anh** ➔ Bot tự dịch sang **Tiếng Việt**\n"
        "▪️ Gửi **Tiếng Việt** ➔ Bot tự dịch sang **Tiếng Anh**\n\n"
        "Không cần bấm nút chọn, tôi tự động nhận biết hết!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# Lắng nghe tin nhắn văn bản và xử lý tự động
@bot.message_handler(func=lambda message: True)
def handle_translation(message):
    user_text = message.text
    
    if user_text.startswith('/'):
        return
        
    msg = bot.reply_to(message, "🔄 Đang nhận diện và dịch, đợi tí nhé...")
    
    # Chạy hàm dịch thông minh
    result, label = translate_smart(user_text)
    
    if result and label:
        # Trả về kết quả kèm nhãn ngôn ngữ tương ứng
        bot.edit_message_text(f"{label}\n\n{result}", message.chat.id, msg.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ Hệ thống dịch thuật đang bận. Vui lòng thử lại sau!", message.chat.id, msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
    except Exception:
        pass

    print("Bot Dịch Song Ngữ đã hoạt động!")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
