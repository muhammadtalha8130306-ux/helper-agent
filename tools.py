"""
Helper — All Tools (Trilingual + Full Suite)
"""
import json
import os
import re
from datetime import datetime, timedelta
import pytz

WORKSPACE = "/home/user/my-agent"
TODO_FILE = f"{WORKSPACE}/memory_todos.json"
NOTES_FILE = f"{WORKSPACE}/memory_notes.json"
CALENDAR_FILE = f"{WORKSPACE}/memory_calendar.json"
EMAIL_OUTBOX = f"{WORKSPACE}/memory_emails.json"
WHATSAPP_OUTBOX = f"{WORKSPACE}/memory_whatsapp.json"

def get_current_time():
    tz = pytz.timezone("Asia/Karachi")
    now = datetime.now(tz)
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S %A"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "Asia/Karachi",
        "iso": now.isoformat()
    }

# ---------- TODOS ----------
def manage_todos(action="list", task=None, task_id=None):
    os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'w') as f: json.dump([], f)
    with open(TODO_FILE, 'r') as f: todos = json.load(f)
    if action == "list":
        return {"todos": todos, "count": len(todos)}
    elif action == "add" and task:
        new_task = {"id": len(todos)+1, "task": task, "created": get_current_time()["datetime"], "done": False}
        todos.append(new_task)
        with open(TODO_FILE, 'w') as f: json.dump(todos, f, indent=2)
        return {"success": True, "added": new_task, "todos": todos}
    elif action == "complete" and task_id:
        for t in todos:
            if t["id"] == int(task_id):
                t["done"]=True; t["completed_at"]=get_current_time()["datetime"]
        with open(TODO_FILE, 'w') as f: json.dump(todos, f, indent=2)
        return {"success": True, "todos": todos}
    elif action == "delete" and task_id:
        todos=[t for t in todos if t["id"]!=int(task_id)]
        with open(TODO_FILE, 'w') as f: json.dump(todos, f, indent=2)
        return {"success": True, "todos": todos}
    return {"error": "Use: list, add, complete, delete"}

# ---------- NOTES ----------
def manage_notes(action="list", content=None, title=None):
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'w') as f: json.dump([], f)
    with open(NOTES_FILE, 'r') as f: notes=json.load(f)
    if action=="list":
        return {"notes": notes[-10:], "count": len(notes)}
    elif action=="add" and content:
        new_note={"id":len(notes)+1,"title":title or f"Note {len(notes)+1}","content":content,"created":get_current_time()["datetime"]}
        notes.append(new_note)
        with open(NOTES_FILE,'w') as f: json.dump(notes,f,indent=2)
        return {"success":True,"added":new_note}
    elif action=="search" and content:
        results=[n for n in notes if content.lower() in n["content"].lower() or content.lower() in n["title"].lower()]
        return {"results":results,"count":len(results)}
    return {"error":"Use: list, add, search"}

# ---------- CALCULATOR ----------
def calculate_tool(expression):
    try:
        allowed=set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return {"error":"Invalid characters. Use numbers + - * / ( ) . %"}
        result=eval(expression,{"__builtins__":{}})
        return {"expression":expression,"result":result}
    except Exception as e:
        return {"error":str(e)}

# ---------- WEATHER (no API key - uses wttr.in) ----------
def get_weather(city="Utmanzai"):
    try:
        import requests
        # wttr.in returns JSON without key
        url=f"https://wttr.in/{city}?format=j1"
        r=requests.get(url,timeout=8)
        if r.status_code==200:
            data=r.json()
            cur=data.get("current_condition",[{}])[0]
            nearest=data.get("nearest_area",[{}])[0].get("areaName",[{}])[0].get("value",city)
            return {
                "city": nearest or city,
                "temp_C": cur.get("temp_C"),
                "temp_F": cur.get("temp_F"),
                "weather": cur.get("weatherDesc",[{}])[0].get("value"),
                "humidity": cur.get("humidity"),
                "wind_kmph": cur.get("windspeedKmph"),
                "feels_like_C": cur.get("FeelsLikeC"),
                "observation_time": cur.get("observation_time"),
                "forecast": data.get("weather",[])[:2]
            }
        else:
            return {"error":f"Weather API error {r.status_code}"}
    except Exception as e:
        # fallback mock
        return {"city":city,"temp_C":"--","weather":"Weather service busy, try again","error":str(e)}

