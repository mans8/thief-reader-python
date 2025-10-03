#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终边框修复测试程序
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt

class FinalBorderFixTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.minimal_mode = False
        self.resize_border_width = 15  # 边框检测宽度
        
    def init_ui(self):
        self.setWindowTitle("最终边框修复测试")
        self.setGeometry(300, 300, 700, 500)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
            }
        """)
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)  # 为边框检测留出空间
        
        # 创建状态标签
        self.status_label = QLabel("状态信息将显示在这里")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(240, 240, 240, 180);
                padding: 10px;
                border-radius: 5px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
        """)
        self.main_layout.addWidget(self.status_label)
        
        # 创建阅读区域
        self.reading_area = QTextEdit()
        self.reading_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid rgba(200, 200, 200, 100);
                border-radius: 8px;
                padding: 15px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                color: #333333;
            }
        """)
        self.reading_area.setPlainText("这是测试区域，用于验证边框检测功能。\n\n请移动鼠标到窗口边缘观察光标变化。")
        self.main_layout.addWidget(self.reading_area)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
        self.central_widget.setMouseTracking(True)
        self.reading_area.setMouseTracking(True)
        
    def toggle_minimal_mode(self):
        """切换最简模式"""
        self.minimal_mode = not self.minimal_mode
        
        if self.minimal_mode:
            print("进入最简模式")
            # 调整布局边距为边框检测留出空间
            self.main_layout.setContentsMargins(25, 25, 25, 25)
            
            # 设置阅读区域样式（减少padding确保边框检测）
            self.reading_area.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 200);
                    border: none;
                    border-radius: 0px;
                    padding: 5px;  /* 关键：减少padding为边框检测留出空间 */
                    font-family: 'Microsoft YaHei';
                    font-size: 14px;
                    color: rgba(51, 51, 51, 200);
                }
            """)
        else:
            print("退出最简模式")
            # 恢复正常布局边距
            self.main_layout.setContentsMargins(25, 25, 25, 25)
            
            # 恢复阅读区域样式
            self.reading_area.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 220);
                    border: 1px solid rgba(200, 200, 200, 100);
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'Microsoft YaHei';
                    font-size: 14px;
                    color: #333333;
                }
            """)
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        pos = event.pos()
        rect = self.rect()
        
        # 计算边框检测区域
        left_boundary = self.resize_border_width
        right_boundary = rect.width() - self.resize_border_width
        bottom_boundary = rect.height() - self.resize_border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        # 更新状态标签
        status_text = f"位置: ({pos.x()}, {pos.y()}) | 窗口: {rect.width()}x{rect.height()}\n"
        status_text += f"边界: 左<={left_boundary}, 右>={right_boundary}, 下>={bottom_boundary}\n"
        status_text += f"检测: 左={on_left}, 右={on_right}, 下={on_bottom}"
        self.status_label.setText(status_text)
        
        # 更新光标
        if on_left or on_right:
            self.setCursor(Qt.SizeHorCursor)
        elif on_bottom:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
        super().mouseMoveEvent(event)
        
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_F3:
            self.toggle_minimal_mode()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    window = FinalBorderFixTest()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()