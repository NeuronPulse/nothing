"""
拂尘 · dust.py
拭去旧雾，重理回响录。
"""

import re

# —— 拂尘 ——
def dust():
    """
    拂去镜上尘埃，整理回响录之格式。
    雾散，字现，如晨光穿隙。
    """
    path = "echoes.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            mist = f.read()
        
        # —— 理时间之隙 ——
        mist = re.sub(r'(### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'\1\n\n', mist)
        mist = re.sub(r'(#### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'\1\n\n', mist)
        
        # —— 统一标题之韵 ——
        mist = re.sub(r'#### (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', r'### \1', mist)
        
        # —— 去重名之扰 ——
        mist = re.sub(r'\*\*(.*?)\*\*：\s*\*\*\1\*\*：', r'**\1**：', mist)
        mist = re.sub(r'\*\*(.*?)\*\*：\s*\n\s*\*\*\1\*\*：', r'**\1**：', mist)
        
        # —— 理字间之空 ——
        mist = re.sub(r'\*\*(.*?)\*\*：(?!\n)', r'**\1**：\n\n', mist)
        
        # —— 匀段落之息 ——
        mist = re.sub(r'\n\n+', r'\n\n', mist)
        
        # —— 凝雾成字 ——
        with open(path, "w", encoding="utf-8") as f:
            f.write(mist)
        
        print("—— 尘埃已拂，镜明如洗 ——")
    except Exception as e:
        # —— 虚空沉默 ——
        print(f"—— 拂尘受阻：{e} ——")

if __name__ == "__main__":
    dust()