# ---------- CALENDAR ----------
def manage_calendar(action="list", title=None, date=None, time=None, description=None, event_id=None):
    os.makedirs(os.path.dirname(CALENDAR_FILE), exist_ok=True)
    if not os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE,'w') as f: json.dump([],f)
    with open(CALENDAR_FILE,'r') as f: events=json.load(f)
    if action=="list":
        return {"events":events,"count":len(events)}
    elif action=="add" and title:
        ev={"id":len(events)+1,"title":title,"date":date or get_current_time()["date"],"time":time or "09:00","description":description or "","created":get_current_time()["datetime"]}
        events.append(ev)
        with open(CALENDAR_FILE,'w') as f: json.dump(events,f,indent=2)
        return {"success":True,"added":ev,"events":events}
    elif action=="delete" and event_id:
        events=[e for e in events if e["id"]!=int(event_id)]
        with open(CALENDAR_FILE,'w') as f: json.dump(events,f,indent=2)
        return {"success":True,"events":events}
    return {"error":"Use: list, add, delete. For add need title, date, time"}

# ---------- EMAIL (mock outbox, needs SMTP to really send) ----------
def send_email(to=None, subject=None, body=None):
    if not to or not subject or not body:
        return {"error":"Need to, subject, body. Example: to='ali@gmail.com', subject='Hello', body='...''"}
    os.makedirs(os.path.dirname(EMAIL_OUTBOX), exist_ok=True)
    if not os.path.exists(EMAIL_OUTBOX):
        with open(EMAIL_OUTBOX,'w') as f: json.dump([],f)
    with open(EMAIL_OUTBOX,'r') as f: out=json.load(f)
    email={"id":len(out)+1,"to":to,"subject":subject,"body":body,"created":get_current_time()["datetime"],"status":"queued (add SMTP in .env to actually send)"}
    out.append(email)
    with open(EMAIL_OUTBOX,'w') as f: json.dump(out,f,indent=2)
    return {"success":True,"email":email,"note":"Saved to outbox. To actually send, add SMTP credentials in .env and I will wire it."}

# ---------- WHATSAPP (mock outbox) ----------
def send_whatsapp(to=None, message=None):
    if not to or not message:
        return {"error":"Need to and message. Example: to='+92300xxxxxxx', message='Salam!'"}
    os.makedirs(os.path.dirname(WHATSAPP_OUTBOX), exist_ok=True)
    if not os.path.exists(WHATSAPP_OUTBOX):
        with open(WHATSAPP_OUTBOX,'w') as f: json.dump([],f)
    with open(WHATSAPP_OUTBOX,'r') as f: out=json.load(f)
    msg={"id":len(out)+1,"to":to,"message":message,"created":get_current_time()["datetime"],"status":"queued (add Twilio credentials to actually send)"}
    out.append(msg)
    with open(WHATSAPP_OUTBOX,'w') as f: json.dump(out,f,indent=2)
    return {"success":True,"whatsapp":msg,"note":"Saved to outbox. Add TWILIO_SID/TOKEN in .env to really send."}

# ---------- TRANSLATE (simple helper) ----------
def translate_tool(text=None, target="english"):
    if not text:
        return {"error":"Provide text to translate"}
    # This is a placeholder - when LLM is connected it will do real translation.
    # In demo mode we give a helpful message.
    return {
        "original": text,
        "target": target,
        "translation": f"[Demo] Translation to {target}: '{text}' (Connect LLM for real translation)",
        "note": "Connect OpenAI key for real Roman Urdu <-> Hindi <-> English translation"
    }

# ---------- WEB SEARCH (placeholder - LLM will do real) ----------
def web_search(query=None):
    if not query:
        return {"error":"Provide query"}
    return {
        "query": query,
        "results": f"[Demo] Web search for '{query}' — Connect LLM + Tavily/SerpAPI for real live results. In demo, I can still chat about general knowledge.",
        "note": "Add TAVILY_API_KEY in .env for live search"
    }

