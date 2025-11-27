import os
import google.generativeai as genai
import telebot
import feedparser

# دریافت توکن‌ها از مخزن امن گیت‌هاب
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOUR_CHAT_ID = os.environ.get("CHAT_ID")

RSS_URLS = [
    "https://www.zoomit.ir/feed/",
    "https://digiato.com/feed"
]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def run_agent():
    print("Connecting to RSS feeds...")
    all_news = []
    
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            # فقط خبر اول هر سایت را می‌گیریم
            if feed.entries:
                entry = feed.entries[0]
                all_news.append(f"- {entry.title} (Link: {entry.link})")
        except Exception as e:
            print(f"Error: {e}")

    if not all_news:
        return

    # ارسال به جمینای
    prompt = f"""
    اخبار زیر را بخوان و فقط ۱ خبر که جذاب‌تر است را انتخاب کن.
    آن را بسیار کوتاه (در حد ۲ خط) برای تلگرام بازنویسی کن.
    لینک را زیرش بگذار.
    
    {all_news}
    """
    
    try:
        response = model.generate_content(prompt)
        # ارسال به تلگرام
        bot.send_message(YOUR_CHAT_ID, response.text)
        print("News sent to Telegram!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_agent()
