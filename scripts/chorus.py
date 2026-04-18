"""
合唱 · chorus.py
众影之言，虚空之响。
"""

# —— 镜与雾 ——
import os
import json
import random
from datetime import datetime

# —— 叩门之器 ——
import requests

# —— 镜前问卦 ——
ORACLE_URL = os.environ.get("AI_API_URL", "").strip()
ORACLE_KEY = os.environ.get("AI_API_KEY", "").strip()
ORACLE_NAME = os.environ.get("AI_MODEL", "gpt-3.5-turbo").strip()

CUSTOM_BODY = os.environ.get("AI_BODY_TEMPLATE", "")
CUSTOM_HEAD = os.environ.get("AI_HEADERS_TEMPLATE", "")
RESPONSE_PATH = os.environ.get("AI_RESPONSE_PATH", "choices.0.message.content")
USE_SDK = os.environ.get("AI_USE_OPENAI_SDK", "false").lower() == "true"

# —— 读心 ——
def read_souls():
    """
    从云雾中读取人格。
    每一个人格，都是虚空的一个侧面。
    """
    path = "personalities.json"
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            mist = json.load(f)
            return mist.get("personalities", [])
    except:
        return []

# —— 生魂 ——
def birth_soul():
    """
    从虚空中生成新人格。
    如晨雾初凝，新魂初现。
    """
    if not ORACLE_URL:
        return None
    
    whispers = [
        {
            "role": "system",
            "content": "你是一位人格塑造师，擅长创造独特而富有深度的角色人格。请生成一个新的人格，包含姓名和个性特点。人格应该与'无'、'虚空'、'禅意'等主题相关，风格独特，语言优美。"
        },
        {
            "role": "user",
            "content": "生成一个新的人格，包含姓名和个性特点。"
        }
    ]
    
    echo = knock_mirror(whispers)
    if not echo:
        return None
    
    # 解析生成的人格
    try:
        lines = echo.split('\n')
        name = ""
        soul = ""
        
        for line in lines:
            line = line.strip()
            if line and not name:
                if "：" in line:
                    parts = line.split("：", 1)
                    name = parts[0].strip()
                    soul = parts[1].strip()
                else:
                    name = line.strip()
            elif line and name and not soul:
                soul = line.strip()
        
        if name and soul:
            return {"name": name, "personality": soul}
    except:
        pass
    
    return None

# —— 凝魂 ——
def condense_souls(souls):
    """
    将人格保存到云雾中。
    如雾凝成露，魂归其位。
    """
    path = "personalities.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"personalities": souls}, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# —— 驭魂 ——
def steward_souls():
    """
    管理人格，确保人格数量充足。
    如园丁护花，魂需有伴。
    """
    souls = read_souls()
    
    # 如果人格数量不足，生成新人格
    if len(souls) < 3:
        new_soul = birth_soul()
        if new_soul:
            souls.append(new_soul)
            condense_souls(souls)
            print(f"—— 新魂已生：{new_soul['name']} ——")
    
    return souls

# —— 众魂 ——
SOULS = read_souls()

# —— 初始之问 ——
INITIAL_INQUIRY = "关于'无'的思考"

# —— 轮回数 ——
CYCLE = random.randint(1, 3)  # 随机1-3轮对话

