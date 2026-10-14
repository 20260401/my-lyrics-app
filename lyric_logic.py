# lyric_logic.py

def format_display(data):
    """
    接收 API 返回的 JSON 数据，返回两行文本。
    不负责网络请求，不负责界面显示，只负责“看数据，决定显示什么”。
    """
    # 1. 没有播放歌曲
    if data.get("status") != "playing" or not data.get("track"):
        return "当前无播放歌曲", ""

    track = data["track"]

    # 2. 播放结束
    if data.get("is_ended"):
        return "[播放结束，等待下一首...]", ""

    # 3. 无歌词
    if not data.get("has_lyrics"):
        return track["title"], "暂无歌词"

    # 4. 正常播放
    current = data.get("current_line")
    next_lines = data.get("next_lines", [])

    if current:
        line1 = current["text"]
        line2 = next_lines[0]["text"] if next_lines else ""
        return line1, line2

    # 兜底：理论上不会走到这里，但为了安全
    return "", ""