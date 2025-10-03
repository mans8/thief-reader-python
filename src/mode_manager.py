#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模式管理模块
负责管理窗口的不同显示模式（普通模式和极简模式）
"""

from typing import Any


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QTextBrowser, QMenu, QAction

class ModeManager:
    """模式管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.minimal_mode = False
        
    def toggle_mode(self):
        """切换显示模式"""
        self.minimal_mode = not self.minimal_mode
        
        if self.minimal_mode:
            self._enter_minimal_mode()
        else:
            self._exit_minimal_mode()
            
    def _enter_minimal_mode(self):
        """进入极简模式"""
        print("进入极简模式")
        main_window = self.main_window
        
        # 隐藏所有界面元素，只保留阅读区域
        main_window.title_bar.hide()
        main_window.menu_container.hide()
        main_window.statusBar().hide()
        main_window.file_panel.hide()
        main_window.doc_title.hide()
        
        # 在极简模式下彻底移除所有边框，只保留一层简洁显示
        main_window.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 从设置中加载透明度
        settings = main_window.settings_manager.load_settings()
        opacity = settings.get('opacity', 1.0)
        if isinstance(opacity, str):
            try:
                opacity = float(opacity)
            except (ValueError, TypeError):
                opacity = 1.0
        opacity = max(0.1, min(1.0, opacity))
        main_window.setWindowOpacity(opacity)
        
        # 设置主窗口中央部件样式 - 移除所有边框和圆角
        central_widget = main_window.centralWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
        """)
        
        # 设置阅读区域样式 - 移除边框，只保留基本样式
        font_family = settings.get('font_family', 'Microsoft YaHei')
        font_size = settings.get('font_size', main_window.current_font_size)
        if not isinstance(font_size, int) or font_size <= 0:
            font_size = 16
            
        main_window.reading_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(255, 255, 255, 200);
                border: none;
                border-radius: 0px;
                padding: 5px;
                font-family: '{font_family}';
                font-size: {font_size}px;
                color: #333333;
            }}
        """)
        
    def _exit_minimal_mode(self):
        """退出极简模式"""
        print("退出极简模式")
        main_window = self.main_window
        
        # 恢复显示所有界面元素
        main_window.title_bar.show()
        main_window.menu_container.show()
        main_window.statusBar().show()
        main_window.doc_title.show()
        if main_window.file_list_visible:
            main_window.file_panel.show()
        
        # 恢复正常透明度 - 确保标题栏和菜单栏完全不透明
        central_widget = main_window.centralWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 255);  /* 完全不透明 */
                border-radius: 10px;
            }
        """)
        
        # 恢复标题栏样式 - 完全不透明
        main_window.title_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(70, 130, 180, 255);  /* 完全不透明 */
                border-radius: 5px;
            }
        """)
        
        # 恢复菜单容器样式 - 完全不透明
        main_window.menu_container.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 255);  /* 完全不透明 */
                border-radius: 0px;
            }
        """)
        
        # 恢复阅读面板容器样式
        # 通过遍历splitter的子部件找到阅读面板容器并恢复样式
        for i in range(main_window.splitter.count()):
            widget = main_window.splitter.widget(i)
            if widget and hasattr(widget, 'findChild'):
                reading_area = widget.findChild(QTextBrowser)
                if reading_area == main_window.reading_area:
                    # 这是阅读面板容器
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: rgba(255, 255, 255, 0);
                            border: none;
                        }
                    """)
                    break
        
        # 恢复阅读区域样式（带字体大小），并保持禁用横向滚动条
        settings = main_window.settings_manager.load_settings()
        font_family = settings.get('font_family', 'Microsoft YaHei')
        font_size = settings.get('font_size', main_window.current_font_size)
        if not isinstance(font_size, int) or font_size <= 0:
            font_size = 16
            
        main_window.reading_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(255, 255, 255, 255);  /* 完全不透明 */
                border: 1px solid rgba(200, 200, 200, 255);  /* 完全不透明边框 */
                border-radius: 8px;
                padding: 15px;
                font-family: '{font_family}';
                font-size: {font_size}px;
                color: #333333;
            }}
            QScrollBar:vertical {{
                background-color: rgba(240, 240, 240, 255);  /* 完全不透明 */
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(180, 180, 180, 255);  /* 完全不透明 */
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar:horizontal {{
                height: 0px;
            }}
        """)
        
        # 确保在普通模式下正确设置鼠标跟踪
        main_window.setMouseTracking(True)
        if hasattr(main_window, 'reading_area') and main_window.reading_area:
            main_window.reading_area.setMouseTracking(True)
            
        # 关键修复：确保中央部件在普通模式下也能正确接收鼠标事件
        central_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        central_widget.setMouseTracking(True)
        central_widget.installEventFilter(main_window)
            
    def show_minimal_context_menu(self, position):
        """显示极简模式下的右键菜单"""
        main_window = self.main_window
        
        # 极简模式下的右键菜单
        menu = QMenu()
        
        # 退出极简模式
        exit_minimal_action = QAction("退出极简模式", main_window)
        exit_minimal_action.triggered.connect(self.toggle_mode)
        menu.addAction(exit_minimal_action)
        
        menu.addSeparator()
        
        # 窗口置于最顶
        stay_on_top_action = QAction("窗口置于最顶", main_window)
        stay_on_top_action.setCheckable(True)
        # 检查当前窗口是否置顶
        current_flags = main_window.windowFlags()
        is_on_top = bool(current_flags & Qt.WindowStaysOnTopHint)
        stay_on_top_action.setChecked(is_on_top)
        stay_on_top_action.triggered.connect(lambda checked: main_window.toggle_stay_on_top_minimal(checked))
        menu.addAction(stay_on_top_action)
        
        menu.addSeparator()
        
        # 关闭窗口
        close_action = QAction("关闭窗口", main_window)
        close_action.triggered.connect(main_window.close)
        menu.addAction(close_action)
        
        # 在鼠标位置显示菜单
        global_pos = main_window.reading_area.mapToGlobal(position)
        menu.exec_(global_pos)