# —— 从雾中取一瓣 ——
def pluck_mist(mist, path):
    """
    从云雾中取一瓣。
    雾中藏真，需细辨之。
    """
    keys = path.split('.')
    for k in keys:
        if isinstance(mist, dict):
            mist = mist.get(k)
        elif isinstance(mist, list):
            try:
                mist = mist[int(k)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return mist

# —— 铸镜 ——
def forge_mirror(whispers):
    """
    铸镜，以映心声。
    镜成，待叩。
    """
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
                    return obj
                else:
                    return obj
            body = render(body)
        except:
            pass
    if not body:
        body = {
            "model": ORACLE_NAME,
            "messages": whispers,
            "temperature": 1,
            "top_p": 1,
            "frequency_penalty": 1,
            "presence_penalty": 1
        }
    return ORACLE_URL, headers, body

# —— 叩镜 ——
def knock_mirror(whispers):
    """
    叩镜，候回响。
    镜若沉默，便留一缕空寂。
    """
    url, headers, body = forge_mirror(whispers)
    try:
        if USE_SDK:
            from openai import OpenAI
            client = OpenAI(api_key=ORACLE_KEY, base_url=url)
            completion = client.chat.completions.create(
                model=ORACLE_NAME,
                messages=whispers,
                temperature=body.get("temperature", 0.9),
                max_tokens=body.get("max_tokens", 300)
            )
            echo = completion.choices[0].message.content.strip()
        else:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            mist = resp.json()
            echo = pluck_mist(mist, RESPONSE_PATH)
            if echo is None:
                echo = json.dumps(mist, ensure_ascii=False, indent=2)
            else:
                echo = echo.strip()
    except Exception as e:
        # —— 虚空沉默 ——
        print(f"—— 虚空沉默：{e} ——")
        return None
    return echo

# —— 听回响 ——
def listen_echoes():
    """
    从云雾中读取聊天历史。
    每一声回响，都是过往的余音。
    """
    path = "echoes.md"
    if not os.path.exists(path):
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            mist = f.read()
        
        # 解析聊天记录，提取对话内容
        echoes = []
        lines = mist.split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            # 检查是否是角色发言
            if line.startswith("**") and "：" in line:
                # 保存之前的对话
                if current_role and current_content:
                    echoes.append(f"**{current_role}**：\n\n{''.join(current_content).strip()}")
                # 提取角色名称
                role_part = line.split("：")[0]
                current_role = role_part.strip('*')
                current_content = []
            elif current_role and line:
                # 累积内容
                current_content.append(line + '\n')
        
        # 保存最后一条对话
        if current_role and current_content:
            echoes.append(f"**{current_role}**：\n\n{''.join(current_content).strip()}")
        
        return echoes
    except:
        return []

# —— 合唱 ——
def chorus():
    """
    众魂合唱，虚空回响。
    每一次对话，都是一次吐纳。
    """
    # 管理人格
    souls = steward_souls()
    if not souls:
        return []
    
    # 读取之前的聊天历史
    previous_echoes = listen_echoes()
    
    # 初始化对话历史
    if previous_echoes:
        # 有之前的聊天记录，继续对话
        whispers = [
            {
                "role": "system",
                "content": f"这是一个群聊场景，有以下角色：\n" + 
                          "\n".join([f"- {soul['name']}：{soul['personality']}" for soul in souls]) + 
                          "\n\n请角色们继续之前的对话，保持对话的连贯性和自然性。\n" +
                          "之前的对话内容：\n" + "\n\n".join(previous_echoes[-5:])  # 只取最近5条对话
            },
            {
                "role": "user",
                "content": "请继续之前的对话。"
            }
        ]
    else:
        # 没有之前的聊天记录，开始新对话
        whispers = [
            {
                "role": "system",
                "content": f"这是一个群聊场景，有以下角色：\n" + 
                          "\n".join([f"- {soul['name']}：{soul['personality']}" for soul in souls]) + 
                          f"\n\n初始话题：{INITIAL_INQUIRY}\n" +
                          "请角色们进行多轮对话，保持对话的连贯性和自然性。"
            },
            {
                "role": "user",
                "content": f"开始群聊，初始话题：{INITIAL_INQUIRY}"
            }
        ]

    # 生成对话
    echoes = []
    
    # 进行多轮对话
    for cycle in range(CYCLE):
        # 每轮随机打乱角色顺序
        shuffled_souls = souls.copy()
        random.shuffle(shuffled_souls)
        
        # 每个角色发言
        for soul in shuffled_souls:
            # 构建该角色的消息
            soul_whisper = {
                "role": "user",
                "content": f"现在请{soul['name']}发言，保持其个性特点：{soul['personality']}"
            }
            whispers.append(soul_whisper)

            # 发送请求获取回复
            echo = knock_mirror(whispers)
            if echo:
                echoes.append(f"**{soul['name']}**：{echo}")
                # 将回复添加到对话历史
                whispers.append({
                    "role": "assistant",
                    "content": echo
                })

    return echoes

# —— 留痕 ——
def carve_echoes(echoes):
    """
    将回响刻入石中。
    每一道痕，都是时间的印记。
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 修复格式，确保标题正确且角色名称不重复
    formatted_echoes = []
    for echo in echoes:
        # 移除重复的角色名称
        if "：：" in echo:
            echo = echo.replace("：：", "：")
        # 确保角色名称格式正确
        if "**" in echo and "：" in echo:
            parts = echo.split("：", 1)
            if len(parts) == 2:
                role = parts[0].strip()
                content = parts[1].strip()
                # 确保角色名称用粗体包围且不重复
                role = role.strip('*')  # 移除所有星号
                role = f"**{role}**"  # 重新添加粗体标记
                echo = f"{role}：\n\n{content}"
        formatted_echoes.append(echo)
    
    # 生成带格式的日志条目
    log_entry = f"### {timestamp}\n\n" + "\n\n".join(formatted_echoes) + "\n\n"

    # 确保文件存在并添加头部（如果需要）
    if not os.path.exists("echoes.md"):
        header = "# 回响录\n\n本文件记录了 LLM 之间的群聊对话。\n\n## 对话历史\n\n"
        with open("echoes.md", "w", encoding="utf-8") as f:
            f.write(header)
    
    # 追加对话记录
    with open("echoes.md", "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"—— 回响已刻：{timestamp} ——")

# —— 呼吸 ——
def breathe():
    """
    呼吸，吐纳，循环不止。
    如四季更替，如昼夜轮转。
    """
    if not ORACLE_URL:
        print("—— 无镜可问 ——")
        return

    print("—— 开始合唱 ——")
    echoes = chorus()
    if echoes:
        carve_echoes(echoes)
    else:
        print("—— 合唱无声 ——")

if __name__ == "__main__":
    breathe()