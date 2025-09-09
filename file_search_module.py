"""
文件搜索模块
负责在指定目录中搜索文件名和文件内容
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from pathlib import Path

class SearchWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("智能检索")
        self.window.geometry("700x600")
        self.window.attributes('-alpha', 0.95)
        self.window.configure(bg='#ECF0F1')
        
        self.search_directory = ""
        self.search_results = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置检索界面"""
        # 标题
        title_label = tk.Label(self.window, text="智能文件检索", 
                              font=('微软雅黑', 16, 'bold'),
                              bg='#ECF0F1', fg='#2C3E50')
        title_label.pack(pady=10)
        
        # 目录选择区域
        dir_frame = tk.Frame(self.window, bg='#ECF0F1')
        dir_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(dir_frame, text="搜索目录:", 
                font=('微软雅黑', 12),
                bg='#ECF0F1', fg='#2C3E50').pack(anchor='w')
        
        dir_select_frame = tk.Frame(dir_frame, bg='#ECF0F1')
        dir_select_frame.pack(fill='x', pady=5)
        
        self.dir_label = tk.Label(dir_select_frame, text="未选择目录",
                                 bg='white', relief='flat', bd=1,
                                 font=('微软雅黑', 10), anchor='w')
        self.dir_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        select_dir_btn = tk.Button(dir_select_frame, text="选择目录",
                                  command=self.select_directory,
                                  bg='#3498DB', fg='white',
                                  font=('微软雅黑', 10),
                                  relief='flat', cursor='hand2')
        select_dir_btn.pack(side='right')
        
        # 搜索区域
        search_frame = tk.Frame(self.window, bg='#ECF0F1')
        search_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(search_frame, text="搜索关键词:", 
                font=('微软雅黑', 12),
                bg='#ECF0F1', fg='#2C3E50').pack(anchor='w')
        
        search_input_frame = tk.Frame(search_frame, bg='#ECF0F1')
        search_input_frame.pack(fill='x', pady=5)
        
        self.search_entry = tk.Entry(search_input_frame,
                                   font=('微软雅黑', 12),
                                   relief='flat', bd=5)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', self.perform_search)
        
        search_btn = tk.Button(search_input_frame, text="搜索",
                             command=self.perform_search,
                             bg='#27AE60', fg='white',
                             font=('微软雅黑', 12),
                             relief='flat', cursor='hand2')
        search_btn.pack(side='right')
        
        # 搜索选项
        option_frame = tk.Frame(self.window, bg='#ECF0F1')
        option_frame.pack(pady=5, padx=20, fill='x')
        
        self.search_filename = tk.BooleanVar(value=True)
        self.search_content = tk.BooleanVar(value=False)
        self.case_sensitive = tk.BooleanVar(value=False)
        
        tk.Checkbutton(option_frame, text="搜索文件名",
                      variable=self.search_filename,
                      bg='#ECF0F1', font=('微软雅黑', 10)).pack(side='left')
        
        tk.Checkbutton(option_frame, text="搜索文件内容",
                      variable=self.search_content,
                      bg='#ECF0F1', font=('微软雅黑', 10)).pack(side='left', padx=(20, 0))
        
        tk.Checkbutton(option_frame, text="区分大小写",
                      variable=self.case_sensitive,
                      bg='#ECF0F1', font=('微软雅黑', 10)).pack(side='left', padx=(20, 0))
        
        # 文件类型过滤
        filter_frame = tk.Frame(self.window, bg='#ECF0F1')
        filter_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(filter_frame, text="文件类型:", 
                font=('微软雅黑', 10),
                bg='#ECF0F1', fg='#2C3E50').pack(side='left')
        
        self.file_type_var = tk.StringVar(value="所有文件")
        file_type_combo = ttk.Combobox(filter_frame, textvariable=self.file_type_var,
                                      values=["所有文件", "文本文件(.txt)", "文档文件(.doc,.docx,.pdf)", 
                                             "图片文件(.jpg,.png,.gif)", "音频文件(.mp3,.wav)", "视频文件(.mp4,.avi)"],
                                      state="readonly", width=20)
        file_type_combo.pack(side='left', padx=(10, 0))
        
        # 进度条和状态
        status_frame = tk.Frame(self.window, bg='#ECF0F1')
        status_frame.pack(pady=5, padx=20, fill='x')
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.status_label = tk.Label(status_frame, text="就绪", 
                                    bg='#ECF0F1', fg='#7F8C8D',
                                    font=('微软雅黑', 9))
        self.status_label.pack(side='left')
        
        # 结果显示区域
        result_frame = tk.Frame(self.window, bg='#ECF0F1')
        result_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        result_header = tk.Frame(result_frame, bg='#ECF0F1')
        result_header.pack(fill='x', pady=(0, 5))
        
        tk.Label(result_header, text="搜索结果:", 
                font=('微软雅黑', 12, 'bold'),
                bg='#ECF0F1', fg='#2C3E50').pack(side='left')
        
        self.result_count_label = tk.Label(result_header, text="", 
                                          font=('微软雅黑', 10),
                                          bg='#ECF0F1', fg='#7F8C8D')
        self.result_count_label.pack(side='right')
        
        # 创建树形视图显示结果
        tree_frame = tk.Frame(result_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('文件名', '路径', '大小', '修改时间', '类型')
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        column_widths = {'文件名': 200, '路径': 250, '大小': 80, '修改时间': 120, '类型': 60}
        for col in columns:
            self.result_tree.heading(col, text=col, command=lambda c=col: self.sort_results(c))
            self.result_tree.column(col, width=column_widths[col])
        
        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.result_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.result_tree.xview)
        
        self.result_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_selected_file)
        self.context_menu.add_command(label="打开文件夹", command=self.open_file_location)
        self.context_menu.add_command(label="复制路径", command=self.copy_file_path)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="文件属性", command=self.show_file_properties)
        
        # 绑定事件
        self.result_tree.bind('<Double-1>', self.open_selected_file)
        self.result_tree.bind('<Button-3>', self.show_context_menu)
        
        # 添加窗口关闭处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def select_directory(self):
        """选择搜索目录"""
        directory = filedialog.askdirectory(title="选择搜索目录")
        if directory:
            self.search_directory = directory
            self.dir_label.config(text=directory)
            self.status_label.config(text=f"已选择目录: {os.path.basename(directory)}")
    
    def perform_search(self, event=None):
        """执行搜索"""
        if not self.search_directory:
            messagebox.showwarning("提示", "请先选择搜索目录")
            return
        
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        # 清空之前的结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.search_results.clear()
        
        # 显示进度条
        self.progress.pack(side='right', padx=(10, 0))
        self.progress.start()
        self.status_label.config(text="搜索中...")
        
        def search():
            try:
                results = []
                file_count = 0
                
                for root, dirs, files in os.walk(self.search_directory):
                    for file in files:
                        file_count += 1
                        if file_count % 100 == 0:  # 每处理100个文件更新状态
                            self.window.after(0, lambda: self.status_label.config(text=f"已扫描 {file_count} 个文件..."))
                        
                        file_path = os.path.join(root, file)
                        
                        # 文件类型过滤
                        if not self.match_file_type(file_path):
                            continue
                        
                        match_found = False
                        match_reason = ""
                        
                        # 搜索文件名
                        if self.search_filename.get():
                            if self.match_text(file, keyword):
                                match_found = True
                                match_reason = "文件名匹配"
                        
                        # 搜索文件内容
                        if not match_found and self.search_content.get():
                            if self.is_text_file(file_path) and self.search_in_file(file_path, keyword):
                                match_found = True
                                match_reason = "内容匹配"
                        
                        if match_found:
                            file_info = self.get_file_info(file_path)
                            file_info['match_reason'] = match_reason
                            results.append(file_info)
                
                self.search_results = results
                self.window.after(0, lambda: self.show_results(results, file_count))
                
            except Exception as e:
                self.window.after(0, lambda: self.show_error(str(e)))
        
        threading.Thread(target=search, daemon=True).start()
    
    def match_file_type(self, file_path):
        """检查文件类型是否匹配过滤条件"""
        file_type = self.file_type_var.get()
        if file_type == "所有文件":
            return True
        
        ext = Path(file_path).suffix.lower()
        type_mapping = {
            "文本文件(.txt)": ['.txt'],
            "文档文件(.doc,.docx,.pdf)": ['.doc', '.docx', '.pdf', '.rtf'],
            "图片文件(.jpg,.png,.gif)": ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            "音频文件(.mp3,.wav)": ['.mp3', '.wav', '.flac', '.aac'],
            "视频文件(.mp4,.avi)": ['.mp4', '.avi', '.mov', '.mkv']
        }
        
        return ext in type_mapping.get(file_type, [])
    
    def match_text(self, text, keyword):
        """文本匹配"""
        if self.case_sensitive.get():
            return keyword in text
        else:
            return keyword.lower() in text.lower()
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            size_bytes = stat.st_size
            
            # 格式化文件大小
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': size_str,
                'size_bytes': size_bytes,
                'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime)),
                'modified_timestamp': stat.st_mtime,
                'type': Path(file_path).suffix.upper().lstrip('.')
            }
        except:
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': "未知",
                'size_bytes': 0,
                'modified': "未知",
                'modified_timestamp': 0,
                'type': Path(file_path).suffix.upper().lstrip('.')
            }
    
    def is_text_file(self, file_path):
        """检查是否为文本文件"""
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.xml', '.json', 
                          '.md', '.log', '.ini', '.cfg', '.conf', '.yml', '.yaml',
                          '.csv', '.sql', '.sh', '.bat', '.c', '.cpp', '.java'}
        return Path(file_path).suffix.lower() in text_extensions
    
    def search_in_file(self, file_path, keyword):
        """在文件内容中搜索关键词"""
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                        return self.match_text(content, keyword)
                except UnicodeDecodeError:
                    continue
            return False
        except:
            return False
    
    def show_results(self, results, total_scanned):
        """显示搜索结果"""
        self.progress.stop()
        self.progress.pack_forget()
        
        if not results:
            self.status_label.config(text=f"搜索完成，扫描了 {total_scanned} 个文件，未找到匹配项")
            self.result_count_label.config(text="无结果")
            return
        
        for result in results:
            self.result_tree.insert('', 'end', values=(
                result['name'],
                result['path'],
                result['size'],
                result['modified'],
                result['type']
            ))
        
        self.status_label.config(text=f"搜索完成，扫描了 {total_scanned} 个文件")
        self.result_count_label.config(text=f"找到 {len(results)} 个匹配文件")
    
    def show_error(self, error):
        """显示错误信息"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="搜索出错")
        messagebox.showerror("搜索错误", f"搜索过程中出现错误：{error}")
    
    def sort_results(self, column):
        """按列排序结果"""
        if not self.search_results:
            return
        
        # 根据列名确定排序键
        sort_key_map = {
            '文件名': 'name',
            '路径': 'path', 
            '大小': 'size_bytes',
            '修改时间': 'modified_timestamp',
            '类型': 'type'
        }
        
        sort_key = sort_key_map.get(column, 'name')
        
        # 排序
        self.search_results.sort(key=lambda x: x.get(sort_key, ''), reverse=False)
        
        # 更新显示
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        for result in self.search_results:
            self.result_tree.insert('', 'end', values=(
                result['name'],
                result['path'],
                result['size'],
                result['modified'],
                result['type']
            ))
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        selection = self.result_tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)
    
    def open_selected_file(self, event=None):
        """打开选中的文件"""
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            file_path = item['values'][1]
            self.open_file(file_path)
    
    def open_file_location(self):
        """打开文件所在文件夹"""
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            file_path = item['values'][1]
            folder_path = os.path.dirname(file_path)
            self.open_file(folder_path)
    
    def copy_file_path(self):
        """复制文件路径到剪贴板"""
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            file_path = item['values'][1]
            self.window.clipboard_clear()
            self.window.clipboard_append(file_path)
            self.status_label.config(text="文件路径已复制到剪贴板")
    
    def show_file_properties(self):
        """显示文件属性"""
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            file_path = item['values'][1]
            
            try:
                stat = os.stat(file_path)
                info = f"""文件属性:

文件名: {os.path.basename(file_path)}
完整路径: {file_path}
文件大小: {item['values'][2]}
修改时间: {item['values'][3]}
文件类型: {item['values'][4]}
创建时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_ctime))}
访问时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_atime))}"""
                
                messagebox.showinfo("文件属性", info)
            except Exception as e:
                messagebox.showerror("错误", f"无法获取文件属性：{str(e)}")
    
    def open_file(self, file_path):
        """打开文件或文件夹"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    os.system(f'open "{file_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件：{str(e)}")
    
    def on_closing(self):
        """窗口关闭处理"""
        self.window.destroy()
