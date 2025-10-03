#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复方案：解决最简模式下文档阅读窗口无法调节大小的问题
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTextBrowser, QFrame)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

class FinalFixSolution(QMainWindow):
    """最终修复方案实现"""
    
    def __init__(self):
        super().__init__()
        self._resize_border_width = 15  # 边框检测宽度
        self.resizing = False
        self.resize_direction = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.minimal_mode = False
        
        self.init_ui()
        
    @property
    def resize_border_width(self):
        return self._resize_border_width
    
    @resize_border_width.setter
    def resize_border_width(self, value):
        self._resize_border_width = value
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("最终修复方案测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 启用鼠标跟踪
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
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)  # 为边框检测留出空间
        
        # 创建阅读区域
        self.reading_area = QTextBrowser()
        self.reading_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 220);
                border: none;
                border-radius: 0px;
                padding: 5px;
            }
        """)
        self.reading_area.setMouseTracking(True)
        main_layout.addWidget(self.reading_area)
        
        # 设置测试内容
        self.reading_area.setPlainText("测试内容...\n请尝试在窗口边缘拖拽调整大小")
        
    def toggle_minimal_mode(self):
        """切换最简模式"""
        self.minimal_mode = not self.minimal_mode
        
        if self.minimal_mode:
            print("进入最简模式")
            # 设置边框检测宽度
            self.resize_border_width = 15
            
            # 调整布局边距为边框检测留出空间
            central_widget = self.centralWidget()
            main_layout = central_widget.layout()
            if main_layout:
                main_layout.setContentsMargins(25, 25, 25, 25)
                
            # 设置透明样式
            central_widget.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                    border-radius: 0px;
                }
            """)
            
            # 设置阅读区域透明样式
            self.reading_area.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 200);
                    border: none;
                    border-radius: 0px;
                    padding: 5px;
                }
            """)
        else:
            print("退出最简模式")
            # 恢复正常样式
            self.resize_border_width = 15
            
            central_widget = self.centralWidget()
            main_layout = central_widget.layout()
            if main_layout:
                main_layout.setContentsMargins(5, 5, 5, 5)
                
            central_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 10px;
                }
            """)
            
            self.reading_area.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 220);
                    border: 1px solid rgba(200, 200, 200, 100);
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            rect = self.rect()
            
            # 使用当前的resize_border_width值
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
            
            print(f"[鼠标按下] 位置=({pos.x()}, {pos.y()}), 窗口大小={rect.width()}x{rect.height()}")
            print(f"[边框检测] 左={on_left}, 右={on_right}, 上={on_top}, 下={on_bottom}")
            
            # 左、右、下边框：调整大小
            if on_left or on_right or on_bottom:
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                
                # 确定调整方向
                if on_left and on_bottom:
                    self.resize_direction = 'bottom-left'
                elif on_right and on_bottom:
                    self.resize_direction = 'bottom-right'
                elif on_left:
                    self.resize_direction = 'left'
                elif on_right:
                    self.resize_direction = 'right'
                elif on_bottom:
                    self.resize_direction = 'bottom'
                    
                print(f"[拖拽模式] 开始调整大小: 方向={self.resize_direction}")
            else:
                # 普通拖拽
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.resizing = False
                print("[拖拽模式] 开始普通拖拽")
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        pos = event.pos()
        rect = self.rect()
        
        # 使用当前的resize_border_width值
        border_width = self.resize_border_width
        
        # 计算边框检测区域
        left_boundary = border_width
        right_boundary = rect.width() - border_width
        bottom_boundary = rect.height() - border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        print(f"[鼠标移动] 位置=({pos.x()}, {pos.y()}), 窗口大小={rect.width()}x{rect.height()}")
        print(f"[边框检测] 左={on_left}, 右={on_right}, 下={on_bottom}")
        
        # 更新光标样式
        self.update_cursor(pos)
        
        # 处理窗口调整大小
        if self.resizing and event.buttons() == Qt.LeftButton and self.resize_start_geometry:
            diff = event.globalPos() - self.resize_start_pos
            start_geo = self.resize_start_geometry
            new_x = start_geo.x()
            new_y = start_geo.y()
            new_width = start_geo.width()
            new_height = start_geo.height()
            
            if self.resize_direction == 'right':
                new_width = start_geo.width() + diff.x()
            elif self.resize_direction == 'bottom':
                new_height = start_geo.height() + diff.y()
            elif self.resize_direction == 'left':
                new_x = start_geo.x() + diff.x()
                new_width = start_geo.width() - diff.x()
            elif self.resize_direction == 'bottom-right':
                new_width = start_geo.width() + diff.x()
                new_height = start_geo.height() + diff.y()
            elif self.resize_direction == 'bottom-left':
                new_x = start_geo.x() + diff.x()
                new_width = start_geo.width() - diff.x()
                new_height = start_geo.height() + diff.y()
            
            # 设置最小尺寸
            if new_width < 300:
                new_width = 300
            if new_height < 200:
                new_height = 200
                
            self.setGeometry(new_x, new_y, new_width, new_height)
            event.accept()
            return
            
        # 处理普通窗口拖拽
        elif event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            return
            
        event.accept()
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.resize_direction = None
            if hasattr(self, 'drag_position'):
                del self.drag_position
        event.accept()
        
    def update_cursor(self, pos):
        """更新光标样式"""
        rect = self.rect()
        border_width = self.resize_border_width
        
        # 计算边框检测区域
        left_boundary = border_width
        right_boundary = rect.width() - border_width
        bottom_boundary = rect.height() - border_width
        
        on_left = pos.x() <= left_boundary
        on_right = pos.x() >= right_boundary
        on_bottom = pos.y() >= bottom_boundary
        
        # 左右边框：水平调整
        if on_left or on_right:
            self.setCursor(Qt.SizeHorCursor)
            print("[光标] 设置为水平调整光标")
        # 下边框：垂直调整
        elif on_bottom:
            self.setCursor(Qt.SizeVerCursor)
            print("[光标] 设置为垂直调整光标")
        # 角落：对角调整
        elif (on_left and on_bottom) or (on_right and on_bottom):
            self.setCursor(Qt.SizeFDiagCursor)
            print("[光标] 设置为对角调整光标")
        else:
            self.setCursor(Qt.ArrowCursor)
            print("[光标] 设置为普通箭头")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FinalFixSolution()
    window.show()
    sys.exit(app.exec_())