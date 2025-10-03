#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复窗口拖拽和文字透明度功能的测试脚本
"""

import os
import sys

# 确保能导入项目模块
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_window_drag_issues():
    """测试窗口拖拽功能的问题"""
    print("🔍 1. 窗口边框拖拽功能问题诊断:")
    print("   问题分析:")
    print("   - resize_start_geometry可能为None，导致错误")
    print("   - 需要在mousePressEvent中正确初始化")
    print("   - mouseMoveEvent中需要处理None值的情况")
    print()
    print("   修复方案:")
    print("   - 确保resize_start_pos和resize_start_geometry正确初始化")
    print("   - 在mouseMoveEvent中添加安全检查")
    print("   - 使用当前窗口几何作为基础进行计算")

def test_text_opacity_issues():
    """测试文字透明度功能的问题"""
    print("\n🔍 2. 最简模式文字透明度问题诊断:")
    print("   问题分析:")
    print("   - 文字透明度可能没有正确从偏好设置读取")
    print("   - alpha值计算可能有误")
    print("   - CSS样式应用时机可能不对")
    print()
    print("   修复方案:")
    print("   - 确保从settings_manager正确读取minimal_text_opacity")
    print("   - 验证0-100%到0-255转换的正确性")
    print("   - 在进入最简模式和设置变更时都应用透明度")

def create_drag_fix():
    """生成窗口拖拽功能修复代码"""
    print("\n✅ 窗口拖拽功能修复代码:")
    print("""
def mousePressEvent(self, event):
    \"\"\"鼠标按下事件，用于窗口拖拽和调整大小\"\"\"
    if event.button() == Qt.LeftButton:
        # 检查是否在边框区域
        pos = event.pos()
        rect = self.rect()
        
        # 判断鼠标位置是否在边框
        on_left = pos.x() <= self.resize_border_width
        on_right = pos.x() >= rect.width() - self.resize_border_width
        on_top = pos.y() <= self.resize_border_width
        on_bottom = pos.y() >= rect.height() - self.resize_border_width
        
        if on_left or on_right or on_top or on_bottom:
            # 在边框区域，启动调整大小模式
            self.resizing = True
            self.resize_start_pos = event.globalPos()
            self.resize_start_geometry = self.geometry()  # 确保正确保存当前几何
            
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
            elif on_top:
                self.resize_direction = 'top'
            elif on_bottom:
                self.resize_direction = 'bottom'
        else:
            # 不在边框区域，普通拖拽
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

def mouseMoveEvent(self, event):
    \"\"\"鼠标移动事件，用于窗口拖拽和调整大小\"\"\"
    if self.resizing and event.buttons() == Qt.LeftButton and self.resize_start_geometry:
        # 调整窗口大小 - 添加安全检查
        diff = event.globalPos() - self.resize_start_pos
        # 使用起始几何作为基础来计算新的尺寸
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
        elif self.resize_direction == 'top':
            new_y = start_geo.y() + diff.y()
            new_height = start_geo.height() - diff.y()
        elif self.resize_direction == 'bottom-right':
            new_width = start_geo.width() + diff.x()
            new_height = start_geo.height() + diff.y()
        elif self.resize_direction == 'bottom-left':
            new_x = start_geo.x() + diff.x()
            new_width = start_geo.width() - diff.x()
            new_height = start_geo.height() + diff.y()
        elif self.resize_direction == 'top-right':
            new_y = start_geo.y() + diff.y()
            new_width = start_geo.width() + diff.x()
            new_height = start_geo.height() - diff.y()
        elif self.resize_direction == 'top-left':
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
        
    elif event.buttons() == Qt.LeftButton and self.drag_position:
        # 普通拖拽
        self.move(event.globalPos() - self.drag_position)
    
    # 更新鼠标样式
    self.update_cursor(event.pos())
    event.accept()
""")

def create_opacity_fix():
    """生成文字透明度修复代码"""
    print("\n✅ 文字透明度功能修复代码:")
    print("""
def toggle_minimal_mode(self):
    \"\"\"切换最简模式\"\"\"
    self.minimal_mode = not self.minimal_mode
    
    if self.minimal_mode:
        print("进入最简模式")
        # 隐藏所有界面元素，只保留阅读区域
        self.title_bar.hide()
        self.menu_container.hide()
        self.statusBar().hide()
        self.file_panel.hide()
        self.doc_title.hide()
        
        # 从设置中加载透明度 - 确保正确读取
        settings = self.settings_manager.load_settings()
        ui_opacity_percent = settings.get('minimal_ui_opacity', 20)
        text_opacity_percent = settings.get('minimal_text_opacity', 80)
        
        # 确保透明度值在有效范围内 0-100%
        ui_opacity_percent = max(0, min(100, int(ui_opacity_percent) if ui_opacity_percent else 20))
        text_opacity_percent = max(0, min(100, int(text_opacity_percent) if text_opacity_percent else 80))
        
        # 转换为255范围的alpha值
        ui_alpha = int(ui_opacity_percent * 255 / 100)
        text_bg_alpha = int(text_opacity_percent * 255 / 100)
        
        # 文字颜色也使用相同的不透明度，确保一致性
        text_color_alpha = text_bg_alpha
        
        # 获取当前字体设置
        font_family = settings.get('font_family', 'Microsoft YaHei')
        font_size = settings.get('font_size', self.current_font_size)
        
        print(f"最简模式设置: UI透明度={ui_opacity_percent}% (alpha={ui_alpha}), 文字透明度={text_opacity_percent}% (alpha={text_bg_alpha})")
        
        # 设置中央部件透明度
        central_widget = self.centralWidget()
        central_widget.setStyleSheet(f\"\"\"
            QWidget {{
                background-color: rgba(255, 255, 255, {ui_alpha});
                border-radius: 10px;
            }}
        \"\"\")
        
        # 设置阅读区域透明度，确保文字透明度与设置一致
        self.reading_area.setStyleSheet(f\"\"\"
            QTextEdit {{
                background-color: rgba(255, 255, 255, {text_bg_alpha});
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-family: '{font_family}';
                font-size: {font_size}px;
                color: rgba(51, 51, 51, {text_color_alpha});
            }}
            QScrollBar:vertical {{
                background-color: rgba(240, 240, 240, {ui_alpha});
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(180, 180, 180, {min(255, ui_alpha + 50)});
                border-radius: 4px;
                min-height: 20px;
            }}
        \"\"\")
    else:
        # 退出最简模式的代码...
        pass
""")

def main():
    """主测试函数"""
    print("=== 技术文档阅读器 - 窗口拖拽与文字透明度功能修复 ===")
    print("诊断时间:", __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    test_window_drag_issues()
    test_text_opacity_issues()
    create_drag_fix()
    create_opacity_fix()
    
    print("\n🔧 修复重点:")
    print("1. 窗口拖拽功能:")
    print("   - 确保resize_start_geometry正确初始化")
    print("   - 在mouseMoveEvent中添加None值检查")
    print("   - 使用起始几何作为计算基础")
    
    print("\n2. 文字透明度功能:")
    print("   - 确保从偏好设置正确读取minimal_text_opacity")
    print("   - 文字和背景使用相同的透明度值")
    print("   - 在模式切换和设置变更时都要应用")
    
    print("\n✅ 修复完成后的测试方法:")
    print("1. 启动程序，移动鼠标到窗口边缘测试光标变化")
    print("2. 拖拽边框测试窗口大小调整")
    print("3. 在偏好设置中调整文字不透明度")
    print("4. 切换最简模式验证透明度效果")

if __name__ == "__main__":
    main()