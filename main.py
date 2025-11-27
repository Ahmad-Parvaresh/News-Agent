import os
import google.generativeai as genai
import telebot
import feedparser

# دریافت توکن‌ها
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOUR_CHAT_ID = os.environ.get("CHAT_ID")

# منابع خبری
RSS_URLS = [
    "https://www.zoomit.ir/feed/",
    "https://digiato.com/feed",
    "https://zoomit.ir/feed/tech/",
]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def clean_html(raw_html):
    return raw_html.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")

def run_news_agent():
    print("Checking RSS feeds...")
    news_pool = []
    
    # گرفتن اخبار خام
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                summary = clean_html(entry.summary)[:200]
                news_pool.append(f"Title: {entry.title}\nSummary: {summary}\nLink: {entry.link}\n---")
        except Exception as e:
            print(f"Error reading {url}: {e}")

    if not news_pool:
        # اگر کلا اینترنت قطع بود یا RSS خالی بود
        bot.send_message(YOUR_CHAT_ID, "🙂")
        return

    # دستور به جمینای
    all_news_text = "\n".join(news_pool)
    
    prompt = f"""
    لیست اخبار زیر را بررسی کن.
    فقط اگر خبری درباره "هوش مصنوعی (AI)" یا "تکنولوژی مهم" است آن را انتخاب و فارسی خلاصه کن (با لینک).
    
    خیلی مهم: اگر هیچ خبر مهمی درباره هوش مصنوعی یا تکنولوژی نبود، فقط و فقط کلمه "NO_NEWS" را برگردان.

    اخبار:
    {all_news_text}
    """
    
    try:
        response = model.generate_content(prompt)
        final_text = response.text.strip()
        
        # --- تغییر جدید اینجاست ---
        if "NO_NEWS" in final_text:
            # اگر خبری نبود، لبخند بفرست
            bot.send_message(YOUR_CHAT_ID, "🙂")
            print("Sent smile emoji.")
        else:
            # اگر خبر بود، خبر را بفرست
            bot.send_message(YOUR_CHAT_ID, final_text)
            print("News sent!")
            
    except Exception as e:
        print(f"Error: {e}")
        # حتی اگر ارور داد هم یک لبخند بفرست که بفهمی زنده است
        bot.send_message(YOUR_CHAT_ID, "🙂 (Error)")

if __name__ == "__main__":
    run_news_agent()
