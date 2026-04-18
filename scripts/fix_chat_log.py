"""
修复聊天记录格式 · fix_chat_log.py
修复聊天记录中的格式问题。
"""

import re

def fix_chat_log():
    """修复聊天记录格式"""
    path = "chat_log.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复时间戳与内容之间的空格问题
        content = re.sub(r'(### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'\1\n\n', content)
        content = re.sub(r'(#### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'\1\n\n', content)
        
        # 确保标题格式一致，统一使用三级标题
        content = re.sub(r'#### (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'### \1', content)
        
        # 修复角色名称重复问题
        content = re.sub(r'\*\*(.*?)\*\*：\s*\*\*\1\*\*：', r'**\1**：', content)
        content = re.sub(r'\*\*(.*?)\*\*：\s*\n\s*\*\*\1\*\*：', r'**\1**：', content)
        
        # 修复内容排版，确保角色发言后有正确的换行
        content = re.sub(r'\*\*(.*?)\*\*：(?!\n)', r'**\1**：\n\n', content)
        
        # 修复段落间的空格
        content = re.sub(r'\n\n+', r'\n\n', content)
        
        # 写回修复后的内容
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("聊天记录格式已修复。")
    except Exception as e:
        print(f"修复聊天记录格式失败：{e}")

if __name__ == "__main__":
    fix_chat_log()