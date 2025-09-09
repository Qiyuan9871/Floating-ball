"""
智能问答模块
负责与用户进行智能对话和问答
"""
import tkinter as tk
from tkinter import scrolledtext
import threading
import time

class ChatWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("智能问答")
        self.window.geometry("600x500")
        self.window.attributes('-alpha', 0.95)
        self.window.configure(bg='#ECF0F1')
        
        self.chat_history = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置聊天界面"""
        # 标题
        title_label = tk.Label(self.window, text="智能问答助手", 
                              font=('微软雅黑', 16, 'bold'),
                              bg='#ECF0F1', fg='#2C3E50')
        title_label.pack(pady=10)
        
        # 聊天记录区域
        chat_frame = tk.Frame(self.window, bg='#ECF0F1')
        chat_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                height=13,
                                font=('微软雅黑', 10),
                                bg='white',
                                relief='flat',
                                bd=1,
                                state='disabled')
        self.chat_display.pack(fill='both', expand=True)
        
        # 输入区域
        input_frame = tk.Frame(self.window, bg='#ECF0F1')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        self.input_entry = tk.Entry(input_frame,
                        font=('微软雅黑', 10),
                        relief='flat',
                        bd=5)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        
        send_btn = tk.Button(input_frame, text="发送",
                           command=self.send_message,
                           bg='#27AE60', fg='white',
                           font=('微软雅黑', 10),
                           relief='flat', cursor='hand2')
        send_btn.pack(side='left', padx=(0, 10))
        
        # 功能按钮区域
        button_frame = tk.Frame(self.window, bg='#ECF0F1')
        button_frame.pack(pady=10, padx=20, fill='x')
        
        clear_btn = tk.Button(button_frame, text="清空对话",
                             command=self.clear_chat,
                             bg='#E74C3C', fg='white',
                             font=('微软雅黑', 10),
                             relief='flat', cursor='hand2')
        clear_btn.pack(side='left', padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="保存对话",
                            command=self.save_chat,
                            bg='#F39C12', fg='white',
                            font=('微软雅黑', 10),
                            relief='flat', cursor='hand2')
        save_btn.pack(side='left')
        
        # 添加欢迎消息
        self.add_message("助手", "您好！我是智能问答助手，有什么问题可以问我哦～\n\n请随时向我提问！")
        
        # 添加窗口关闭处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def add_message(self, sender, message):
        """添加消息到聊天记录"""
        self.chat_display.config(state='normal') # 允许编辑
        
        timestamp = time.strftime('%H:%M:%S')
        
        if sender == "用户":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 您: {message}\n")
            self.chat_display.tag_add("user", "end-2l", "end-1l")
            self.chat_display.tag_config("user", foreground="#2980B9", font=('微软雅黑', 10, 'bold'))
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 助手: {message}\n")
            self.chat_display.tag_add("assistant", "end-2l", "end-1l")
            self.chat_display.tag_config("assistant", foreground="#27AE60", font=('微软雅黑', 10))
        
        self.chat_history.append({"sender": sender, "message": message, "timestamp": timestamp}) # 保存到内存
        
        self.chat_display.config(state='disabled') # 禁止编辑
        self.chat_display.see(tk.END) # 滚动到最后
    
    def send_message(self, event=None):
        """发送消息"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.add_message("用户", message)
        self.input_entry.delete(0, tk.END) # 清空输入框
        
        # AI回复
        self.generate_response(message)

    def generate_response(self, user_message):
        """生成AI回复（调用Dify API实现智能回答）"""
        def respond():
            import requests
            import json
            import time
            
            # Dify API配置
            api_key = "app-sa19QdxtZJsz6I1rI7RVNsZ2"  # 请替换为实际的API密钥
            api_url = "http://localhost/v1/chat-messages"
            
            # 构建请求数据
            payload = {
                "inputs": {},
                "query": user_message,
                "response_mode": "streaming",
                "conversation_id": "",
                "user": "cyn"
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                # 调用Dify API，启用流式响应
                response = requests.post(api_url, headers=headers, 
                                    json=payload, stream=True)
                
                if response.status_code == 200:
                    # 初始化时添加一个空的助手消息
                    self.window.after(0, lambda: self.add_message("助手", ""))
                    # 流式处理响应
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            # 处理SSE数据
                            if decoded_line.startswith("data: "):
                                try:
                                    data = json.loads(decoded_line[6:])  # 去掉"data: "前缀
                                    if 'answer' in data:
                                        # 直接获取answer字段作为新增内容
                                        new_content = data['answer']
                                        # 实时更新显示（传入新增内容）
                                        self.window.after(0, lambda text=new_content: 
                                                        self.append_to_last_message("助手", text))
                                        # 添加小延迟以获得更好的流式效果
                                        time.sleep(0.02)
                                except json.JSONDecodeError:
                                    continue
                else:
                    error_msg = f"API调用失败，状态码：{response.status_code}"
                    self.window.after(0, lambda: self.append_to_last_message("助手", error_msg))
                    
            except Exception as e:
                error_msg = f"请求过程中出现错误：{str(e)}"
                self.window.after(0, lambda: self.append_to_last_message("助手", error_msg))
        
        threading.Thread(target=respond, daemon=True).start()

    def append_to_last_message(self, sender, new_text):
        """向最后一条消息追加内容（用于流式输出）"""
        if not self.chat_history:  # 没有聊天记录
            return
        
        # 更新内存中的聊天记录
        last_msg = self.chat_history[-1]
        if last_msg["sender"] == sender:
            last_msg["message"] += new_text
        
        # 更新显示界面
        self.chat_display.config(state='normal')
        
        # 插入新文本
        self.chat_display.insert("end-1c", new_text)
        
        # 重新为助手消息应用标签样式
        if sender == "助手":
            # 获取最后一段消息的起始和结束位置
            last_line_start = self.chat_display.index("end-2l linestart")
            last_line_end = self.chat_display.index("end-1c")
            # 为最后一行应用助手标签样式
            self.chat_display.tag_add("assistant", last_line_start, last_line_end)
            self.chat_display.tag_config("assistant", foreground="#27AE60", font=('微软雅黑', 10))
        elif sender == "用户":
            # 为最后一行应用用户标签样式
            self.chat_display.tag_add("user", "end-2l", "end-1l")
            self.chat_display.tag_config("user", foreground="#2980B9", font=('微软雅黑', 10, 'bold'))
        
        self.chat_display.config(state='disabled')  # 禁止编辑
        self.chat_display.see(tk.END)  # 滚动到最后

    def clear_chat(self):
        """清空聊天记录"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.chat_history.clear()
        
        # 重新添加欢迎消息
        self.add_message("助手", "对话已清空！有什么新问题可以问我哦～")
    
    def save_chat(self):
        """保存聊天记录"""
        if not self.chat_history:
            tk.messagebox.showinfo("提示", "暂无聊天记录可保存")
            return
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存聊天记录"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("智能问答聊天记录\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for chat in self.chat_history:
                        f.write(f"[{chat['timestamp']}] {chat['sender']}: {chat['message']}\n\n")
                
                tk.messagebox.showinfo("成功", f"聊天记录已保存到：\n{file_path}")
            except Exception as e:
                tk.messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def on_closing(self):
        """窗口关闭处理"""
        self.window.destroy()