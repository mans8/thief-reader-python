#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试resize_border_width值变化的测试程序
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt

class DetailedDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize_border_width = 10  # 初始化为10
        self.minimal_mode = False
        print(f"[初始化] resize_border_width = {self.resize_border_width}")
        
        # 记录所有resize_border_width的修改历史
        self.resize_border_history = []
        self.log_resize_border_change("初始化", self.resize_border_width)
        
        self.init_ui()
        
    def log_resize_border_change(self, reason, value):
        """记录resize_border_width的修改历史"""
        import traceback
        stack = traceback.format_stack()
        self.resize_border_history.append({
            "reason": reason,
            "value": value,
            "stack": stack[-2]  # 记录调用栈
        })
        print(f"[历史记录] {reason}: resize_border_width = {value}")
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("详细调试resize_border_width值变化")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
            }
        """)
        central_widget.setMouseTracking(True)
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 状态标签
        self.status_label = QLabel("调试信息将显示在这里")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(240, 240, 240, 180);
                padding: 10px;
                border-radius: 5px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # 历史记录区域
        self.history_area = QTextEdit()
        self.history_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid rgba(200, 200, 200, 100);
                border-radius: 8px;
                padding: 15px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                color: #333333;
            }
        """)
        self.history_area.setPlainText("历史记录将显示在这里...")
        layout.addWidget(self.history_area)
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        pos = event.pos()
        rect = self.rect()
        
        # 显示当前resize_border_width值
        print(f"[调试] 当前resize_border_width = {self.resize_border_width}")
        
        # 边框检测
        on_left = pos.x() <= self.resize_border_width
        on_right = pos.x() >= rect.width() - self.resize_border_width
        on_bottom = pos.y() >= rect.height() - self.resize_border_width
        
        # 更新状态标签
        status_text = f"鼠标位置: ({pos.x()}, {pos.y()})\n"
        status_text += f"窗口大小: {rect.width()}x{rect.height()}\n"
        status_text += f"resize_border_width: {self.resize_border_width}\n"
        status_text += f"边框检测: 左={on_left}, 右={on_right}, 下={on_bottom}\n"
        status_text += f"左边界: <= {self.resize_border_width}\n"
        status_text += f"右边界: >= {rect.width() - self.resize_border_width}\n"
        status_text += f"下边界: >= {rect.height() - self.resize_border_width}"
        
        self.status_label.setText(status_text)
        
        # 更新光标
        self.update_cursor(pos)
        
        event.accept()
        
    def update_cursor(self, pos):
        """更新光标样式"""
        if hasattr(self, '_in_update_cursor') and self._in_update_cursor:
            return
            
        self._in_update_cursor = True
        
        try:
            rect = self.rect()
            on_left = pos.x() <= self.resize_border_width
            on_right = pos.x() >= rect.width() - self.resize_border_width
            on_bottom = pos.y() >= rect.height() - self.resize_border_width
            
            if on_left or on_right:
                self.setCursor(Qt.SizeHorCursor)
            elif on_bottom:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        finally:
            self._in_update_cursor = False
            
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_F3:
            self.toggle_minimal_mode()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_H:
            # 显示历史记录
            self.show_history()
        else:
            super().keyPressEvent(event)
            
    def show_history(self):
        """显示修改历史"""
        history_text = "=== resize_border_width 修改历史 ===\n\n"
        for i, record in enumerate(self.resize_border_history):
            history_text += f"{i+1}. {record['reason']}: {record['value']}\n"
            history_text += f"   调用栈: {record['stack'].strip()}\n\n"
            
        self.history_area.setPlainText(history_text)
            
    def toggle_minimal_mode(self):
        """切换最简模式"""
        self.minimal_mode = not self.minimal_mode
        print(f"[最简模式] 切换到: {self.minimal_mode}")
        
        if self.minimal_mode:
            # 在最简模式下设置resize_border_width为10
            old_value = self.resize_border_width
            self.resize_border_width = 10
            self.log_resize_border_change("进入最简模式", self.resize_border_width)
            
            # 更新样式
            central_widget = self.centralWidget()
            central_widget.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                    border-radius: 0px;
                }
            """)
        else:
            # 退出最简模式时恢复resize_border_width为10
            old_value = self.resize_border_width
            self.resize_border_width = 10
            self.log_resize_border_change("退出最简模式", self.resize_border_width)
            
            # 恢复样式
            central_widget = self.centralWidget()
            central_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 10px;
                }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DetailedDebugWindow()
    window.show()
    sys.exit(app.exec_())