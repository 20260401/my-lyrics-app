import tkinter as tk
import requests
import time
import requests
from lyric_logic import format_display

API_URL = "http://127.0.0.1:21863/api/status"

# ================= 全局样式变量 =================
current_font_size = 28
current_color = "yellow"

# ================= 状态记忆区 =================
last_track_id = None
has_printed_ended = False
last_printed_line = None
is_first_run = True


def create_window():
    root = tk.Tk()
    root.title("透明歌词")
    transparent_color = "#ff00ff"
    root.configure(bg=transparent_color)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", transparent_color)
    # 窗口的宽和高
    window_width = 800
    # 根据初始字号计算高度，保证初始窗口能装下大字号
    window_height = current_font_size * 2 + 80

    # 获取屏幕宽度
    screen_width = root.winfo_screenwidth()

    # 计算水平居中坐标：(屏幕宽 - 窗口宽) / 2
    x = int((screen_width - window_width) / 2)

    # 顶部留一点点间距，比如 20 像素
    y = 20

    # 设置几何尺寸和位置
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.grid_columnconfigure(0, weight=1)

    left_label = tk.Label(root, text="", anchor="w", bg=transparent_color,
                          fg=current_color, font=("Microsoft YaHei UI", current_font_size, "bold"),
                          wraplength=window_width - 40)
    left_label.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

    right_label = tk.Label(root, text="", anchor="e", bg=transparent_color,
                           fg=current_color, font=("Microsoft YaHei UI", current_font_size, "bold"),
                           wraplength=window_width - 40)
    right_label.grid(row=1, column=0, sticky="e", padx=12, pady=(4, 8))
    # ==========================================
    # 右键菜单逻辑
    # ==========================================
    def apply_style():
        # 1. 应用字体和颜色
        style = ("Microsoft YaHei UI", current_font_size, "bold")
        # wraplength 表示文字超过多少像素就自动换行
        wrap = window_width - 40
        left_label.config(font=style, fg=current_color, wraplength=wrap)
        right_label.config(font=style, fg=current_color, wraplength=wrap)

        # 2. 根据字号重新计算窗口高度（两行字 + 内边距）
        new_height = current_font_size * 2 + 80
        # 保持窗口当前位置不变，只改宽高
        root.geometry(f"{window_width}x{new_height}+{root.winfo_x()}+{root.winfo_y()}")   

    def increase_font():
        global current_font_size
        current_font_size += 2
        apply_style()

    def decrease_font():
        global current_font_size
        if current_font_size > 10:
            current_font_size -= 2
        apply_style()

    def change_color():
        global current_color
        colors = ["white", "yellow", "cyan", "lightgreen", "pink"]
        idx = colors.index(current_color) if current_color in colors else 0
        current_color = colors[(idx + 1) % len(colors)]
        apply_style()

    # 创建菜单
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="增大字号", command=increase_font)
    menu.add_command(label="减小字号", command=decrease_font)
    menu.add_separator()
    menu.add_command(label="切换颜色", command=change_color)

    # 绑定右键事件
    def show_menu(event):
        menu.post(event.x_root, event.y_root)  # 在鼠标位置弹出菜单

    root.bind("<Button-3>", show_menu)  # Windows 上 Button-3 就是右键
    
    # ==========================================
    # 窗口拖动逻辑
    # ==========================================
    def start_drag(event):
        # 记录鼠标在窗口上的相对坐标
        root.drag_start_x = event.x
        root.drag_start_y = event.y

    def on_drag(event):
        # 计算窗口应该移动到的全局坐标
        # event.x_root 和 y_root 是鼠标在屏幕上的绝对坐标
        new_x = root.winfo_x() + event.x - root.drag_start_x
        new_y = root.winfo_y() + event.y - root.drag_start_y

        # 移动窗口，格式是 "+X+Y"
        root.geometry(f"+{new_x}+{new_y}")

    # 绑定鼠标事件
    root.bind("<Button-1>", start_drag)      # 左键按下
    root.bind("<B1-Motion>", on_drag)        # 左键按住移动
    
    return root, left_label, right_label


def update_lyrics(root, left_label, right_label):
    global last_track_id, last_printed_line, is_first_run

    # ===== 1. 请求数据 =====
    try:
        data = requests.get(API_URL, timeout=2).json()
    except Exception as e:
        left_label.config(text="[连接服务失败]")
        right_label.config(text="")
        root.after(500, lambda: update_lyrics(root, left_label, right_label))
        return

    # ===== 2. 切歌检测（状态管理保留在这里，因为它需要记忆） =====
    track = data.get("track")
    if track and track.get("id") != last_track_id:
        if is_first_run:
            is_first_run = False
        last_track_id = track["id"]
        last_printed_line = None

    # ===== 3. 获取要显示的文字（核心逻辑已剥离到 lyric_logic.py） =====
    line1, line2 = format_display(data)

    # ===== 4. 更新界面（只有内容变了才更新，避免闪屏） =====
    if line1 != last_printed_line:
        left_label.config(text=line1)
        right_label.config(text=line2)
        last_printed_line = line1

    # ===== 5. 设定下一次调用 =====
    root.after(500, lambda: update_lyrics(root, left_label, right_label))


if __name__ == "__main__":
    root, left_label, right_label = create_window()
    # 启动后 0 毫秒立刻执行第一次更新
    root.after(0, lambda: update_lyrics(root, left_label, right_label))
    root.mainloop()