from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from agent import get_system_prompt, demo_response, load_config
from tools import execute_tool, TOOL_SCHEMAS

app = Flask(__name__, static_folder='static')
CORS(app)

# Try to load LLM if API key exists
LLM_AVAILABLE = False
llm_client = None
llm_model = "gpt-4o-mini"

try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sk-..." and len(api_key) > 20:
        from openai import OpenAI
        llm_client = OpenAI(api_key=api_key)
        LLM_AVAILABLE = True
        print(f"✅ LLM connected: {llm_model}")
    else:
        print("ℹ️ No API key - running in DEMO mode")
except Exception as e:
    print(f"ℹ️ Demo mode: {e}")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/config')
def get_config():
    return jsonify(load_config())

@app.route('/api/tools')
def get_tools():
    return jsonify(TOOL_SCHEMAS)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "No message"}), 400

    # If LLM is available, use it with tool calling
    if LLM_AVAILABLE and llm_client:
        try:
            messages = [{"role": "system", "content": get_system_prompt()}]
            # add history (last 10)
            for h in history[-10:]:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_message})

            tools_for_api = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"]
                    }
                } for t in TOOL_SCHEMAS
            ]

            response = llm_client.chat.completions.create(
                model=llm_model,
                messages=messages,
                tools=tools_for_api,
                tool_choice="auto"
            )
            
            msg = response.choices[0].message
            
            # Handle tool calls
            tool_results = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    import json as js
                    args = js.loads(tc.function.arguments) if tc.function.arguments else {}
                    result = execute_tool(tc.function.name, args)
                    tool_results.append({"tool": tc.function.name, "args": args, "result": result})
                    # Add to messages for follow-up
                    messages.append(msg)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result)
                    })
                
                # Get final answer after tools
                final = llm_client.chat.completions.create(
                    model=llm_model,
                    messages=messages
                )
                answer = final.choices[0].message.content
                return jsonify({"reply": answer, "tools_used": tool_results, "mode": "llm"})
            
            return jsonify({"reply": msg.content, "tools_used": [], "mode": "llm"})
        
        except Exception as e:
            print(f"LLM error, falling back to demo: {e}")
            # fall through to demo

    # DEMO mode (rule-based, works without API key)
    reply, tool_data = demo_response(user_message, execute_tool)
    return jsonify({"reply": reply, "tools_used": [tool_data] if tool_data else [], "mode": "demo"})

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
def todos_api():
    from tools import manage_todos
    if request.method == 'GET':
        return jsonify(manage_todos("list"))
    data = request.json or {}
    if request.method == 'POST':
        if data.get("action") == "complete":
            return jsonify(manage_todos("complete", task_id=data.get("id")))
        return jsonify(manage_todos("add", task=data.get("task")))
    if request.method == 'DELETE':
        return jsonify(manage_todos("delete", task_id=request.args.get("id")))

if __name__ == '__main__':
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 Helper running on http://0.0.0.0:{port}")
    print(f"📂 Workspace: /home/user/my-agent")
    app.run(host='0.0.0.0', port=port, debug=False)
