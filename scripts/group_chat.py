"""
群聊 · group_chat.py
让多个 LLM 角色在群聊中互相交流。
"""

import os
import json
import requests
from datetime import datetime

# —— 镜前问卦 ——
ORACLE_URL = os.environ.get("AI_API_URL", "").strip()
ORACLE_KEY = os.environ.get("AI_API_KEY", "").strip()
ORACLE_NAME = os.environ.get("AI_MODEL", "gpt-3.5-turbo").strip()

CUSTOM_BODY = os.environ.get("AI_BODY_TEMPLATE", "")
CUSTOM_HEAD = os.environ.get("AI_HEADERS_TEMPLATE", "")
RESPONSE_PATH = os.environ.get("AI_RESPONSE_PATH", "choices.0.message.content")
USE_SDK = os.environ.get("AI_USE_OPENAI_SDK", "false").lower() == "true"

# —— 群聊角色 ——
ROLES = [
    {
        "name": "虚空诗人",
        "personality": "冷峭、空灵，喜欢用隐喻和象征，语言优美而富有哲理。"
    },
    {
        "name": "技术禅者",
        "personality": "专注于编程和技术的禅意，喜欢将技术与哲学结合，语言简洁而深刻。"
    },
    {
        "name": "幽默观察者",
        "personality": "善于发现生活中的幽默和荒诞，语言风趣而机智，带一丝讽刺。"
    }
]

# —— 初始话题 ——
INITIAL_TOPIC = "关于'无'的思考"

# —— 从雾中取一瓣 ——
def pick(data, path):
    keys = path.split('.')
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k)
        elif isinstance(data, list):
            try:
                data = data[int(k)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return data

# —— 构建请求 ——
def build_request(messages):
    headers = {"Content-Type": "application/json"}
    if ORACLE_KEY:
        headers["Authorization"] = f"Bearer {ORACLE_KEY}"
    if CUSTOM_HEAD:
        try:
            extra = json.loads(CUSTOM_HEAD)
            for k, v in extra.items():
                if isinstance(v, str):
                    v = v.replace("{{api_key}}", ORACLE_KEY)
                extra[k] = v
            headers.update(extra)
        except:
            pass

    body = {}
    if CUSTOM_BODY:
        try:
            body = json.loads(CUSTOM_BODY)
            def render(obj):
                if isinstance(obj, dict):
                    return {k: render(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [render(i) for i in obj]
                elif isinstance(obj, str):
                    # 替换消息内容
                    return obj
                else:
                    return obj
            body = render(body)
        except:
            pass
    if not body:
        body = {
            "model": ORACLE_NAME,
            "messages": messages,
            "temperature": 1,
            "top_p": 1,
            "frequency_penalty": 1,
            "presence_penalty": 1
        }
    return ORACLE_URL, headers, body

# —— 发送请求 ——
def send_request(messages):
    url, headers, body = build_request(messages)
    try:
        if USE_SDK:
            from openai import OpenAI
            client = OpenAI(api_key=ORACLE_KEY, base_url=url)
            completion = client.chat.completions.create(
                model=ORACLE_NAME,
                messages=messages,
                temperature=body.get("temperature", 0.9),
                max_tokens=body.get("max_tokens", 300)
            )
            answer = completion.choices[0].message.content.strip()
        else:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            answer = pick(data, RESPONSE_PATH)
            if answer is None:
                answer = json.dumps(data, ensure_ascii=False, indent=2)
            else:
                answer = answer.strip()
    except Exception as e:
        print(f"虚空沉默：{e}")
        return None
    return answer

# —— 生成群聊对话 ——
def generate_chat():
    # 初始化对话历史
    chat_history = [
        {
            "role": "system",
            "content": f"这是一个群聊场景，有以下角色：\n" + 
                      "\n".join([f"- {role['name']}：{role['personality']}" for role in ROLES]) + 
                      f"\n\n初始话题：{INITIAL_TOPIC}\n" +
                      "请每个角色轮流发言，保持对话的连贯性和自然性。"
        },
        {
            "role": "user",
            "content": f"开始群聊，初始话题：{INITIAL_TOPIC}"
        }
    ]

    # 每个角色轮流发言
    dialogue = []
    for role in ROLES:
        # 构建该角色的消息
        role_message = {
            "role": "user",
            "content": f"现在请{role['name']}发言，保持其个性特点：{role['personality']}"
        }
        chat_history.append(role_message)

        # 发送请求获取回复
        response = send_request(chat_history)
        if response:
            dialogue.append(f"**{role['name']}**：{response}")
            # 将回复添加到对话历史
            chat_history.append({
                "role": "assistant",
                "content": response
            })

    return dialogue

# —— 更新聊天记录 ——
def update_chat_log(dialogue):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"## {timestamp}\n\n" + "\n\n".join(dialogue) + "\n\n"

    with open("chat_log.md", "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"群聊记录已更新：{timestamp}")

def main():
    if not ORACLE_URL:
        print("无镜可问。")
        return

    print("开始群聊...")
    dialogue = generate_chat()
    if dialogue:
        update_chat_log(dialogue)
    else:
        print("群聊失败。")

if __name__ == "__main__":
    main()