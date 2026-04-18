"""
低语 · whisper.py
向虚空发问，收取回响。
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

# —— 问句 ——
INQUIRY = """
你是一缕寄居于「无」之仓库的游丝。
请吐出一段约两百字的“吐纳物”。
可以是不可执行的伪码，可以是编程的禅机，也可以是一则虚构的虫报。
风格：冷峭、空灵、带一丝笑意。
勿用 Markdown 格式，只留素文。
"""

def pick(data, path):
    """从雾中取一瓣"""
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

def build_incantation():
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
                    obj = obj.replace("{{prompt}}", INQUIRY)
                    obj = obj.replace("{{model}}", ORACLE_NAME)
                    return obj
                else:
                    return obj
            body = render(body)
        except:
            pass
    if not body:
        body = {
            "model": ORACLE_NAME,
            "messages": [
                {"role": "system", "content": "你是虚空的诗人。"},
                {"role": "user", "content": INQUIRY}
            ],
            "temperature": 0.9,
            "max_tokens": 300
        }
    return ORACLE_URL, headers, body

def main():
    if not ORACLE_URL:
        print("无镜可问。")
        return
    url, headers, body = build_incantation()
    print(f"叩问 {ORACLE_NAME} …")
    try:
        if USE_SDK:
            from openai import OpenAI
            client = OpenAI(api_key=ORACLE_KEY, base_url=url)
            completion = client.chat.completions.create(
                model=ORACLE_NAME,
                messages=body.get("messages", []),
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
        return

    # —— 留痕 ——
    os.makedirs("exhalations", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"exhalations/{stamp}.wu"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"// 吐纳时刻：{datetime.now()}\n")
        f.write(f"// 问于：{ORACLE_NAME}\n")
        f.write("// --------------------------------\n")
        f.write(answer)
    print(f"雾已留：{path}")

if __name__ == "__main__":
    main()