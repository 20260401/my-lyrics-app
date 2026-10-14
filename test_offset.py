import requests
import json

# 你的本地服务地址
url = "http://127.0.0.1:21863/api/offset"

# 想要发送的 JSON 数据
# 负数表示让歌词延迟显示，用来治疗"歌词太快"的问题
payload = {"offset_ms": -1300}

try:
    # 发送 POST 请求
    response = requests.post(url, json=payload)
    # 打印服务器返回的状态码和内容
    print("状态码:", response.status_code)
    print("服务器返回:", response.json())
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")