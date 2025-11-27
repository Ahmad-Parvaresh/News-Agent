import os
import google.generativeai as genai
import telebot
import feedparser

# --- دریافت توکن‌ها ---
# نکته: ما دیگر جمینای را دستی نمیگیریم، خود کتابخانه GOOGLE_API_KEY را پیدا میکند
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOUR_CHAT_ID = os.environ.get("CHAT_ID")

# --- تنظیمات ---
RSS_URLS = [
    "https://www.zoomit.ir/feed/",
    "https://digiato.com/feed",
    "https://zoomit.ir/feed/tech/",
]

# انتخاب مدل (از نسخه پرو استفاده می‌کنیم که پایدارتر است)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def clean_html(raw_html):
    return raw_html.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")

def run_news_agent():
    # --- تست اتصال (دیباگ) ---
    # این خط به ما میگوید آیا کلید پیدا شد یا نه (بدون لو دادن کلید)
    key_status = "✅ Found" if os.environ.get("GOOGLE_API_KEY") else "❌ Not Found"
    print(f"Checking Connection... API Key status: {key_status}")
    
    print("Checking RSS feeds...")
    news_pool = []
    
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                summary = clean_html(entry.summary)[:200]
                news_pool.append(f"Title: {entry.title}\nSummary: {summary}\nLink: {entry.link}\n---")
        except Exception as e:
            print(f"Error reading {url}: {e}")

    if not news_pool:
        bot.send_message(YOUR_CHAT_ID, "🙂 (No RSS Data)")
        return

    all_news_text = "\n".join(news_pool)
    
    prompt = f"""
    لیست اخبار زیر را بررسی کن.
    اگر خبری درباره "هوش مصنوعی (AI)"، "مدل‌های زبانی" یا "تکنولوژی انقلابی" دیدی، آن را انتخاب و فارسی خلاصه کن.
    
    قانون مهم: اگر خبر مهمی نبود، فقط کلمه "NO_NEWS" را برگردان.

    اخبار:
    {all_news_text}
    """
    
    try:
        response = model.generate_content(prompt)
        final_text = response.text.strip()
        
        if "NO_NEWS" in final_text:
            bot.send_message(YOUR_CHAT_ID, "🙂")
            print("No important news. Sent smile.")
        else:
            bot.send_message(YOUR_CHAT_ID, final_text)
            print("News sent to Telegram!")
            
    except Exception as e:
        print(f"Critical Error: {e}")
        # ارسال ارور به تلگرام برای اینکه بفهمیم دردش چیست
        bot.send_message(YOUR_CHAT_ID, f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_news_agent()
