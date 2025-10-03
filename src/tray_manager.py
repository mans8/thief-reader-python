#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘管理器模块
"""

import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

class TrayManager(QObject):
    """系统托盘管理器类"""
    
    # 信号
    show_window_signal = pyqtSignal()
    quit_application_signal = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.tray_icon = None
        
        # 检查系统是否支持托盘图标
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统托盘不可用")
            return
            
        self.create_tray_icon()
        
    def create_tray_icon(self):
        """创建托盘图标"""
        try:
            # 创建托盘图标
            self.tray_icon = QSystemTrayIcon(self)
            
            # 设置图标
            icon = self.create_icon()
            self.tray_icon.setIcon(icon)
            
            # 设置提示文本
            self.tray_icon.setToolTip("技术文档阅读器 - 双击显示/隐藏")
            
            # 创建右键菜单
            self.create_context_menu()
            
            # 连接信号
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            
            # 显示托盘图标
            self.tray_icon.show()
            
        except Exception as e:
            print(f"创建托盘图标时出错: {e}")
            
    def create_icon(self):
        """创建应用图标 - 使用logo.png"""
        # 尝试加载logo.png文件作为图标
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            # 如果logo.png不存在，则使用原来的绘制图标
            # 创建一个类似谷歌浏览器的圆形图标
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 绘制外圈 - 蓝色
            painter.setBrush(QColor(66, 133, 244))  # 谷歌蓝
            painter.setPen(QColor(32, 33, 36))      # 深灰色边框
            painter.drawEllipse(1, 1, 14, 14)
            
            # 绘制内圈 - 红色
            painter.setBrush(QColor(234, 67, 53))   # 谷歌红
            painter.setPen(QColor(0, 0, 0, 0))      # 透明边框
            painter.drawEllipse(4, 4, 8, 8)
            
            # 绘制中心白色圆点
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(6, 6, 4, 4)
            
            # 绘制一些装饰线条
            painter.setBrush(QColor(52, 168, 83))   # 谷歌绿
            painter.drawEllipse(2, 6, 3, 4)
            
            painter.setBrush(QColor(251, 188, 5))   # 谷歌黄
            painter.drawEllipse(11, 6, 3, 4)
            
            painter.end()
            
            return QIcon(pixmap)
        
    def create_context_menu(self):
        """创建托盘右键菜单"""
        menu = QMenu()
        
        # 显示/隐藏主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_main_window)
        menu.addAction(show_action)
        
        # 分隔符
        menu.addSeparator()
        
        # 打开文档
        open_action = QAction("打开文档", self)
        open_action.triggered.connect(self.main_window.open_document)
        menu.addAction(open_action)
        
        # 分隔符
        menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.main_window.open_preferences)
        menu.addAction(settings_action)
        
        # 分隔符
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        # 设置菜单
        if self.tray_icon:
            self.tray_icon.setContextMenu(menu)
        
    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_main_window()
        elif reason == QSystemTrayIcon.Trigger:
            # 单击时显示菜单（在某些系统上）
            pass
            
    def toggle_main_window(self):
        """切换主窗口显示状态"""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.show_main_window()
            
    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
        # 如果窗口最小化，恢复它
        if self.main_window.isMinimized():
            self.main_window.showNormal()
            
    def hide_main_window(self):
        """隐藏主窗口"""
        self.main_window.hide()
        
    def quit_application(self):
        """退出应用程序"""
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()
        
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, timeout=3000):
        """显示托盘消息 - 已禁用以提高隐蔽性"""
        # 为了提高隐蔽性，不显示任何弹窗通知
        pass
            
    def is_available(self):
        """检查托盘是否可用"""
        return QSystemTrayIcon.isSystemTrayAvailable()
        
    def update_tooltip(self, text):
        """更新托盘图标提示文本"""
        if self.tray_icon:
            self.tray_icon.setToolTip(f"技术文档阅读器 - {text}")