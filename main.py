import requests
import time
import sys

# 防止中文乱码
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:21863/api/status"

# ================= 状态记忆区 =================
last_track_id = None          # 记住上一首歌的 ID
has_printed_ended = False     # 记住是否已经打印过“结束”
last_printed_content = None   # 记住上一次打印的完整内容（用于防重复）
is_first_run = True           # 标记是否是程序刚启动

print("歌词监听服务已启动，等待网易云播放...\n")

while True:
    try:
        # 请求数据
        resp = requests.get(API_URL, timeout=2)
        data = resp.json()
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] 请求失败，请检查服务是否运行: {e}")
        time.sleep(1)
        continue

    # 1. 判断是否有歌曲播放
    if data.get("status") != "playing" or not data.get("track"):
        if last_printed_content != "[无播放歌曲]":
            print("[无播放歌曲]")
            last_printed_content = "[无播放歌曲]"
        time.sleep(0.5)
        continue

    track = data["track"]

    # 2. 切歌检测
    if track["id"] != last_track_id:
        if is_first_run:
            is_first_run = False  # 程序启动第一次看到这首歌，不打印切歌
        else:
            print("\n" + "=" * 40)
            print(f"切歌了！新歌: {track['title']} - {track['artist']}")
            print("=" * 40)
        
        last_track_id = track["id"]
        last_printed_content = None  # 清空记忆，强制刷新歌词

    # 3. 播放结束检测
    if data.get("is_ended"):
        if not has_printed_ended:
            if not is_first_run:  # 如果是刚启动就遇到结束，不打印
                print("[播放结束，等待下一首...]")
                has_printed_ended = True
        time.sleep(0.5)
        continue
    else:
        has_printed_ended = False  # 只要没结束，就重置结束标记

    # 4. 无歌词检测
    if not data.get("has_lyrics"):
        content = f"{track['title']}\n暂无歌词"
        if last_printed_content != content:
            print(content)
            last_printed_content = content
        time.sleep(0.5)
        continue

    # 5. 前奏检测
    if data.get("is_prelude"):
        content = f"{track['title']}\n—" * 10
        if last_printed_content != content:
            print(content)
            last_printed_content = content
        time.sleep(0.5)
        continue

    # 6. 正常播放
    current = data.get("current_line")
    next_lines = data.get("next_lines", [])

    if current:
        # 构造要显示的内容（第一行：当前句，第二行：下下句）
        line1 = current["text"]
        line2 = next_lines[0]["text"] if next_lines else "—"

        # 只有当内容发生变化时才输出（解决“同样歌词重复输出”问题）
        if line1 != last_printed_content:
            print(line1)
            print(f"  {line2}")
            last_printed_content = line1

    time.sleep(0.5)