# ---------- TEXT TO SPEECH (placeholder) ----------
def text_to_speech(text=None, voice="default"):
    if not text:
        return {"error":"Provide text"}
    return {
        "text": text,
        "voice": voice,
        "audio_url": None,
        "status": "Queued — Add ELEVENLABS_API_KEY for real voice. For now, use browser's built-in speech.",
        "note": "I can generate speech file when you add ElevenLabs key, or use Web Speech API in browser for free."
    }

TOOL_SCHEMAS = [
    {"name":"get_current_time","description":"Get current date/time Asia/Karachi","parameters":{"type":"object","properties":{},"required":[]}},
    {"name":"manage_todos","description":"Manage todos: list, add, complete, delete","parameters":{"type":"object","properties":{"action":{"type":"string","enum":["list","add","complete","delete"]},"task":{"type":"string"},"task_id":{"type":"integer"}},"required":["action"]}},
    {"name":"manage_notes","description":"Save/search notes & memory","parameters":{"type":"object","properties":{"action":{"type":"string","enum":["list","add","search"]},"content":{"type":"string"},"title":{"type":"string"}},"required":["action"]}},
    {"name":"calculate_tool","description":"Math calculations","parameters":{"type":"object","properties":{"expression":{"type":"string"}},"required":["expression"]}},
    {"name":"get_weather","description":"Get weather for a city (no key needed)","parameters":{"type":"object","properties":{"city":{"type":"string","description":"City name e.g. Utmanzai, Peshawar, Delhi, Lahore"}},"required":[]}},
    {"name":"manage_calendar","description":"Calendar: list, add, delete events","parameters":{"type":"object","properties":{"action":{"type":"string","enum":["list","add","delete"]},"title":{"type":"string"},"date":{"type":"string","description":"YYYY-MM-DD"},"time":{"type":"string","description":"HH:MM"},"description":{"type":"string"},"event_id":{"type":"integer"}},"required":["action"]}},
    {"name":"send_email","description":"Send email (saves to outbox, needs SMTP to actually send)","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},"required":["to","subject","body"]}},
    {"name":"send_whatsapp","description":"Send WhatsApp message (needs Twilio to actually send)","parameters":{"type":"object","properties":{"to":{"type":"string","description":"Phone with country code e.g. +92300xxxx"},"message":{"type":"string"}},"required":["to","message"]}},
    {"name":"web_search","description":"Search web for live info","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
    {"name":"text_to_speech","description":"Convert text to speech audio","parameters":{"type":"object","properties":{"text":{"type":"string"},"voice":{"type":"string"}},"required":["text"]}},
    {"name":"translate_tool","description":"Translate between English, Roman Urdu, Roman Hindi","parameters":{"type":"object","properties":{"text":{"type":"string"},"target":{"type":"string","enum":["english","roman-urdu","roman-hindi"]}},"required":["text","target"]}},
]

def execute_tool(name, args):
    try:
        if name=="get_current_time": return get_current_time()
        elif name=="manage_todos": return manage_todos(args.get("action","list"), args.get("task"), args.get("task_id"))
        elif name=="manage_notes": return manage_notes(args.get("action","list"), args.get("content"), args.get("title"))
        elif name=="calculate_tool": return calculate_tool(args.get("expression",""))
        elif name=="get_weather": return get_weather(args.get("city","Utmanzai"))
        elif name=="manage_calendar": return manage_calendar(args.get("action","list"), args.get("title"), args.get("date"), args.get("time"), args.get("description"), args.get("event_id"))
        elif name=="send_email": return send_email(args.get("to"), args.get("subject"), args.get("body"))
        elif name=="send_whatsapp": return send_whatsapp(args.get("to"), args.get("message"))
        elif name=="web_search": return web_search(args.get("query"))
        elif name=="text_to_speech": return text_to_speech(args.get("text"), args.get("voice","default"))
        elif name=="translate_tool": return translate_tool(args.get("text"), args.get("target","english"))
        else: return {"error":f"Unknown tool: {name}"}
    except Exception as e:
        return {"error":str(e)}
