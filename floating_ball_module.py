"""
悬浮球核心模块
负责悬浮球的显示、动画、菜单和事件处理
"""
import tkinter as tk
from PIL import Image, ImageTk
import math
from audio_upload_module import AudioUploadWindow
from chat_bot_module import ChatWindow
from file_search_module import SearchWindow

"""
悬浮球类
"""
class FloatingBall:
    def __init__(self):
        # 主悬浮球窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        
        # 创建悬浮球
        self.ball = tk.Toplevel()
        self.ball.overrideredirect(True)  # 去除窗口边框
        self.ball.attributes('-topmost', True)  # 置顶
        self.ball.attributes('-alpha', 0.7)  # 固定半透明状态
        
        # 设置悬浮球大小和位置
        self.ball_size = 80
        self.ball.geometry(f'{self.ball_size}x{self.ball_size}+100+100')
        
        # 创建圆形画布，设置圆形边界
        self.canvas = tk.Canvas(self.ball, width=self.ball_size, height=self.ball_size, 
                               highlightthickness=0, bg='#000001')
        self.canvas.pack()
        
        # 设置透明背景
        self.ball.configure(bg='#000001')
        self.ball.attributes('-transparentcolor', '#000001')
        
        # 边缘吸附相关变量
        self.is_on_edge = False
        self.original_ball_size = self.ball_size
        self.half_ball_size = self.ball_size // 2

        # 绘制圆形球体
        self.load_ball_image()
        self.draw_ball()
        
        # 功能菜单窗口
        self.menu_window = None
        self.is_menu_visible = False
        
        # 绑定事件到画布而不是窗口，实现圆形点击区域
        self.canvas.bind('<Enter>', self.on_hover_enter)
        self.canvas.bind('<Leave>', self.on_hover_leave)
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_drag_release)  # 添加释放事件
        self.canvas.bind('<Button-3>', self.show_context_menu)  # 添加右键菜单事件

        # 为圆形区域添加鼠标检测
        self.canvas.tag_bind('ball', '<Enter>', self.on_hover_enter)
        self.canvas.tag_bind('ball', '<Leave>', self.on_hover_leave)
        self.canvas.tag_bind('ball', '<Button-1>', self.start_drag)
        self.canvas.tag_bind('ball', '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind('ball', '<ButtonRelease-1>', self.on_drag_release)
        self.canvas.tag_bind('ball', '<Button-3>', self.show_context_menu)  # 添加右键菜单事件

        # 拖拽相关变量
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False        
        
        # 功能窗口实例
        self.upload_window = None
        self.chat_window = None
        self.search_window = None
        
    def draw_ball(self):
        """绘制悬浮球"""
        center = self.ball_size // 2
        radius = center - 5
        
        # 清除之前的绘图
        self.canvas.delete('ball','half_ball')
        
        if self.is_on_edge:
            # 绘制半球形状（边缘吸附时）
            self._draw_half_ball(center, radius)
        else:
            # 绘制完整球体
            self._draw_full_ball(center, radius)
    
    
    def load_ball_image(self):
        """预加载并缓存球体图片"""
        try:
            image = Image.open("image/robot.png")
            image = image.resize((self.ball_size, self.ball_size), Image.Resampling.LANCZOS)
            self.ball_image = ImageTk.PhotoImage(image)

            image_left = Image.open("image/left_robot.png")
            image_left = image_left.resize((self.ball_size, self.ball_size), Image.Resampling.LANCZOS)
            self.ball_image_left = ImageTk.PhotoImage(image_left)

            image_right = Image.open("image/right_robot.png")
            image_right = image_right.resize((self.ball_size, self.ball_size), Image.Resampling.LANCZOS)
            self.ball_image_right = ImageTk.PhotoImage(image_right)

        except Exception as e:
            print(f"加载图片失败: {e}")
            self.ball_image = None
            self.ball_image_left = None
            self.ball_image_right = None
    def _draw_full_ball(self, center, radius):
        # 在画布中心显示图片
        self.canvas.create_image(center, center, image=self.ball_image, tags='ball')
    
    def _draw_half_ball(self, center, radius):
        # 在画布中心显示图片
        # 根据在边缘的位置决定绘制哪一半
        ball_x = self.ball.winfo_x()
        ball_y = self.ball.winfo_y()
        screen_width = self.ball.winfo_screenwidth()
        
        if ball_x <= 0:  # 左边缘
            # 绘制右半球
            self.canvas.create_image(center, center, image=self.ball_image_right, tags='half_ball')        
        elif ball_x >= screen_width - self.ball_size:  # 右边缘
            # 绘制左半球
            self.canvas.create_image(center, center, image=self.ball_image_left, tags='half_ball')
        else:
            # 默认绘制完整球体
            self._draw_full_ball(center, radius)

    def on_drag_release(self, event):
        """拖拽释放事件，处理边缘吸附"""
        self.is_dragging = False
        self.check_edge_snap()
    
    def check_edge_snap(self):
        """检查并处理边缘吸附"""
        ball_x = self.ball.winfo_x()
        ball_y = self.ball.winfo_y()
        screen_width = self.ball.winfo_screenwidth()
        screen_height = self.ball.winfo_screenheight()
        
        snap_threshold = 20  # 吸附阈值
        
        # 检查是否靠近边缘
        if ball_x <= snap_threshold:
            # 吸附到左边缘
            self.ball.geometry(f'{self.ball_size}x{self.ball_size}+0+{ball_y}')
            self.is_on_edge = True
        elif ball_x >= screen_width - self.ball_size - snap_threshold:
            # 吸附到右边缘
            self.ball.geometry(f'{self.ball_size}x{self.ball_size}+{screen_width - self.ball_size}+{ball_y}')
            self.is_on_edge = True
        else:
            self.is_on_edge = False
            
        # 更新球体绘制
        self.draw_ball()
    
    def on_hover_enter(self, event):
        """鼠标悬停进入，恢复完整球体"""
        if self.is_on_edge:
            self.is_on_edge = False
            self.draw_ball()
        if not self.is_menu_visible:
            self.show_menu()
    
    def on_hover_leave(self, event):
        """鼠标悬停离开"""
        # 延迟隐藏菜单，给用户时间移动到菜单上
        self.root.after(300, self.check_hide_menu)
        if self.should_restore_edge_state():
            self.root.after(350, self.restore_edge_state)  #new 稍微延迟于菜单检查
    
    def should_restore_edge_state(self):
        """判断是否应该恢复边缘状态"""
        #new 如果当前在拖拽中，不恢复边缘状态
        if self.is_dragging:
            return False
        # 如果不在边缘但应该是边缘状态，则需要恢复
        if not self.is_on_edge:
            ball_x = self.ball.winfo_x()
            screen_width = self.ball.winfo_screenwidth()
            snap_threshold = 20
            # 检查是否在屏幕边缘
            return (ball_x <= snap_threshold) or (ball_x >= screen_width - self.ball_size - snap_threshold)
        return False
    
    def restore_edge_state(self):
        """恢复边缘状态"""
        #new 再次检查是否仍在边缘
        if self.should_restore_edge_state() and not self.is_menu_visible:
            self.is_on_edge = True
            self.draw_ball()
    def check_hide_menu(self):
        """检查是否需要隐藏菜单"""
        if self.menu_window and self.is_menu_visible:
            # 检查鼠标是否在菜单或球体上
            x, y = self.root.winfo_pointerxy()
            ball_x = self.ball.winfo_rootx()
            ball_y = self.ball.winfo_rooty()
            menu_x = self.menu_window.winfo_rootx()
            menu_y = self.menu_window.winfo_rooty()
            
            # 如果鼠标不在球体或菜单区域，隐藏菜单
            if not ((ball_x <= x <= ball_x + self.ball_size and ball_y <= y <= ball_y + self.ball_size) or
                    (menu_x <= x <= menu_x + 200 and menu_y <= y <= menu_y + 120)):
                self.hide_menu()
                #new 检查是否需要恢复边缘状态
                if self.should_restore_edge_state():
                    self.is_on_edge = True
                    self.draw_ball()
    
    def show_menu(self):
        """显示功能菜单"""
        if self.menu_window:
            self.menu_window.destroy()
        
        self.menu_window = tk.Toplevel()
        self.menu_window.overrideredirect(True)
        self.menu_window.attributes('-topmost', True)
        self.menu_window.attributes('-alpha', 0.9)
        
        # 计算菜单位置
        ball_x = self.ball.winfo_x()
        ball_y = self.ball.winfo_y()
        if ball_x + self.ball_size + 200 > self.root.winfo_screenwidth():
            menu_x = ball_x - 200
        else:
            menu_x = ball_x + self.ball_size + 10
        # menu_x = ball_x + self.ball_size + 10
        menu_y = ball_y - 20
        
        self.menu_window.geometry(f'200x120+{menu_x}+{menu_y}')
        self.menu_window.configure(bg='#2C3E50')
        
        # 创建菜单按钮
        buttons_data = [
            ("📁 上传文件", self.open_upload_window),
            ("💬 智能问答", self.open_chat_window),
            ("🔍 智能检索", self.open_search_window)
        ]
        
        for i, (text, command) in enumerate(buttons_data):
            btn = tk.Button(self.menu_window, text=text, command=command,
                          bg='#34495E', fg='white', relief='flat',
                          font=('微软雅黑', 10), cursor='hand2')
            btn.pack(fill='x', padx=5, pady=2)
            
            # 添加悬停效果
            def on_enter(e, button=btn):
                button.config(bg='#5DADE2')
            def on_leave(e, button=btn):
                button.config(bg='#34495E')
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        
        self.is_menu_visible = True
        
        # 绑定菜单事件
        self.menu_window.bind('<Leave>', self.on_menu_leave)
    
    def on_menu_leave(self, event):
        """鼠标离开菜单"""
        self.root.after(300, self.check_hide_menu)
    
    def hide_menu(self):
        """隐藏菜单"""
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
        self.is_menu_visible = False

    def start_drag(self, event):
        """开始拖拽"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    def on_drag(self, event):
        """拖拽移动"""
        self.is_dragging = True
        self.is_on_edge = False  # 拖拽时暂时取消边缘状态
        self.draw_ball()  # 恢复完整球体
        
        x = self.ball.winfo_x() + (event.x - self.drag_start_x)
        y = self.ball.winfo_y() + (event.y - self.drag_start_y)
        
        # 限制移动范围在屏幕内
        screen_width = self.ball.winfo_screenwidth()
        screen_height = self.ball.winfo_screenheight()
        x = max(0, min(x, screen_width - self.ball_size))
        y = max(0, min(y, screen_height - self.ball_size))
        
        self.ball.geometry(f'{self.ball_size}x{self.ball_size}+{x}+{y}')
        
        # 拖拽时隐藏菜单
        if self.is_menu_visible:
            self.hide_menu()

    def open_upload_window(self):
        """打开上传文件窗口"""
        self.hide_menu()
        
        if self.upload_window and tk.Toplevel.winfo_exists(self.upload_window.window):
            self.upload_window.lift()
            return
        
        self.upload_window = AudioUploadWindow()
    
    def open_chat_window(self):
        """打开智能问答窗口"""
        self.hide_menu()
        
        if self.chat_window and tk.Toplevel.winfo_exists(self.chat_window.window):
            self.chat_window.lift()
            return
        
        self.chat_window = ChatWindow()
    
    def open_search_window(self):
        """打开智能检索窗口"""
        self.hide_menu()
        
        if self.search_window and tk.Toplevel.winfo_exists(self.search_window.window):
            self.search_window.lift()
            return
        
        self.search_window = SearchWindow()

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 隐藏功能菜单
        self.hide_menu()
        
        # 创建右键菜单
        context_menu = tk.Menu(self.ball, tearoff=0, bg='#2C3E50', fg='white', font=('微软雅黑', 10))
        context_menu.add_command(label="关闭悬浮球", command=self.close_floating_ball)
        
        # 在鼠标位置显示菜单
        try:
            context_menu.post(event.x_root, event.y_root)
        except:
            pass
        
        # 点击其他地方隐藏菜单
        def hide_context_menu(event=None):
            try:
                context_menu.unpost()
            except:
                pass
        
        # 绑定点击事件隐藏菜单
        self.ball.bind('<Button-1>', hide_context_menu)
        self.ball.bind('<Button-3>', hide_context_menu)

    def close_floating_ball(self):
        """关闭悬浮球"""
        try:
            self.ball.destroy()
        except:
            pass
        
        try:
            if self.menu_window:
                self.menu_window.destroy()
        except:
            pass
        
        # 如果有打开的子窗口，也一并关闭
        try:
            if self.upload_window and self.upload_window.window.winfo_exists():
                self.upload_window.window.destroy()
        except:
            pass
            
        try:
            if self.chat_window and self.chat_window.window.winfo_exists():
                self.chat_window.window.destroy()
        except:
            pass
            
        try:
            if self.search_window and self.search_window.window.winfo_exists():
                self.search_window.window.destroy()
        except:
            pass
        
        # 退出主循环
        try:
            self.root.quit()
        except:
            pass
        
    def run(self):
        """运行应用"""
        self.root.mainloop()