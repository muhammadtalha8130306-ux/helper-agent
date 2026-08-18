"""
Helper — Trilingual Agent Core
Supports: English, Roman Urdu, Roman Hindi
"""
import json
import re

CONFIG_PATH = "/home/user/my-agent/config.json"

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_system_prompt():
    config = load_config()
    return config["system_prompt"]

def detect_language(text: str) -> str:
    """Detect roman-urdu, roman-hindi, or english"""
    t = text.lower()
    # Roman Urdu markers
    urdu_words = ["kya","hai","hoon","kar","raha","rahi","chahiye","aap","tum","main","mein","kal","aj","aaj","bhai","acha","sahih","salam","walaikum","shukriya","meherbani","zaroor","kaam","yaad","rakho","mausam","kaisa","kithay","kidhar","batao","bata","samjh","samajh"]
    hindi_words = ["namaste","kaise","kaisa","kya","hai","ho","aap","hum","mai","main","kar","rahe","krna","chahiye","bahut","accha","dhanyavad","shukriya","kaam","yaad","mausam","batao","kripya","ji","hoga","hain"]
    # Count
    u_count = sum(1 for w in urdu_words if w in t)
    h_count = sum(1 for w in hindi_words if w in t)
    # Hindi often has namaste, kaise
    if any(x in t for x in ["namaste","pranam","dhanyavad","kripya","bahut accha"]):
        return "roman-hindi"
    if any(x in t for x in ["salam","walaikum","inshallah","mashallah","bhai jaan","yaar"]):
        return "roman-urdu"
    # Use fallback: if more hindi-specific
    if h_count > u_count and any(x in t for x in ["kaise ho","kaisa hai"]):
        return "roman-hindi"
    if u_count>0:
        # ambiguous between urdu/hindi roman - default to roman-urdu for PK user
        return "roman-urdu"
    return "english"

