#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的边框测试程序
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class SimpleBorderTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("简单边框测试")
        self.setGeometry(200, 200, 600, 400)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
            }
        """)
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置边距用于边框检测
        
        # 创建标签
        label = QLabel("移动鼠标到窗口边缘测试边框检测功能")
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 20px;
                background-color: transparent;
            }
        """)
        layout.addWidget(label)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
        central_widget.setMouseTracking(True)
        
        # 边框检测宽度
        self.resize_border_width = 20
        
    def mouseMoveEvent(self, event):
        pos = event.pos()
        rect = self.rect()
        
        # 计算边框检测区域
        left_boundary = self.resize_border_width
        right_boundary = rect.width() - self.resize_border_width
        bottom_boundary = rect.height() - self.resize_border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        # 显示调试信息
        print(f"[测试] 位置=({pos.x()}, {pos.y()}), 窗口大小={rect.width()}x{rect.height()}")
        print(f"[测试] 边界: 左<={left_boundary}, 右>={right_boundary}, 下>={bottom_boundary}")
        print(f"[测试] 检测: 左={on_left}, 右={on_right}, 下={on_bottom}")
        
        # 更新光标
        if on_left or on_right:
            self.setCursor(Qt.SizeHorCursor)
            print("[测试] 光标: 水平调整")
        elif on_bottom:
            self.setCursor(Qt.SizeVerCursor)
            print("[测试] 光标: 垂直调整")
        else:
            self.setCursor(Qt.ArrowCursor)
            print("[测试] 光标: 普通箭头")
            
        super().mouseMoveEvent(event)

def main():
    app = QApplication(sys.argv)
    window = SimpleBorderTest()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()