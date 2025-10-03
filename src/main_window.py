#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QMenuBar, QMenu, QAction, QFileDialog, QTextBrowser,
                             QLabel, QStatusBar, QSplitter, QListWidget, 
                             QMessageBox, QFrame, QPushButton, QShortcut, QApplication,
                             QDesktopWidget)  # 添加QDesktopWidget导入
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QKeySequence, QWheelEvent, QCursor

from document_reader import DocumentReader
from settings_manager import SettingsManager
from tray_manager import TrayManager
from settings_dialog import SettingsDialog
from mode_manager import ModeManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化管理器
        self.settings_manager = SettingsManager()
        self.document_reader = DocumentReader()
        self.tray_manager = TrayManager(self)
        self.mode_manager = ModeManager(self)
        
        # 当前文档相关
        self.current_file = None
        self.recent_files = []
        
        # 窗口拖拽相关
        self.drag_position = None
        
        # 界面状态控制
        self.file_list_visible = True
        self.minimal_mode = False
        self.current_font_size = 12
        
        # 窗口边框调整大小相关
        self._resize_border_width = 15  # 边框宽度，设置为15px以便更容易检测
        print(f"[初始化] resize_border_width设置为: {self._resize_border_width}")
        self._last_border_width_set_reason = "初始化"
        self._border_width_history = [("初始化", self._resize_border_width)]
        self.resizing = False
        self.resize_direction = None
        self.resize_start_pos = None  # 初始化调整开始位置
        self.resize_start_geometry = None  # 初始化调整开始几何
        
        # 初始化界面
        self.init_ui()
        self.init_shortcuts()
        self.load_settings()
        
        # 老板键定时器
        self.boss_key_timer = QTimer()
        self.boss_key_timer.timeout.connect(self.show_window)
        
        # 自动保存阅读进度定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_reading_progress)
        self.auto_save_timer.start(30000)  # 每30秒自动保存一次
        
        # 重要：确保鼠标跟踪在所有组件初始化完成后启用
        print("[主程序启动] 开始配置鼠标跟踪和事件过滤器...")
        self.setup_mouse_tracking()
        
    @property
    def resize_border_width(self):
        print(f"[属性获取] resize_border_width当前值: {self._resize_border_width}")
        return self._resize_border_width
    
    @resize_border_width.setter
    def resize_border_width(self, value):
        import traceback
        stack = traceback.format_stack()
        reason = stack[-2].split('\n')[0] if stack else '未知'
        self._resize_border_width = value
        self._border_width_history.append((reason, value))
        print(f"[属性设置] resize_border_width设置为: {value}, 原因: {reason}")
        # 打印最近的几次设置历史
        if len(self._border_width_history) > 1:
            print(f"[属性设置历史] 最近5次设置:")
            for i, (r, v) in enumerate(self._border_width_history[-5:]):
                print(f"  {i+1}. 值={v}, 原因={r}")
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("技术文档阅读器 - Technical Document Reader")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置窗口属性，实现背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 移除窗口边框
        
        # 启用鼠标跟踪，确保能接收到鼠标移动事件 - 关键修复
        self.setMouseTracking(True)
        print("[初始化] 主窗口鼠标跟踪已启用")
        
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
            }
        """)
        # 为中央部件启用鼠标跟踪和事件过滤器 - 关键修复
        central_widget.setMouseTracking(True)
        central_widget.installEventFilter(self)
        print("[初始化] 中央部件鼠标跟踪和事件过滤器已配置")
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 设置为15px，与resize_border_width一致
        main_layout.setSpacing(2)
        
        # 添加标题栏
        self.create_title_bar(main_layout)
        
        # 创建菜单栏容器
        self.menu_container = QWidget()
        self.menu_container.setFixedHeight(35)  # 设置固定高度
        main_layout.addWidget(self.menu_container)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        # 为分割器启用鼠标跟踪和事件过滤器 - 关键修复
        self.splitter.setMouseTracking(True)
        self.splitter.installEventFilter(self)
        print("[初始化] 分割器鼠标跟踪和事件过滤器已配置")
        main_layout.addWidget(self.splitter)
        
        # 左侧文档列表
        self.create_file_list_panel(self.splitter)
        
        # 右侧阅读区域
        self.create_reading_panel(self.splitter)
        
        # 设置分割器比例
        self.splitter.setSizes([200, 800])
        
        # 创建菜单栏（现在会正确放在标题栏下方）
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 确保在初始化完成后设置正确的鼠标跟踪
        self.setup_mouse_tracking()
        
    def create_file_list_panel(self, parent):
        """创建文件列表面板"""
        self.file_panel = QFrame()
        self.file_panel.setMaximumWidth(250)
        self.file_panel.setMinimumWidth(150)
        # 为文件面板启用鼠标跟踪 - 关键修复
        self.file_panel.setMouseTracking(True)
        # 为文件面板安装事件过滤器确保鼠标事件传播 - 关键修复
        self.file_panel.installEventFilter(self)
        print("[初始化] 文件面板鼠标跟踪和事件过滤器已配置")
        self.file_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(240, 240, 240, 200);
                border: 1px solid rgba(200, 200, 200, 100);
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self.file_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题栏（包含收缩按钮）
        title_layout = QHBoxLayout()
        title_label = QLabel("文档列表")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                padding: 5px;
                background-color: rgba(255, 255, 255, 0);
                color: #333333;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 收缩按钮
        self.collapse_btn = QPushButton("«")
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 130, 180, 150);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 200);
            }
        """)
        self.collapse_btn.setToolTip("收缩/展开文档列表")
        self.collapse_btn.clicked.connect(self.toggle_file_list_collapse)
        title_layout.addWidget(self.collapse_btn)
        
        layout.addLayout(title_layout)
        
        # 文档列表
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(200, 200, 200, 100);
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: rgba(70, 130, 180, 150);
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(70, 130, 180, 80);
            }
        """)
        self.file_list.itemClicked.connect(self.on_file_selected)
        # 为文件列表启用鼠标跟踪和事件过滤器 - 关键修复
        self.file_list.setMouseTracking(True)
        self.file_list.installEventFilter(self)
        print("[初始化] 文件列表鼠标跟踪和事件过滤器已配置")
        layout.addWidget(self.file_list)
        
        parent.addWidget(self.file_panel)
        
    def create_title_bar(self, layout):
        """创建自定义标题栏"""
        self.title_bar = QWidget()  # 保存为实例属性以便在极简模式中隐藏
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(70, 130, 180, 255);  /* 完全不透明 */
                border-radius: 5px;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 标题文本
        self.title_label = QLabel("技术文档阅读器")  # 保存为实例属性
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 控制按钮
        
        # 最小化按钮
        self.min_btn = QPushButton("-")
        self.min_btn.setFixedSize(25, 25)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
                color: #333333;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.min_btn.clicked.connect(self.showMinimized)
        self.min_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时的光标
        self.min_btn.setToolTip("最小化")
        title_layout.addWidget(self.min_btn)
        
        # 最大化按钮
        self.max_btn = QPushButton("□")  # 使用空心正方形表示最大化
        self.max_btn.setFixedSize(25, 25)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
                color: #333333;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.max_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时的光标
        self.max_btn.setToolTip("最大化")
        title_layout.addWidget(self.max_btn)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                border: none;
                border-radius: 12px;
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff3b30;
            }
            QPushButton:pressed {
                background-color: #e03020;
            }
        """)
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时的光标
        close_btn.setToolTip("关闭")
        title_layout.addWidget(close_btn)
        
        layout.addWidget(self.title_bar)
        
    def toggle_maximize(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")  # 空心正方形：最大化
            self.max_btn.setToolTip("最大化")
        else:
            self.showMaximized()
            self.max_btn.setText("■")  # 实心正方形：还原
            self.max_btn.setToolTip("还原")
        
        # 确保状态栏在最大化后正确显示
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.setVisible(True)
            self.status_bar.raise_()
        
    def create_reading_panel(self, parent):
        """创建阅读面板"""
        reading_panel = QFrame()
        reading_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0);
                border: none;
            }
        """)
        layout = QVBoxLayout(reading_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 文档标题
        self.doc_title = QLabel("欢迎使用技术文档阅读器")
        self.doc_title.setAlignment(Qt.AlignCenter)
        self.doc_title.setStyleSheet("""
            QLabel {
                font-size: 16px; 
                font-weight: bold; 
                padding: 10px;
                background-color: rgba(255, 255, 255, 0);
                color: #333333;
            }
        """)
        layout.addWidget(self.doc_title)
        
        # 阅读区域
        self.reading_area = QTextBrowser()
        # 禁用横向滚动条，启用自动换行
        self.reading_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.reading_area.setLineWrapMode(QTextBrowser.WidgetWidth)
        self.reading_area.setWordWrapMode(1)  # 1 = WordWrap
        self.reading_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 255);  /* 完全不透明 */
                border: 1px solid rgba(200, 200, 200, 255);  /* 完全不透明边框 */
                border-radius: 8px;
                padding: 15px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                color: #333333;
            }
            QScrollBar:vertical {
                background-color: rgba(240, 240, 240, 255);  /* 完全不透明 */
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(180, 180, 180, 255);  /* 完全不透明 */
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        self.reading_area.setPlainText("请选择要阅读的文档...\n\n支持的格式：\n- PDF文件 (.pdf)\n- Markdown文件 (.md)\n- 文本文件 (.txt)")
        
        # 为阅读区域安装事件过滤器支持Ctrl+滚轮缩放
        self.reading_area.installEventFilter(self)
        
        # 启用鼠标跟踪，确保边框拖拽功能正常 - 关键修复
        self.reading_area.setMouseTracking(True)
        print("[初始化] 阅读区域鼠标跟踪已启用")
        
        # 设置右键菜单策略
        self.reading_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reading_area.customContextMenuRequested.connect(self.show_context_menu)
        
        # 重要：确保阅读区域不拦截鼠标移动事件，让父窗口处理边框检测
        # 保持False让事件正常传播到主窗口
        self.reading_area.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 为阅读区域安装事件过滤器，确保鼠标事件能传播到主窗口 - 关键修复
        self.reading_area.installEventFilter(self)
        print("[初始化] 阅读区域事件过滤器已安装")
        
        layout.addWidget(self.reading_area)
        
        parent.addWidget(reading_panel)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        # 不使用系统菜单栏，而是在菜单容器中创建自定义菜单
        menu_layout = QHBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(10, 2, 10, 2)
        menu_layout.setSpacing(15)
        
        # 创建菜单按钮
        self.create_menu_button("文件(&F)", self.create_file_menu, menu_layout)
        self.create_menu_button("视图(&V)", self.create_view_menu, menu_layout)
        self.create_menu_button("设置(&S)", self.create_settings_menu, menu_layout)
        self.create_menu_button("帮助(&H)", self.create_help_menu, menu_layout)
        
        menu_layout.addStretch()  # 按钮左对齐
        
    def create_menu_button(self, text, menu_func, layout):
        """创建菜单按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px 10px;
                color: #333333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 100);
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: rgba(70, 130, 180, 150);
            }
        """)
        
        menu = menu_func()
        btn.setMenu(menu)
        layout.addWidget(btn)
        
    def create_file_menu(self):
        """创建文件菜单"""
        menu = QMenu(self)
        
        open_action = QAction("打开文档(&O)", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_document)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        recent_menu = menu.addMenu("最近文档(&R)")
        self.recent_menu = recent_menu
        
        menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        return menu
        
    def create_view_menu(self):
        """创建视图菜单"""
        menu = QMenu(self)
        
        stay_on_top_action = QAction("始终置顶(&T)", self)
        stay_on_top_action.setCheckable(True)
        stay_on_top_action.setShortcut("Ctrl+T")
        stay_on_top_action.triggered.connect(self.toggle_stay_on_top)
        menu.addAction(stay_on_top_action)
        self.stay_on_top_action = stay_on_top_action
        
        menu.addSeparator()
        
        toggle_file_list_action = QAction("切换文档列表(&L)", self)
        toggle_file_list_action.setShortcut("F2")
        toggle_file_list_action.triggered.connect(self.toggle_file_list)
        menu.addAction(toggle_file_list_action)
        
        minimal_mode_action = QAction("极简模式(&M)", self)
        minimal_mode_action.setShortcut("F3")
        minimal_mode_action.triggered.connect(self.toggle_minimal_mode)
        menu.addAction(minimal_mode_action)
        
        menu.addSeparator()
        
        fullscreen_action = QAction("全屏(&F)", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        menu.addAction(fullscreen_action)
        
        return menu
        
    def create_settings_menu(self):
        """创建设置菜单"""
        menu = QMenu(self)
        
        preferences_action = QAction("偏好设置(&P)", self)
        preferences_action.triggered.connect(self.open_preferences)
        menu.addAction(preferences_action)
        
        return menu
        
    def create_help_menu(self):
        """创建帮助菜单"""
        menu = QMenu(self)
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        return menu
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(240, 240, 240, 255);
                border-top: 1px solid rgba(200, 200, 200, 255);
                padding: 2px;
                height: 20px;
                color: #333333;
            }
        """)
        # 为状态栏启用鼠标跟踪和事件过滤器，确保下边框拖拽正常工作 - 关键修复
        self.status_bar.setMouseTracking(True)
        self.status_bar.installEventFilter(self)
        print("[初始化] 状态栏鼠标跟踪和事件过滤器已配置")
        self.setStatusBar(self.status_bar)
        
        # 显示就绪状态
        self.status_bar.showMessage("就绪")
        
    def init_shortcuts(self):
        """初始化快捷键"""
        # 老板键 - 隐藏窗口
        boss_key = QAction(self)
        boss_key.setShortcut("Ctrl+Shift+H")
        boss_key.triggered.connect(self.boss_key_pressed)
        self.addAction(boss_key)
        
        # 按照用户要求，字体大小调整必须在偏好设置中进行，移除Ctrl+=和Ctrl+-快捷键
        
        # 快速最小化到托盘
        minimize_to_tray = QAction(self)
        minimize_to_tray.setShortcut("Ctrl+M")
        minimize_to_tray.triggered.connect(self.minimize_to_tray)
        self.addAction(minimize_to_tray)
        
        # 切换文档列表显示 - 注释掉重复的快捷键绑定，使用菜单中的绑定
        # toggle_file_list = QAction(self)
        # toggle_file_list.setShortcut("F2")
        # toggle_file_list.triggered.connect(self.toggle_file_list)
        # self.addAction(toggle_file_list)
        
        # 极简模式 - 注释掉重复的快捷键绑定，使用菜单中的绑定
        # minimal_mode = QAction(self)
        # minimal_mode.setShortcut("F3")
        # minimal_mode.triggered.connect(self.toggle_minimal_mode)
        # self.addAction(minimal_mode)
        
    def open_document(self):
        """打开文档"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文档",
            "",
            "支持的文档 (*.pdf *.md *.txt);;PDF文件 (*.pdf);;Markdown文件 (*.md);;文本文件 (*.txt)"
        )
        
        if file_path:
            self.load_document(file_path)
            
    def load_document(self, file_path):
        """加载文档"""
        try:
            # 先保存当前文档的阅读进度
            if self.current_file:
                self.save_reading_progress_on_change()
            
            # 读取文档内容
            content = self.document_reader.read_document(file_path)
            
            if content is not None:
                self.current_file = file_path
                
                # 根据文件类型设置内容
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext == '.md':
                    # Markdown文件使用HTML显示
                    self.reading_area.setHtml(content)
                else:
                    # 其他文件使用纯文本显示
                    self.reading_area.setPlainText(content)
                    
                self.doc_title.setText(os.path.basename(file_path))
                
                # 添加到文档列表
                self.add_to_file_list(file_path)
                
                # 添加到最近文档
                self.add_to_recent_files(file_path)
                
                # 恢复阅读进度
                self.restore_reading_progress()
                
                self.status_bar.showMessage(f"已加载: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "错误", "无法读取文档内容")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载文档时出错: {str(e)}")
            
    def add_to_file_list(self, file_path):
        """添加到文件列表"""
        file_name = os.path.basename(file_path)
        
        # 检查是否已存在
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == file_path:
                print(f"文档已存在于列表中: {file_name}")
                return
                
        # 添加新项目
        item = self.file_list.addItem(file_name)
        self.file_list.item(self.file_list.count() - 1).setData(Qt.UserRole, file_path)
        print(f"添加文档到列表: {file_name}")
        
    def add_to_recent_files(self, file_path):
        """添加到最近文档"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            
        self.recent_files.insert(0, file_path)
        
        # 限制最近文档数量
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
            
        self.update_recent_menu()
        
        # 立即保存最近文档列表到设置中
        current_settings = self.settings_manager.load_settings()
        current_settings['recent_files'] = self.recent_files
        self.settings_manager.save_settings(current_settings)
        print(f"保存最近文档列表: {len(self.recent_files)} 个文档")
        
    def update_recent_menu(self):
        """更新最近文档菜单"""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(lambda checked, path=file_path: self.load_document(path))
            self.recent_menu.addAction(action)
            
    def on_file_selected(self, item):
        """文件列表选择事件"""
        file_path = item.data(Qt.UserRole)
        if file_path and file_path != self.current_file:
            self.load_document(file_path)
            
    def boss_key_pressed(self):
        """老板键按下"""
        if self.isVisible():
            self.hide()
            self.status_bar.showMessage("已隐藏窗口")
            # 3秒后显示提示
            self.boss_key_timer.start(3000)
        else:
            self.show_window()
            
    def show_window(self):
        """显示窗口"""
        self.boss_key_timer.stop()
        self.show()
        self.raise_()
        self.activateWindow()
        self.status_bar.showMessage("窗口已恢复")
        
    def toggle_stay_on_top(self, checked):
        """切换置顶状态"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def zoom_in(self):
        """放大字体"""
        font = self.reading_area.font()
        size = font.pointSize()
        if size <= 0:  # 防止字体大小为0或负数
            size = 12  # 设置默认字体大小
        if size < 72:
            new_size = size + 1
            font.setPointSize(new_size)
            self.reading_area.setFont(font)
            self.current_font_size = new_size
            
    def zoom_out(self):
        """缩小字体"""
        font = self.reading_area.font()
        size = font.pointSize()
        if size <= 0:  # 防止字体大小为0或负数
            size = 12  # 设置默认字体大小
        if size > 6:
            new_size = size - 1
            font.setPointSize(new_size)
            self.reading_area.setFont(font)
            self.current_font_size = new_size
            
    def open_preferences(self):
        """打开偏好设置"""
        try:
            dialog = SettingsDialog(self, self.settings_manager.load_settings())
            dialog.settings_changed.connect(self.apply_new_settings)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开设置对话框时出错: {str(e)}")
            
    def apply_new_settings(self, settings):
        """应用新设置"""
        try:
            # 应用透明度
            opacity = settings.get('opacity', 1.0)
            if isinstance(opacity, str):
                opacity = float(opacity)
            self.setWindowOpacity(opacity)
            
            # 应用字体设置
            font_family = settings.get('font_family', 'Microsoft YaHei')
            font_size = settings.get('font_size', 12)
            
            # 处理字体大小的类型转换和验证
            if isinstance(font_size, str):
                try:
                    font_size = int(font_size)
                except (ValueError, TypeError):
                    font_size = 12
            
            # 验证字体大小的有效性
            if font_size <= 0 or font_size > 72:
                font_size = 12
                
            print(f"应用字体设置: {font_family}, 大小: {font_size}")
            
            font = QFont(font_family, font_size)
            self.reading_area.setFont(font)
            self.current_font_size = font_size
            
            # 在极简模式下也需要更新字体大小
            if self.minimal_mode:
                # 更新极简模式下的字体大小 - 使用0-100%范围
                ui_opacity_percent = settings.get('minimal_ui_opacity', 20)
                text_opacity_percent = settings.get('minimal_text_opacity', 80)
                
                # 确保透明度值在有效范围内
                ui_opacity_percent = max(0, min(100, int(ui_opacity_percent) if ui_opacity_percent else 20))
                text_opacity_percent = max(0, min(100, int(text_opacity_percent) if text_opacity_percent else 80))
                
                # 转换为255范围的alpha值
                ui_alpha = int(ui_opacity_percent * 255 / 100)
                text_alpha = int(text_opacity_percent * 255 / 100)
                
                # 重新应用极简模式样式（包含新的字体大小），并禁用横向滚动条
                self.reading_area.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: rgba(255, 255, 255, {text_alpha});
                        border: none;
                        border-radius: 8px;
                        padding: 15px;
                        font-family: '{font_family}';
                        font-size: {font_size}px;
                        color: rgba(51, 51, 51, {min(255, text_alpha + 55)};
                    }}
                    QScrollBar:vertical {{
                        background-color: rgba(240, 240, 240, {ui_alpha});
                        width: 8px;
                        border-radius: 4px;
                    }}
                    QScrollBar::handle:vertical {{
                        background-color: rgba(180, 180, 180, {min(255, ui_alpha + 50)};
                        border-radius: 4px;
                        min-height: 20px;
                    }}
                    QScrollBar:horizontal {{
                        height: 0px;
                    }}
                """)
            else:
                # 正常模式下更新字体大小，并禁用横向滚动条
                self.reading_area.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: rgba(255, 255, 255, 220);
                        border: 1px solid rgba(200, 200, 200, 100);
                        border-radius: 8px;
                        padding: 15px;
                        font-family: '{font_family}';
                        font-size: {font_size}px;
                        color: #333333;
                    }}
                    QScrollBar:vertical {{
                        background-color: rgba(240, 240, 240, 150);
                        width: 12px;
                        border-radius: 6px;
                    }}
                    QScrollBar::handle:vertical {{
                        background-color: rgba(180, 180, 180, 200);
                        border-radius: 6px;
                        min-height: 20px;
                    }}
                    QScrollBar:horizontal {{
                        height: 0px;
                    }}
                """)
            
            # 应用颜色设置
            bg_color = settings.get('bg_color', '#ffffff')
            text_color = settings.get('text_color', '#000000')
            self.apply_colors(bg_color, text_color)
            
            # 应用置顶设置
            stay_on_top = settings.get('stay_on_top', False)
            self.stay_on_top_action.setChecked(stay_on_top)
            self.toggle_stay_on_top(stay_on_top)
            
            # 保存设置
            self.settings_manager.save_settings(settings)
            
            self.status_bar.showMessage("设置已应用")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用设置时出错: {str(e)}")
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "技术文档阅读器 v1.0.0\n\n"
                         "一个专业的文档阅读器\n"
                         "支持PDF、Markdown、TXT格式\n\n"
                         "作者: Qoder AI")
        
    def load_settings(self):
        """加载设置"""
        settings = self.settings_manager.load_settings()
        
        # 应用窗口透明度
        opacity = settings.get('opacity', 1.0)
        if isinstance(opacity, str):
            try:
                opacity = float(opacity)
            except (ValueError, TypeError):
                opacity = 1.0
        # 确保透明度值在有效范围内
        opacity = max(0.1, min(1.0, opacity))
        self.setWindowOpacity(opacity)
        
        # 应用字体设置 - 优先使用用户配置的字体，确保启动时生效
        font_family = settings.get('font_family', 'Microsoft YaHei')
        font_size = settings.get('font_size', 16)  # 默认16px，避免无效值
        
        # 处理字体大小的类型转换和验证
        if isinstance(font_size, str):
            try:
                font_size = int(font_size)
            except (ValueError, TypeError):
                font_size = 16  # 安全默认值
        
        # 验证字体大小的有效性 - 确保不为0或负数
        if font_size <= 0 or font_size > 72:
            font_size = 16  # 安全默认值
            
        print(f"设置字体: {font_family}, 大小: {font_size}")
        
        # 立即设置字体对象，使用setPointSize确保正确设置
        font = QFont(font_family)
        font.setPointSize(font_size)  # 使用setPointSize确保字体大小正确设置
        self.reading_area.setFont(font)
        self.current_font_size = font_size  # 记录当前字体大小
        
        # 立即应用字体设置到样式中，确保在所有模式下都生效，并禁用横向滚动条
        # 总是先应用正常模式的样式，因为初始化时不在极简模式
        self.reading_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid rgba(200, 200, 200, 100);
                border-radius: 8px;
                padding: 15px;
                font-family: '{font_family}';
                font-size: {font_size}px;
                color: #333333;
            }}
            QScrollBar:vertical {{
                background-color: rgba(240, 240, 240, 150);
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(180, 180, 180, 200);
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar:horizontal {{
                height: 0px;
            }}
        """)
        
        # 应用颜色设置
        bg_color = settings.get('bg_color', '#ffffff')
        text_color = settings.get('text_color', '#000000')
        self.apply_colors(bg_color, text_color)
        
        # 加载最近文档
        self.recent_files = settings.get('recent_files', [])
        self.update_recent_menu()
        
        # 恢复文档列表
        self.restore_file_list()
        
    def apply_colors(self, bg_color, text_color):
        """应用颜色设置"""
        palette = self.reading_area.palette()
        palette.setColor(QPalette.Base, QColor(bg_color))
        palette.setColor(QPalette.Text, QColor(text_color))
        self.reading_area.setPalette(palette)
        
    def save_settings(self):
        """保存设置"""
        current_font = self.reading_area.font()
        current_font_size = current_font.pointSize()
        # 确保保存的字体大小有效
        if current_font_size <= 0:
            current_font_size = 12
            
        # 获取当前透明度，确保是浮点数
        current_opacity = self.windowOpacity()
        if not isinstance(current_opacity, (int, float)):
            current_opacity = 1.0
        elif current_opacity <= 0 or current_opacity > 1:
            current_opacity = 1.0
            
        settings = {
            'opacity': current_opacity,
            'font_family': current_font.family(),
            'font_size': current_font_size,
            'recent_files': self.recent_files,
            'window_geometry': [self.x(), self.y(), self.width(), self.height()]
        }
        
        if self.current_file:
            settings['current_file'] = self.current_file
            # 保存阅读进度
            cursor = self.reading_area.textCursor()
            settings['reading_position'] = cursor.position()
            
        self.settings_manager.save_settings(settings)
        
    def restore_reading_progress(self):
        """恢复阅读进度"""
        if self.current_file:
            position = self.settings_manager.get_reading_position(self.current_file)
            if position:
                cursor = self.reading_area.textCursor()
                cursor.setPosition(position)
                self.reading_area.setTextCursor(cursor)
                
    def closeEvent(self, event):
        """关闭事件处理"""
        # 保存设置和进度
        self.save_settings()
        
        # 隐藏到托盘而不是关闭，不显示任何通知
        event.ignore()
        self.hide()
        
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.pdf', '.md', '.txt')):
                    event.accept()
                    return
        event.ignore()
        
    def dropEvent(self, event):
        """拖拽释放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_document(file_path)
            
    def mousePressEvent(self, event):
        """鼠标按下事件，用于窗口拖拽和调整大小"""
        if event.button() == Qt.LeftButton:
            # 检查是否在边框区域
            pos = event.pos()
            rect = self.rect()
            
            # 判断鼠标位置是否在边框
            border_width = self.resize_border_width
            
            # 计算边框检测区域
            left_boundary = border_width
            right_boundary = rect.width() - border_width
            bottom_boundary = rect.height() - border_width
            top_boundary = border_width
            
            on_left = pos.x() <= left_boundary
            on_right = pos.x() >= right_boundary
            on_top = pos.y() <= top_boundary
            on_bottom = pos.y() >= bottom_boundary
            
            # 添加调试信息
            mode_str = "极简模式" if self.minimal_mode else "普通模式"
            print(f"[{mode_str}鼠标按下] 位置=({pos.x()}, {pos.y()}), 窗口大小=({rect.width()}, {rect.height()})")
            print(f"[边框检测] 左={on_left}, 右={on_right}, 上={on_top}, 下={on_bottom}")
            print(f"[边框数值] 左边界<={left_boundary}, 右边界>={right_boundary}, 上边界<={top_boundary}, 下边界>={bottom_boundary}")
            print(f"[详细坐标] 鼠标X={pos.x()}, 左边界={left_boundary}, 右边界={right_boundary}")
            print(f"[窗口边缘检测] 窗口左边缘={rect.left()}, 窗口右边缘={rect.right()}, 窗口下边缘={rect.bottom()}")
            print(f"[鼠标相对位置] 鼠标相对于窗口左边缘={pos.x()}, 鼠标相对于窗口右边缘={rect.width() - pos.x()}, 鼠标相对于窗口下边缘={rect.height() - pos.y()}")
            
            # 上边框：移动窗口
            if on_top and not (on_left or on_right):
                # 上边框拖拽：移动窗口
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.resizing = False
                print("[拖拽模式] 开始移动窗口")
            # 左、右、下边框和角落：调整大小
            elif on_left or on_right or on_bottom or (on_left and on_top) or (on_right and on_top):
                # 在边框区域，启动调整大小模式
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                
                # 确定调整方向
                if on_left and on_top:
                    self.resize_direction = 'top-left'
                elif on_right and on_top:
                    self.resize_direction = 'top-right'
                elif on_left and on_bottom:
                    self.resize_direction = 'bottom-left'
                elif on_right and on_bottom:
                    self.resize_direction = 'bottom-right'
                elif on_left:
                    self.resize_direction = 'left'
                elif on_right:
                    self.resize_direction = 'right'
                elif on_bottom:
                    self.resize_direction = 'bottom'
                else:
                    # 如果不在明确的调整区域，回退到普通拖拽
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                    self.resizing = False
                    
                print(f"[拖拽模式] 开始调整大小: 方向={self.resize_direction}")
            else:
                # 不在边框区域，普通拖拽
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.resizing = False
                print("[拖拽模式] 开始普通拖拽")
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于窗口拖拽和调整大小"""
        pos = event.pos()
        rect = self.rect()
        
        # 确保使用正确的resize_border_width值
        border_width = self.resize_border_width
        
        # 添加更多调试信息
        mode_str = "极简模式" if self.minimal_mode else "普通模式"
        print(f"[调试信息] 当前模式: {mode_str}")
        print(f"[调试信息] resize_border_width当前值={border_width}")
        print(f"[调试信息] 窗口位置: ({self.x()}, {self.y()}), 窗口大小: {self.width()}x{self.height()}")
        print(f"[调试信息] 鼠标位置: ({pos.x()}, {pos.y()})")
        
        # 计算边框检测区域
        left_boundary = border_width
        right_boundary = rect.width() - border_width
        bottom_boundary = rect.height() - border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        # 显示所有鼠标位置的调试信息
        print(f"[鼠标移动] 位置=({pos.x()}, {pos.y()}), 窗口大小={rect.width()}x{rect.height()}")
        print(f"[边框数值] 左边界<={left_boundary}, 右边界>={right_boundary}, 下边界>={bottom_boundary}")
        print(f"[边框检测] 左={on_left}, 右={on_right}, 下={on_bottom}")
        
        # 强制调用光标更新
        self.update_cursor(pos)
        
        # 先处理窗口调整大小
        if self.resizing and event.buttons() == Qt.LeftButton and self.resize_start_geometry:
            # 调整窗口大小 - 修复计算逻辑
            diff = event.globalPos() - self.resize_start_pos
            # 使用起始几何信息作为基础来计算新的尺寸，确保计算正确
            start_geo = self.resize_start_geometry
            new_x = start_geo.x()
            new_y = start_geo.y()
            new_width = start_geo.width()
            new_height = start_geo.height()
            
            if self.resize_direction == 'right':
                # 向右调整大小，只改变宽度
                new_width = start_geo.width() + diff.x()
            elif self.resize_direction == 'bottom':
                # 向下调整大小，只改变高度
                new_height = start_geo.height() + diff.y()
            elif self.resize_direction == 'left':
                # 向左调整大小，需要同时调整x位置和宽度
                new_x = start_geo.x() + diff.x()
                new_width = start_geo.width() - diff.x()
            elif self.resize_direction == 'bottom-right':
                # 向右下调整大小，同时改变宽度和高度
                new_width = start_geo.width() + diff.x()
                new_height = start_geo.height() + diff.y()
            elif self.resize_direction == 'bottom-left':
                # 向左下调整大小，需要同时调整x位置、宽度和高度
                new_x = start_geo.x() + diff.x()
                new_width = start_geo.width() - diff.x()
                new_height = start_geo.height() + diff.y()
            elif self.resize_direction == 'top-right':
                # 向右上调整大小，需要同时调整y位置、宽度和高度
                new_y = start_geo.y() + diff.y()
                new_width = start_geo.width() + diff.x()
                new_height = start_geo.height() - diff.y()
            elif self.resize_direction == 'top-left':
                # 向左上调整大小，需要同时调整x位置、y位置、宽度和高度
                new_x = start_geo.x() + diff.x()
                new_y = start_geo.y() + diff.y()
                new_width = start_geo.width() - diff.x()
                new_height = start_geo.height() - diff.y()
            
            # 设置最小尺寸
            if new_width < 300:
                new_width = 300
            if new_height < 200:
                new_height = 200
            
            self.setGeometry(new_x, new_y, new_width, new_height)
            event.accept()
            return
            
        # 处理普通窗口拖拽
        elif event.buttons() == Qt.LeftButton and self.drag_position:
            # 普通拖拽
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            return
        
        # 如果在边框区域，直接处理调整大小逻辑
        if on_left or on_right or on_bottom:
            # 阻止事件传播到子控件
            event.accept()
            return
            
        # 无论是否按下鼠标，都要更新光标样式
        print(f"[调试信息] 更新光标样式")
        self.update_cursor(event.pos())
        event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.resize_direction = None
            self.drag_position = None
        event.accept()
        
    def update_cursor(self, pos):
        """根据鼠标位置更新光标样式 - 在极简模式和正常模式下都工作"""
        # 添加详细调试
        mode_str = "极简模式" if self.minimal_mode else "普通模式"
        print(f"[光标更新] 开始处理 - 模式={mode_str}, 位置=({pos.x()}, {pos.y()})")
        print(f"[光标更新] resize_border_width={self.resize_border_width}")
        print(f"[光标更新] resizing状态={self.resizing}")
        
        # 在极简模式和正常模式下都允许边框调整
        # 只有在鼠标左键按下且正在调整大小时才跳过光标更新
        if self.resizing and QApplication.mouseButtons() & Qt.LeftButton:
            print(f"[光标更新] 正在调整大小中，跳过光标更新")
            return
        
        # 重置resizing状态，确保在没有鼠标按键时能正确更新光标
        # 添加安全检查，确保QApplication可用
        try:
            if not (QApplication.mouseButtons() & Qt.LeftButton):
                self.resizing = False
                self.resize_direction = None
        except:
            # 如果QApplication不可用，直接重置状态
            self.resizing = False
            self.resize_direction = None
            
        rect = self.rect()
        # 使用局部变量确保一致性
        border_width = self.resize_border_width
        
        # 计算边框检测区域
        left_boundary = border_width
        right_boundary = rect.width() - border_width
        bottom_boundary = rect.height() - border_width
        top_boundary = border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_top = pos.y() <= top_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        # 添加调试信息
        print(f"[光标更新调试] 边框检测: 左={on_left}, 右={on_right}, 上={on_top}, 下={on_bottom}")
        print(f"[光标更新调试] 窗口大小: {rect.width()}x{rect.height()}")
        print(f"[光标更新调试] 边框阈值: 左<={left_boundary}, 右>={right_boundary}, 上<={top_boundary}, 下>={bottom_boundary}")
        print(f"[窗口边缘检测] 窗口左边缘={rect.left()}, 窗口右边缘={rect.right()}, 窗口下边缘={rect.bottom()}")
        print(f"[鼠标相对位置] 鼠标相对于窗口左边缘={pos.x()}, 鼠标相对于窗口右边缘={rect.width() - pos.x()}, 鼠标相对于窗口下边缘={rect.height() - pos.y()}")
        
        # 上边框：移动光标（只有上边，不包含角落）
        if on_top and not (on_left or on_right):
            self.setCursor(Qt.SizeAllCursor)  # 移动光标
            print("[光标] 设置为移动光标 - SizeAllCursor")
        # 角落拖拽：调整大小
        elif on_left and on_top or on_right and on_bottom:
            self.setCursor(Qt.SizeFDiagCursor)  # 斜对角箭头
            print("[光标] 设置为斜对角调整光标 - SizeFDiagCursor")
        elif on_right and on_top or on_left and on_bottom:
            self.setCursor(Qt.SizeBDiagCursor)  # 斜对角箭头
            print("[光标] 设置为斜对角调整光标 - SizeBDiagCursor")
        # 左右边框：水平调整
        elif on_left or on_right:
            print(f"[光标设置] 检测到水平边框, 左={on_left}, 右={on_right}")
            self.setCursor(Qt.SizeHorCursor)    # 水平箭头
            print("[光标] 设置为水平调整光标 - SizeHorCursor")
            # 强制刷新光标显示
            self.update()
        # 下边框：垂直调整
        elif on_bottom:
            print(f"[光标设置] 检测到垂直边框, 下={on_bottom}")
            self.setCursor(Qt.SizeVerCursor)    # 垂直到箭头
            print("[光标] 设置为垂直调整光标 - SizeVerCursor")
            # 强制刷新光标显示
            self.update()
        else:
            self.setCursor(Qt.ArrowCursor)      # 普通箭头
            print("[光标] 设置为普通箭头 - ArrowCursor")
            
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件，切换最大化状态"""
        if event.button() == Qt.LeftButton:
            # 只有在标题栏区域双击才最大化
            if event.pos().y() <= 30:  # 标题栏高度
                if self.isMaximized():
                    self.showNormal()
                else:
                    self.showMaximized()
            event.accept()
            
    def eventFilter(self, obj, event):
        """事件过滤器，主要用于处理阅读区域的滚轮事件和鼠标事件传播"""
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QWheelEvent, QMouseEvent
        
        # 处理鼠标移动事件，从子控件传播到主窗口
        # 关键修复：确保边框检测区域不被子控件拦截
        child_widgets = []
        if hasattr(self, 'reading_area') and self.reading_area:
            child_widgets.append(self.reading_area)
        if hasattr(self, 'file_panel') and self.file_panel:
            child_widgets.append(self.file_panel)
        if hasattr(self, 'splitter') and self.splitter:
            child_widgets.append(self.splitter)
        if hasattr(self, 'file_list') and self.file_list:
            child_widgets.append(self.file_list)
        if hasattr(self, 'status_bar') and self.status_bar:
            child_widgets.append(self.status_bar)
        if self.centralWidget():
            child_widgets.append(self.centralWidget())
            
        if event.type() == QEvent.MouseMove and obj in child_widgets:
            # 将子控件的鼠标移动事件映射到主窗口坐标系
            child_pos = event.pos()
            global_pos = obj.mapToGlobal(child_pos)
            main_window_pos = self.mapFromGlobal(global_pos)
            
            # 手动调用主窗口的鼠标移动事件处理
            mouse_event = QMouseEvent(event.type(), main_window_pos, global_pos, 
                                    event.button(), event.buttons(), event.modifiers())
            self.mouseMoveEvent(mouse_event)
            
            # 让事件继续传播给子控件
            return False
        elif event.type() == QEvent.MouseButtonPress and obj in child_widgets:
            # 将子控件的鼠标按下事件映射到主窗口坐标系
            child_pos = event.pos()
            global_pos = obj.mapToGlobal(child_pos)
            main_window_pos = self.mapFromGlobal(global_pos)
            
            # 手动调用主窗口的鼠标按下事件处理
            mouse_event = QMouseEvent(event.type(), main_window_pos, global_pos, 
                                    event.button(), event.buttons(), event.modifiers())
            self.mousePressEvent(mouse_event)
            
            # 让事件继续传播给子控件
            return False
        elif event.type() == QEvent.MouseButtonRelease and obj in child_widgets:
            # 将子控件的鼠标释放事件映射到主窗口坐标系
            child_pos = event.pos()
            global_pos = obj.mapToGlobal(child_pos)
            main_window_pos = self.mapFromGlobal(global_pos)
            
            # 手动调用主窗口的鼠标释放事件处理
            mouse_event = QMouseEvent(event.type(), main_window_pos, global_pos, 
                                    event.button(), event.buttons(), event.modifiers())
            self.mouseReleaseEvent(mouse_event)
            
            # 让事件继续传播给子控件
            return False
            
        # 按照用户要求，字体大小调整必须在偏好设置中进行，不再支持Ctrl+滚轮动态调整
        # 这里保留事件过滤器的结构，但不处理缩放操作
        
        return super().eventFilter(obj, event)
            
    def setup_mouse_tracking(self):
        """配置所有组件的鼠标跟踪和事件过滤器 - 关键修复"""
        print("[鼠标跟踪配置] 开始配置所有组件的鼠标跟踪...")
        
        # 1. 主窗口鼠标跟踪
        self.setMouseTracking(True)
        print("[鼠标跟踪配置] 主窗口鼠标跟踪已启用")
        
        # 2. 中央部件鼠标跟踪
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.setMouseTracking(True)
            central_widget.installEventFilter(self)
            print("[鼠标跟踪配置] 中央部件鼠标跟踪已启用")
        
        # 3. 阅读区域鼠标跟踪
        if hasattr(self, 'reading_area') and self.reading_area:
            self.reading_area.setMouseTracking(True)
            self.reading_area.installEventFilter(self)
            print("[鼠标跟踪配置] 阅读区域鼠标跟踪已启用")
        
        # 4. 文件面板鼠标跟踪
        if hasattr(self, 'file_panel') and self.file_panel:
            self.file_panel.setMouseTracking(True)
            self.file_panel.installEventFilter(self)
            print("[鼠标跟踪配置] 文件面板鼠标跟踪已启用")
        
        # 5. 文件列表鼠标跟踪
        if hasattr(self, 'file_list') and self.file_list:
            self.file_list.setMouseTracking(True)
            self.file_list.installEventFilter(self)
            print("[鼠标跟踪配置] 文件列表鼠标跟踪已启用")
        
        # 6. 分割器鼠标跟踪
        if hasattr(self, 'splitter') and self.splitter:
            self.splitter.setMouseTracking(True)
            self.splitter.installEventFilter(self)
            print("[鼠标跟踪配置] 分割器鼠标跟踪已启用")
        
        # 7. 状态栏鼠标跟踪
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.setMouseTracking(True)
            self.status_bar.installEventFilter(self)
            print("[鼠标跟踪配置] 状态栏鼠标跟踪已启用")
        
        print("[鼠标跟踪配置] 所有组件鼠标跟踪配置完成")
            
    def minimize_to_tray(self):
        """最小化到托盘"""
        self.hide()
        
    def toggle_file_list(self):
        """切换文档列表显示"""
        self.file_list_visible = not self.file_list_visible
        self.file_panel.setVisible(self.file_list_visible)
        
    def toggle_file_list_collapse(self):
        """收缩/展开文档列表"""
        if self.file_panel.width() > 50:  # 当前是展开状态
            # 收缩到只显示按钮
            self.file_panel.setMaximumWidth(40)
            self.file_panel.setMinimumWidth(40)
            self.file_list.hide()
            self.collapse_btn.setText("»")
            self.collapse_btn.setToolTip("展开文档列表")
        else:  # 当前是收缩状态
            # 展开显示列表
            self.file_panel.setMaximumWidth(250)
            self.file_panel.setMinimumWidth(150)
            self.file_list.show()
            self.collapse_btn.setText("«")
            self.collapse_btn.setToolTip("收缩文档列表")
        
    def keyPressEvent(self, event):
        """键盘按下事件，确保在极简模式下也能响应F3"""
        if event.key() == Qt.Key_F3:
            self.toggle_minimal_mode()
            event.accept()
        elif event.key() == Qt.Key_F2:
            self.toggle_file_list()
            event.accept()
        else:
            super().keyPressEvent(event)
            
    def toggle_minimal_mode(self):
        """切换极简模式"""
        self.mode_manager.toggle_mode()
        self.minimal_mode = self.mode_manager.minimal_mode
        
    def restore_file_list(self):
        """恢复文档列表"""
        try:
            print(f"恢复文档列表，最近文档数量: {len(self.recent_files)}")
            # 清空现有列表
            self.file_list.clear()
            
            # 添加最近文档到列表
            for file_path in self.recent_files:
                if os.path.exists(file_path):
                    print(f"添加文档到列表: {os.path.basename(file_path)}")
                    self.add_to_file_list(file_path)
                else:
                    print(f"文档不存在，跳过: {file_path}")
        except Exception as e:
            print(f"恢复文档列表时出错: {e}")
            
    def save_reading_progress_on_change(self):
        """在文档切换时保存阅读进度"""
        if self.current_file:
            cursor = self.reading_area.textCursor()
            position = cursor.position()
            self.settings_manager.save_reading_progress(self.current_file, position)
            print(f"保存阅读进度: {os.path.basename(self.current_file)} -> 位置 {position}")
            
    def auto_save_reading_progress(self):
        """自动保存阅读进度"""
        if self.current_file:
            cursor = self.reading_area.textCursor()
            position = cursor.position()
            self.settings_manager.save_reading_progress(self.current_file, position)
            # 不显示日志，避免干扰
            
    def show_context_menu(self, position):
        """显示右键菜单"""
        if self.minimal_mode:
            # 极简模式下的右键菜单
            self.mode_manager.show_minimal_context_menu(position)
        else:
            # 正常模式下使用默认右键菜单
            pass  # 使用QTextBrowser默认的右键菜单
            
    def toggle_stay_on_top_minimal(self, checked):
        """极简模式下切换置顶状态"""
        current_flags = self.windowFlags()
        if checked:
            # 设置置顶
            new_flags = current_flags | Qt.WindowStaysOnTopHint
        else:
            # 取消置顶
            new_flags = current_flags & ~Qt.WindowStaysOnTopHint
        
        # 保持极简模式的无边框特性
        new_flags |= Qt.FramelessWindowHint
        
        self.setWindowFlags(new_flags)
        self.show()  # 重新显示窗口使标志生效

    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == event.WindowStateChange:
            # 确保状态栏在窗口状态变化后仍然正确显示
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.setVisible(True)
                # 强制更新状态栏布局
                self.status_bar.updateGeometry()
                # 确保状态栏在最前面
                self.status_bar.raise_()
        super().changeEvent(event)

    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        # 确保状态栏在窗口大小变化后仍然正确显示
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.setVisible(True)
        super().resizeEvent(event)