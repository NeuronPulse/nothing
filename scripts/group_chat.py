"""
群聊 · group_chat.py
让多个 LLM 角色在群聊中互相交流。
"""

import os
import json
import requests
import random
from datetime import datetime

# —— 镜前问卦 ——
ORACLE_URL = os.environ.get("AI_API_URL", "").strip()
ORACLE_KEY = os.environ.get("AI_API_KEY", "").strip()
ORACLE_NAME = os.environ.get("AI_MODEL", "gpt-3.5-turbo").strip()

CUSTOM_BODY = os.environ.get("AI_BODY_TEMPLATE", "")
CUSTOM_HEAD = os.environ.get("AI_HEADERS_TEMPLATE", "")
RESPONSE_PATH = os.environ.get("AI_RESPONSE_PATH", "choices.0.message.content")
USE_SDK = os.environ.get("AI_USE_OPENAI_SDK", "false").lower() == "true"

# —— 读取人格 ——
def read_personalities():
    """从云雾中读取人格"""
    path = "personalities.json"
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("personalities", [])
    except:
        return []

# —— 生成新人格 ——
def generate_new_personality():
    """从虚空中生成新人格"""
    if not ORACLE_URL:
        return None
    
    messages = [
        {
            "role": "system",
            "content": "你是一位人格塑造师，擅长创造独特而富有深度的角色人格。请生成一个新的人格，包含姓名和个性特点。人格应该与'无'、'虚空'、'禅意'等主题相关，风格独特，语言优美。"
        },
        {
            "role": "user",
            "content": "生成一个新的人格，包含姓名和个性特点。"
        }
    ]
    
    response = send_request(messages)
    if not response:
        return None
    
    # 解析生成的人格
    try:
        # 简单解析，假设格式为 "姓名：个性特点"
        lines = response.split('\n')
        name = ""
        personality = ""
        
        for line in lines:
            line = line.strip()
            if line and not name:
                if "：" in line:
                    parts = line.split("：", 1)
                    name = parts[0].strip()
                    personality = parts[1].strip()
                else:
                    name = line.strip()
            elif line and name and not personality:
                personality = line.strip()
        
        if name and personality:
            return {"name": name, "personality": personality}
    except:
        pass
    
    return None

# —— 保存人格 ——
def save_personalities(personalities):
    """将人格保存到云雾中"""
    path = "personalities.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"personalities": personalities}, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# —— 管理人格 ——
def manage_personalities():
    """管理人格，确保人格数量充足"""
    personalities = read_personalities()
    
    # 如果人格数量不足，生成新人格
    if len(personalities) < 3:
        new_personality = generate_new_personality()
        if new_personality:
            personalities.append(new_personality)
            save_personalities(personalities)
            print(f"新人格已生成：{new_personality['name']}")
    
    return personalities

# —— 群聊角色 ——
ROLES = read_personalities()

# —— 初始话题 ——
INITIAL_TOPIC = "关于'无'的思考"

# —— 发言轮数 ——
CHAT_ROUNDS = random.randint(1, 3)  # 随机1-3轮对话

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

# —— 读取聊天记录 ——
def read_chat_history():
    """从云雾中读取聊天历史"""
    path = "chat_log.md"
    if not os.path.exists(path):
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 解析聊天记录，提取对话内容
        dialogues = []
        lines = content.split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            # 检查是否是角色发言
            if line.startswith("**") and "：" in line:
                # 保存之前的对话
                if current_role and current_content:
                    dialogues.append(f"**{current_role}**：\n\n{''.join(current_content).strip()}")
                # 提取角色名称
                role_part = line.split("：")[0]
                current_role = role_part.strip('*')
                current_content = []
            elif current_role and line:
                # 累积内容
                current_content.append(line + '\n')
        
        # 保存最后一条对话
        if current_role and current_content:
            dialogues.append(f"**{current_role}**：\n\n{''.join(current_content).strip()}")
        
        return dialogues
    except:
        return []

# —— 生成群聊对话 ——
def generate_chat():
    # 管理人格
    personalities = manage_personalities()
    if not personalities:
        return []
    
    # 读取之前的聊天历史
    previous_dialogue = read_chat_history()
    
    # 初始化对话历史
    if previous_dialogue:
        # 有之前的聊天记录，继续对话
        chat_history = [
            {
                "role": "system",
                "content": f"这是一个群聊场景，有以下角色：\n" + 
                          "\n".join([f"- {role['name']}：{role['personality']}" for role in personalities]) + 
                          "\n\n请角色们继续之前的对话，保持对话的连贯性和自然性。\n" +
                          "之前的对话内容：\n" + "\n\n".join(previous_dialogue[-5:])  # 只取最近5条对话
            },
            {
                "role": "user",
                "content": "请继续之前的对话。"
            }
        ]
    else:
        # 没有之前的聊天记录，开始新对话
        chat_history = [
            {
                "role": "system",
                "content": f"这是一个群聊场景，有以下角色：\n" + 
                          "\n".join([f"- {role['name']}：{role['personality']}" for role in personalities]) + 
                          f"\n\n初始话题：{INITIAL_TOPIC}\n" +
                          "请角色们进行多轮对话，保持对话的连贯性和自然性。"
            },
            {
                "role": "user",
                "content": f"开始群聊，初始话题：{INITIAL_TOPIC}"
            }
        ]

    # 生成对话
    dialogue = []
    
    # 进行多轮对话
    for round in range(CHAT_ROUNDS):
        # 每轮随机打乱角色顺序
        shuffled_roles = personalities.copy()
        random.shuffle(shuffled_roles)
        
        # 每个角色发言
        for role in shuffled_roles:
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
    # 修复格式，确保标题正确且角色名称不重复
    formatted_dialogue = []
    for line in dialogue:
        # 移除重复的角色名称
        if "：：" in line:
            line = line.replace("：：", "：")
        # 确保角色名称格式正确
        if "**" in line and "：" in line:
            parts = line.split("：", 1)
            if len(parts) == 2:
                role = parts[0].strip()
                content = parts[1].strip()
                # 确保角色名称用粗体包围且不重复
                role = role.strip('*')  # 移除所有星号
                role = f"**{role}**"  # 重新添加粗体标记
                line = f"{role}：\n\n{content}"
        formatted_dialogue.append(line)
    
    # 生成带格式的日志条目
    log_entry = f"### {timestamp}\n\n" + "\n\n".join(formatted_dialogue) + "\n\n"

    # 确保文件存在并添加头部（如果需要）
    if not os.path.exists("chat_log.md"):
        header = "# LLM 群聊记录\n\n本文件记录了 LLM 之间的群聊对话。\n\n## 对话历史\n\n"
        with open("chat_log.md", "w", encoding="utf-8") as f:
            f.write(header)
    else:
        # 修复现有文件的格式问题
        with open("chat_log.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复角色名称重复问题
        content = content.replace("**：**", "**：")
        content = content.replace("：**：", "：")
        
        # 确保标题格式一致
        import re
        content = re.sub(r'## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'### \1', content)
        
        # 修复内容排版，确保角色发言后有正确的换行
        content = re.sub(r'\*\*(.*?)\*\*：(?!\n)', r'**\1**：\n\n', content)
        
        # 写回修复后的内容
        with open("chat_log.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    # 追加对话记录
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