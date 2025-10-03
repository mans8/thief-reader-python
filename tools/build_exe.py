#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 使用PyInstaller打包应用程序
"""

import os
import sys
import subprocess

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller 安装完成")

def build_executable():
    """构建可执行文件"""
    print("开始打包应用程序...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 单文件打包
        "--windowed",                   # 无控制台窗口
        "--name=摸鱼看文档",            # 可执行文件名
        "--icon=icon.ico",              # 图标文件（如果有的话）
        "--add-data=config;config",     # 包含配置目录
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyPDF2",
        "--hidden-import=markdown",
        "main.py"
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        print("可执行文件位置: dist/摸鱼看文档.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        
    except FileNotFoundError:
        print("错误: 找不到 pyinstaller 命令")
        print("请确保已正确安装 PyInstaller")

def create_icon():
    """创建简单的图标文件"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的图标
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制一个简单的书本图标
        draw.rectangle([10, 15, 54, 50], fill='steelblue', outline='darkblue', width=2)
        draw.line([32, 15, 32, 50], fill='darkblue', width=2)
        draw.line([10, 32, 54, 32], fill='darkblue', width=1)
        
        # 保存为ICO文件
        img.save('icon.ico', format='ICO')
        print("图标文件创建成功: icon.ico")
        
    except ImportError:
        print("警告: 无法创建图标文件，需要安装 Pillow")
        print("跳过图标创建...")

def main():
    """主函数"""
    print("摸鱼看文档软件打包工具")
    print("=" * 40)
    
    # 检查是否在正确的目录
    if not os.path.exists("main.py"):
        print("错误: 找不到 main.py 文件")
        print("请在项目根目录运行此脚本")
        return
        
    # 安装PyInstaller
    install_pyinstaller()
    
    # 创建图标
    create_icon()
    
    # 构建可执行文件
    build_executable()
    
    print("\n打包完成！")
    print("注意事项：")
    print("1. 首次运行时会创建配置文件")
    print("2. 建议将exe文件放在独立文件夹中")
    print("3. 如果遇到问题，请检查Python和PyQt5安装是否正确")

if __name__ == "__main__":
    main()