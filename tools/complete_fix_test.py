#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整修复测试程序：验证最简模式下边框拖拽功能
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTextBrowser, QLabel)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

class BorderDragTestWindow(QMainWindow):
    """边框拖拽测试窗口"""
    
    def __init__(self):
        super().__init__()
        self._resize_border_width = 15  # 边框检测宽度
        self.resizing = False
        self.resize_direction = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.drag_position = None
        self.minimal_mode = False
        
        self.init_ui()
        
    @property
    def resize_border_width(self):
        """获取边框检测宽度"""
        print(f"[属性获取] resize_border_width当前值: {self._resize_border_width}")
        return self._resize_border_width
    
    @resize_border_width.setter
    def resize_border_width(self, value):
        """设置边框检测宽度"""
        print(f"[属性设置] resize_border_width设置为: {value}")
        self._resize_border_width = value
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("边框拖拽功能测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
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
        
        # 状态标签
        self.status_label = QLabel("状态信息将显示在这里")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(240, 240, 240, 180);
                padding: 5px;
                border-radius: 3px;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
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
        self.reading_area.setPlainText("""
边框拖拽功能测试

测试步骤：
1. 移动鼠标到窗口边缘（15px范围内）
2. 观察光标是否变化：
   - 左/右边框：应显示 ↔ 水平光标
   - 下边框：应显示 ↕ 垂直光标
   - 上边框：应显示 ✥ 移动光标
3. 按住鼠标左键拖拽测试调整功能

当前边框宽度：15px
布局边距：25px（为边框检测预留空间）
        """)
        main_layout.addWidget(self.reading_area)
        
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
                border_margin = self.resize_border_width + 10  # 边距比边框宽度大10px
                main_layout.setContentsMargins(border_margin, border_margin, border_margin, border_margin)
                
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
                normal_margin = max(5, self.resize_border_width - 10)  # 确保至少5px边距
                main_layout.setContentsMargins(normal_margin, normal_margin, normal_margin, normal_margin)
                
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
            
            # 上边框：移动窗口
            if on_top and not (on_left or on_right):
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.resizing = False
                print("[拖拽模式] 开始移动窗口")
            # 左、右、下边框：调整大小
            elif on_left or on_right or on_bottom:
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
        
        # 更新光标样式和状态信息
        self.update_cursor_and_status(pos)
        
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
        elif event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            return
            
        event.accept()
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.resize_direction = None
            self.drag_position = None
            print("[鼠标释放] 结束拖拽")
        event.accept()
        
    def update_cursor_and_status(self, pos):
        """更新光标样式和状态信息"""
        if self.resizing:
            return
            
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
        
        # 更新状态信息
        status_text = f"鼠标位置: ({pos.x()}, {pos.y()}) | 窗口大小: {rect.width()}x{rect.height()}\n"
        status_text += f"边框检测 (边框宽度={border_width}px): "
        status_text += f"左={on_left}, 右={on_right}, 上={on_top}, 下={on_bottom}\n"
        
        cursor_name = "普通箭头"
        
        # 设置光标
        if on_top and not (on_left or on_right):
            self.setCursor(Qt.SizeAllCursor)
            cursor_name = "移动光标 ✥"
        elif on_left and on_top or on_right and on_bottom:
            self.setCursor(Qt.SizeFDiagCursor)
            cursor_name = "斜对角光标 ↖↘"
        elif on_right and on_top or on_left and on_bottom:
            self.setCursor(Qt.SizeBDiagCursor)
            cursor_name = "斜对角光标 ↗↙"
        elif on_left or on_right:
            self.setCursor(Qt.SizeHorCursor)
            cursor_name = "水平光标 ↔"
        elif on_bottom:
            self.setCursor(Qt.SizeVerCursor)
            cursor_name = "垂直光标 ↕"
        else:
            self.setCursor(Qt.ArrowCursor)
            cursor_name = "普通箭头"
            
        status_text += f"当前光标: {cursor_name}"
        self.status_label.setText(status_text)
        print(f"[光标更新] {cursor_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BorderDragTestWindow()
    window.show()
    sys.exit(app.exec_())