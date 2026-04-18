"""
数雾 · count_mist.py
清点吐纳之物，绘作云雾徽记。
"""

import os

def mist_count():
    path = "exhalations"
    if not os.path.exists(path):
        return 0
    return len([f for f in os.listdir(path) if f.endswith('.wu')])

def paint_mist(n):
    label = "雾"
    lw = 40
    vw = 40
    tw = lw + vw
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#ccc" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="{tw}" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#3a3a3a" d="M0 0h{lw}v20H0z"/>
    <path fill="#7c8ca4" d="M{lw} 0h{vw}v20H{lw}z"/>
    <path fill="url(#b)" d="M0 0h{tw}v20H0z"/>
  </g>
  <g fill="#e0e0e0" text-anchor="middle" font-family="Georgia, serif" font-size="11">
    <text x="{lw/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{lw/2}" y="14">{label}</text>
    <text x="{lw+vw/2}" y="15" fill="#010101" fill-opacity=".3">{n}</text>
    <text x="{lw+vw/2}" y="14">{n}</text>
  </g>
</svg>'''
    return svg

def main():
    n = mist_count()
    with open("mist.svg", "w", encoding="utf-8") as f:
        f.write(paint_mist(n))
    print(f"雾数：{n}")

if __name__ == "__main__":
    main()