def demo_response(user_message: str, tool_executor):
    msg = user_message.lower()
    lang = detect_language(user_message)

    # Helpers for multilingual replies
    def reply_ru(en, ru, hi):
        if lang=="roman-urdu": return ru
        if lang=="roman-hindi": return hi
        return en

    # TIME
    if any(x in msg for x in ["time","samay","waqt","baj rahe","kitne baje","date","tarikh","aaj kya"]):
        data = tool_executor("get_current_time", {})
        if lang=="roman-urdu":
            return f"🕐 Abhi ka time: **{data['datetime']}** (Asia/Karachi)\n\nAur koi kaam hai?", data
        elif lang=="roman-hindi":
            return f"🕐 Abhi ka samay: **{data['datetime']}** (Asia/Karachi)\n\nAur kuch chahiye?", data
        return f"🕐 Current time: **{data['datetime']}** (Asia/Karachi)\n\nAnything else?", data

    # WEATHER
    if any(x in msg for x in ["weather","mausam","mosam","garmi","sardi","barish"]):
        # extract city
        city="Utmanzai"
        for c in ["peshawar","lahore","karachi","islamabad","delhi","mumbai","lucknow","kanpur","utmanzai","charsadda","quetta"]:
            if c in msg:
                city=c
                break
        data = tool_executor("get_weather", {"city": city})
        if "error" in data and "temp_C" not in data:
            return reply_ru(
                f"⚠️ Weather error: {data.get('error')}",
                f"⚠️ Mausam ki info nahi mil rahi: {data.get('error')}",
                f"⚠️ Mausam ki jankari nahi mili: {data.get('error')}"
            ), data
        temp = data.get("temp_C","--")
        weather = data.get("weather","")
        hum = data.get("humidity","--")
        wind = data.get("wind_kmph","--")
        city_name = data.get("city",city)
        if lang=="roman-urdu":
            return f"🌤️ **{city_name} ka mausam:**\n{weather} — **{temp}°C**\nHumidity: {hum}% | Hawa: {wind} km/h", data
        elif lang=="roman-hindi":
            return f"🌤️ **{city_name} ka mausam:**\n{weather} — **{temp}°C**\nHumidity: {hum}% | Hawa: {wind} km/h", data
        return f"🌤️ **Weather in {city_name}:**\n{weather} — **{temp}°C**\nHumidity: {hum}% | Wind: {wind} km/h", data

    # TODO
    if any(x in msg for x in ["todo","task","remind","reminder","kaam","yad dila","yaad dila"]):
        if any(x in msg for x in ["add","create","new","banao","daldo","jodo","add karo"]):
            task = user_message
            # clean
            for w in ["add","todo","task","create","new","banao","karo","please"]:
                task = re.sub(w, "", task, flags=re.I)
            task=task.strip(" :.-")
            if len(task)<3:
                return reply_ru(
                    "What task should I add? Example: `Add todo: Buy groceries tomorrow`",
                    "Kaunsa kaam add karna hai? Example: `Add todo: Kal bazaar jana hai`",
                    "Kaunsa kaam add karna hai? Example: `Add todo: Kal bazaar jana hai`"
                ), None
            result = tool_executor("manage_todos", {"action":"add","task":task})
            return reply_ru(
                f"✅ Added: **{task}**\nYou have {len(result['todos'])} task(s).",
                f"✅ Add ho gaya: **{task}**\nTotal {len(result['todos'])} kaam hain.",
                f"✅ Add ho gaya: **{task}**\nKul {len(result['todos'])} kaam hain."
            ), result
        elif any(x in msg for x in ["list","show","dikhao","dekho","sare"]):
            result = tool_executor("manage_todos", {"action":"list"})
            if not result["todos"]:
                return reply_ru("📝 Todo list empty! Say `Add todo: ...`", "📝 Koi kaam nahi hai! `Add todo: ...` likho", "📝 Koi kaam nahi hai! `Add todo: ...` likho"), result
            lines="\n".join([f"{'✅' if t['done'] else '⬜'} **{t['id']}.** {t['task']}" for t in result["todos"]])
            return reply_ru(f"📝 **Your Todos ({result['count']}):**\n{lines}", f"📝 **Tumhare Kaam ({result['count']}):**\n{lines}", f"📝 **Aapke Kaam ({result['count']}):**\n{lines}"), result
        else:
            # default list
            result = tool_executor("manage_todos", {"action":"list"})
            if not result["todos"]:
                return reply_ru("📝 No todos yet. Try `Add todo: Call Ahmed at 5pm`","📝 Abhi koi kaam nahi. `Add todo: Ahmed ko 5 baje call` likho","📝 Abhi koi kaam nahi. `Add todo: Ahmed ko 5 baje call` likho"), result
            lines="\n".join([f"{'✅' if t['done'] else '⬜'} **{t['id']}.** {t['task']}" for t in result["todos"]])
            return f"📝 **Todos ({result['count']}):**\n{lines}", result

    # CALENDAR
    if any(x in msg for x in ["calendar","event","meeting","appointment","mulakat","schedule"]):
        if any(x in msg for x in ["add","create","banao","schedule karo"]):
            # naive extract title
            title=user_message.replace("add","").replace("calendar","").replace("event","").strip(" :")
            result=tool_executor("manage_calendar",{"action":"add","title":title or "New Event","date":None,"time":None})
            return reply_ru(f"📅 Event added: **{title}**","📅 Event add ho gaya: **{title}**","📅 Event add ho gaya: **{title}**"), result
        else:
            result=tool_executor("manage_calendar",{"action":"list"})
            if not result["events"]:
                return reply_ru("📅 No events yet. Say `Add calendar event: Meeting with Ali tomorrow 5pm`","📅 Koi event nahi hai. `Add calendar event: Kal 5 baje meeting` likho","📅 Koi event nahi hai. `Add calendar event: Kal 5 baje meeting` likho"), result
            lines="\n".join([f"📌 **{e['title']}** — {e['date']} {e['time']}" for e in result["events"]])
            return f"📅 **Calendar ({result['count']}):**\n{lines}", result

    # NOTES / MEMORY
    if any(x in msg for x in ["note","remember","yaad rakho","yaad rakh","yad rakho","save karo"]):
        if any(x in msg for x in ["add","save","remember","yaad","rakho"]):
            result=tool_executor("manage_notes",{"action":"add","content":user_message,"title":"Quick note"})
            return reply_ru("💾 Saved! I will remember that.","💾 Save kar liya! Yaad rahega.","💾 Save kar liya! Yaad rahega."), result
        else:
            result=tool_executor("manage_notes",{"action":"list"})
            if not result["notes"]:
                return reply_ru("No notes yet. Say `Remember: ...`","Koi note nahi. `Yaad rakho: ...` likho","Koi note nahi. `Yaad rakho: ...` likho"), result
            lines="\n".join([f"**{n['title']}:** {n['content'][:80]}" for n in result["notes"]])
            return f"📓 **Notes:**\n{lines}", result

    # EMAIL
    if any(x in msg for x in ["email","mail","e-mail"]):
        return reply_ru(
            "📧 To send email, tell me: `Send email to ali@gmail.com subject Hello body Salam, kaise ho?` — I will queue it (add SMTP in .env to actually send).",
            "📧 Email bhejne ke liye bolo: `Send email to ali@gmail.com subject Salam body Kya haal hai?` — Main outbox me save kar dunga (SMTP lagao to real me jayega).",
            "📧 Email bhejne ke liye bolo: `Send email to ali@gmail.com subject Namaste body Kaise ho?` — Main outbox me save kar dunga."
        ), None

    # WHATSAPP
    if any(x in msg for x in ["whatsapp","whats app","watsapp"]):
        return reply_ru(
            "💬 To send WhatsApp: `Send whatsapp to +92300xxxxxxx message Salam!` — queued (add Twilio keys to really send).",
            "💬 WhatsApp bhejne ke liye: `Send whatsapp to +92300xxxxxxx message Salam bhai!` — save ho jayega (Twilio lagao to real jayega).",
            "💬 WhatsApp bhejne ke liye: `Send whatsapp to +9198xxxxxxx message Namaste!` — save ho jayega."
        ), None

    # TRANSLATE
    if any(x in msg for x in ["translate","tarjuma","anuvaad","urdu me","hindi me","english me"]):
        return reply_ru(
            "🌐 Tell me: `Translate to roman-urdu: How are you?` or `Translate to english: kya haal hai?`",
            "🌐 Bolo: `Translate to roman-urdu: How are you?` ya `Translate to english: kya haal hai?`",
            "🌐 Bolo: `Translate to roman-hindi: How are you?` ya `Translate to english: kaise ho?`"
        ), None

    # CALCULATE
    if any(c in msg for c in ["+","-","*","/","calculate","hisab","jama","guna"]):
        exprs=re.findall(r'[\d\.\+\-\*\/\(\)% ]{3,}', user_message)
        if exprs:
            result=tool_executor("calculate_tool",{"expression":exprs[0].strip()})
            if "result" in result:
                return f"🧮 **{result['expression']} = {result['result']}**", result

    # WEB SEARCH
    if any(x in msg for x in ["search","google","dhundo","talash","khojo","who is","what is","latest"]):
        q=user_message
        result=tool_executor("web_search",{"query":q})
        return reply_ru(
            f"🔍 Search query: **{q}**\n{result['results']}\n\n*Tip: Add TAVILY_API_KEY for live web results.*",
            f"🔍 Talash: **{q}**\n{result['results']}\n\n*Live results ke liye TAVILY_API_KEY lagao.*",
            f"🔍 Khoj: **{q}**\n{result['results']}\n\n*Live results ke liye TAVILY_API_KEY lagao.*"
        ), result

    # VOICE
    if any(x in msg for x in ["voice","bolo","speak","sunao","audio"]):
        return reply_ru(
            "🔊 I can convert text to voice! Say `Speak: Hello how are you?` — in browser you can also click 🔊 on my reply to hear it.",
            "🔊 Main text ko awaz me badal sakta hoon! Bolo `Speak: Salam kya haal hai?` — reply pe 🔊 dabao to sun sakte ho.",
            "🔊 Main text ko awaz me badal sakta hoon! Bolo `Speak: Namaste kaise ho?` — reply pe 🔊 dabao."
        ), None

    # DEFAULT - trilingual greeting with instructions
    if lang=="roman-urdu":
        return f"""Assalam-o-Alaikum! Main **Helper** hoon 🤖 — Roman Urdu, Hindi aur English teenon me madad karta hoon.

**Main kya kar sakta hoon:**
- ✅ **Kaam/Todos:** `Add todo: Kal bazaar jana hai` | `Show my todos`
- 🌤️ **Mausam:** `Mausam kaisa hai Peshawar me?`
- 📅 **Calendar:** `Add calendar event: Ali se meeting kal 5 baje`
- 💾 **Yaad rakho:** `Yaad rakho: Meri birthday Aug 20 hai`
- 📧 **Email:** `Send email to ali@gmail.com subject Salam body ...`
- 💬 **WhatsApp:** `Send whatsapp to +92300xxxxxxx message Salam!`
- 🧮 **Hisab:** `Calculate (25000*15)/100`
- 🔍 **Search:** `Search latest news`
- 🔊 **Awaz:** `Speak: Salam kya haal hai?`

Bolo, kya kaam hai?""", None
    elif lang=="roman-hindi":
        return f"""Namaste! Main **Helper** hoon 🤖 — Roman Hindi, Urdu aur English teenon me madad karta hoon.

**Main kya kar sakta hoon:**
- ✅ **Kaam/Todos:** `Add todo: Kal bazaar jana hai` | `Show my todos`
- 🌤️ **Mausam:** `Mausam kaisa hai Delhi me?`
- 📅 **Calendar:** `Add calendar event: Ali se meeting kal 5 baje`
- 💾 **Yaad rakho:** `Yaad rakho: Mera birthday Aug 20 hai`
- 📧 **Email:** `Send email to ali@gmail.com subject Namaste body ...`
- 💬 **WhatsApp:** `Send whatsapp to +9198xxxxxxx message Namaste!`
- 🧮 **Hisab:** `Calculate (25000*15)/100`
- 🔍 **Search:** `Search latest news`
- 🔊 **Awaz:** `Speak: Namaste kaise ho?`

Bolo, kya kaam hai?""", None
    else:
        return f"""Hello! I'm **Helper** 🤖 — I speak English, Roman Urdu, and Roman Hindi.

**I can help with:**
- ✅ **Todos:** `Add todo: Buy groceries tomorrow` | `Show my todos`
- 🌤️ **Weather:** `What's weather in Peshawar?`
- 📅 **Calendar:** `Add calendar event: Meeting with Ali tomorrow 5pm`
- 💾 **Memory:** `Remember: My birthday is Aug 20`
- 📧 **Email:** `Send email to ali@gmail.com subject Hello body ...`
- 💬 **WhatsApp:** `Send whatsapp to +92300xxxxxxx message Salam!`
- 🧮 **Math:** `Calculate (25000*15)/100`
- 🔍 **Search:** `Search latest AI news`
- 🔊 **Voice:** `Speak: Hello how are you?`

What would you like to do?""", None
