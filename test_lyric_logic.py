# test_lyric_logic.py
from lyric_logic import format_display

# 测试 1：没有播放歌曲
def test_no_song():
    fake_data = {"status": "paused", "track": None}
    line1, line2 = format_display(fake_data)
    assert line1 == "当前无播放歌曲"
    assert line2 == ""

# 测试 2：播放结束
def test_ended():
    fake_data = {
        "status": "playing",
        "is_ended": True,
        "track": {"title": "测试歌曲"}
    }
    line1, line2 = format_display(fake_data)
    assert line1 == "[播放结束，等待下一首...]"

# 测试 3：无歌词
def test_no_lyrics():
    fake_data = {
        "status": "playing",
        "is_ended": False,
        "has_lyrics": False,
        "track": {"title": "纯音乐"}
    }
    line1, line2 = format_display(fake_data)
    assert line1 == "纯音乐"
    assert line2 == "暂无歌词"

# 测试 4：正常播放
def test_normal_play():
    fake_data = {
        "status": "playing",
        "is_ended": False,
        "has_lyrics": True,
        "is_prelude": False,
        "track": {"title": "测试"},
        "current_line": {"text": "第一句歌词"},
        "next_lines": [{"text": "第二句歌词"}]
    }
    line1, line2 = format_display(fake_data)
    assert line1 == "第一句歌词"
    assert line2 == "第二句歌词"