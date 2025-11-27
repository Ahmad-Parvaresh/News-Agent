import os
import google.generativeai as genai
import telebot
import feedparser

# --- 1. دریافت توکن‌ها به روش سخت‌گیرانه ---
GEMINI_KEY = os.environ.get("MY_GEMINI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- 2. بررسی اینکه آیا توکن‌ها واقعا رسیدند؟ ---
if not GEMINI_KEY:
    raise ValueError("Error: GEMINI_KEY is missing! Check YAML file.")
if not TELEGRAM_TOKEN:
    raise ValueError("Error: TELEGRAM_TOKEN is missing!")

# --- 3. تنظیم دستی جمینای (راه حل مشکل شما) ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- تنظیمات خبری ---
RSS_URLS = [
    "https://www.zoomit.ir/feed/",
    "https://digiato.com/feed",
    "https://zoomit.ir/feed/tech/",
]

def clean_html(raw_html):
    return raw_html.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")

def run_news_agent():
    print("Bot started. Checking RSS feeds...")
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
        print("No RSS data found.")
        bot.send_message(CHAT_ID, "🙂 (RSS Empty)")
        return

    all_news_text = "\n".join(news_pool)
    
    prompt = f"""
    لیست اخبار زیر را بررسی کن.
    اگر خبری درباره "هوش مصنوعی (AI)"، "مدل‌های زبانی" یا "تکنولوژی انقلابی" دیدی، آن را انتخاب و فارسی خلاصه کن.
    قانون: اگر خبر مهمی نبود، فقط بنویس: NO_NEWS

    اخبار:
    {all_news_text}
    """
    
    try:
        response = model.generate_content(prompt)
        final_text = response.text.strip()
        
        if "NO_NEWS" in final_text:
            bot.send_message(CHAT_ID, "🙂")
            print("Sent smile.")
        else:
            bot.send_message(CHAT_ID, final_text)
            print("News sent!")
            
    except Exception as e:
        print(f"Critical Error: {e}")
        bot.send_message(CHAT_ID, f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_news_agent()
