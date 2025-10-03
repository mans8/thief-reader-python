#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摸鱼看文档软件 - 主程序入口
作者: Qoder AI
描述: 一个隐蔽的文档阅读器，支持PDF、Markdown、TXT格式
"""

import sys
import os
import socket
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main_window import MainWindow

class SingleInstanceApp:
    """单实例应用程序类"""
    
    def __init__(self, port=12345):
        self.port = port
        self.socket = None
        
    def is_running(self):
        """检查是否已有实例运行"""
        try:
            # 尝试绑定端口
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('127.0.0.1', self.port))
            self.socket.listen(1)
            return False  # 没有其他实例运行
        except OSError:
            return True   # 已有实例运行
            
    def cleanup(self):
        """清理资源"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def main():
    """主函数"""
    # 检查单实例
    single_instance = SingleInstanceApp()
    
    if single_instance.is_running():
        # 已有实例运行，直接退出不显示任何提示
        single_instance.cleanup()
        return
    
    try:
        # 创建应用实例
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 设置应用信息
        app.setApplicationName("技术文档阅读器")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TechnicalReader")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 启动事件循环
        result = app.exec_()
        
    finally:
        # 清理资源
        single_instance.cleanup()
        
    sys.exit(result)

if __name__ == "__main__":
    main()