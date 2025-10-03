#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的设置对话框模块
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QSlider, QSpinBox, QComboBox,
                             QColorDialog, QPushButton, QGroupBox, QCheckBox,
                             QFontComboBox, QGridLayout, QLineEdit,
                             QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

class SettingsDialog(QDialog):
    """设置对话框类"""
    
    # 设置改变信号
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("偏好设置")
        self.setModal(True)
        self.resize(500, 400)
        
        # 主布局
        layout = QVBoxLayout(self)
        
        # 标签页容器
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个设置页面
        self.create_appearance_tab()
        self.create_behavior_tab()
        self.create_shortcuts_tab()
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        self.apply_button = QPushButton("应用")
        
        self.ok_button.clicked.connect(self.accept_settings)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
    def create_appearance_tab(self):
        """创建外观设置页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 透明度设置
        opacity_group = QGroupBox("窗口不透明度")
        opacity_layout = QGridLayout(opacity_group)
        
        opacity_layout.addWidget(QLabel("不透明度:"), 0, 0)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider, 0, 1)
        
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_label, 0, 2)
        
        layout.addWidget(opacity_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout(font_group)
        
        font_layout.addWidget(QLabel("字体:"), 0, 0)
        self.font_combo = QFontComboBox()
        font_layout.addWidget(self.font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("大小:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(6)
        self.font_size_spin.setMaximum(72)
        self.font_size_spin.setValue(12)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        # 极简模式透明度设置
        minimal_group = QGroupBox("极简模式不透明度")
        minimal_layout = QGridLayout(minimal_group)
        
        minimal_layout.addWidget(QLabel("UI不透明度:"), 0, 0)
        self.ui_opacity_slider = QSlider(Qt.Horizontal)
        self.ui_opacity_slider.setMinimum(0)
        self.ui_opacity_slider.setMaximum(100)
        self.ui_opacity_slider.setValue(20)  # 默认20%透明度
        self.ui_opacity_slider.valueChanged.connect(self.on_ui_opacity_changed)
        minimal_layout.addWidget(self.ui_opacity_slider, 0, 1)
        
        self.ui_opacity_label = QLabel("20%")
        minimal_layout.addWidget(self.ui_opacity_label, 0, 2)
        
        minimal_layout.addWidget(QLabel("文字不透明度:"), 1, 0)
        self.text_opacity_slider = QSlider(Qt.Horizontal)
        self.text_opacity_slider.setMinimum(0)
        self.text_opacity_slider.setMaximum(100)
        self.text_opacity_slider.setValue(80)  # 默认80%透明度
        self.text_opacity_slider.valueChanged.connect(self.on_text_opacity_changed)
        minimal_layout.addWidget(self.text_opacity_slider, 1, 1)
        
        self.text_opacity_label = QLabel("80%")
        minimal_layout.addWidget(self.text_opacity_label, 1, 2)
        
        layout.addWidget(minimal_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "外观")
        
        # 存储颜色值
        self.bg_color = QColor(255, 255, 255)
        self.text_color = QColor(0, 0, 0)
        
    def create_behavior_tab(self):
        """创建行为设置页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 自动保存设置
        auto_save_group = QGroupBox("自动保存")
        auto_save_layout = QVBoxLayout(auto_save_group)
        
        self.auto_save_progress_cb = QCheckBox("自动保存阅读进度")
        self.auto_save_progress_cb.setChecked(True)
        auto_save_layout.addWidget(self.auto_save_progress_cb)
        
        layout.addWidget(auto_save_group)
        layout.addStretch()
        self.tab_widget.addTab(widget, "行为")
        
    def create_shortcuts_tab(self):
        """创建快捷键设置页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts_group = QGroupBox("快捷键设置")
        shortcuts_layout = QGridLayout(shortcuts_group)
        
        shortcuts_layout.addWidget(QLabel("F3键:"), 0, 0)
        shortcuts_layout.addWidget(QLabel("切换极简模式"), 0, 1)
        
        shortcuts_layout.addWidget(QLabel("F2键:"), 1, 0)
        shortcuts_layout.addWidget(QLabel("切换文档列表"), 1, 1)
        
        layout.addWidget(shortcuts_group)
        layout.addStretch()
        self.tab_widget.addTab(widget, "快捷键")
        
    def load_current_settings(self):
        """加载当前设置"""
        if not self.current_settings:
            return
            
        # 外观设置 - 加强类型检查和验证
        opacity = self.current_settings.get('opacity', 1.0)
        if isinstance(opacity, str):
            try:
                # 检查是否有重复的值（如 "1.01.01.0..."）
                if opacity.count('.') > 1 or not opacity.strip():
                    opacity = 1.0  # 重置为默认值
                else:
                    opacity = float(opacity)
            except (ValueError, TypeError):
                opacity = 1.0
        elif not isinstance(opacity, (int, float)):
            opacity = 1.0
        self.opacity_slider.setValue(int(opacity * 100))
        
        font_family = self.current_settings.get('font_family', 'Microsoft YaHei')
        index = self.font_combo.findText(font_family)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
            
        font_size = self.current_settings.get('font_size', 12)
        if isinstance(font_size, str):
            try:
                if not font_size.strip() or not font_size.isdigit():
                    font_size = 12
                else:
                    font_size = int(font_size)
            except (ValueError, TypeError):
                font_size = 12
        elif not isinstance(font_size, int):
            font_size = 12
        # 验证字体大小的有效性
        if font_size <= 0 or font_size > 72:
            font_size = 12
        self.font_size_spin.setValue(font_size)
        
        # 加载极简模式透明度设置 - 改为0-100%范围
        ui_opacity = self.current_settings.get('minimal_ui_opacity', 20)  # 默认20%
        if isinstance(ui_opacity, str):
            try:
                if not ui_opacity.strip():
                    ui_opacity = 20
                else:
                    ui_opacity = int(float(ui_opacity))  # 支持浮点数转换
            except (ValueError, TypeError):
                ui_opacity = 20
        elif not isinstance(ui_opacity, (int, float)):
            ui_opacity = 20
        # 验证范围 0-100%
        if ui_opacity < 0 or ui_opacity > 100:
            ui_opacity = 20
        self.ui_opacity_slider.setValue(ui_opacity)
        
        text_opacity = self.current_settings.get('minimal_text_opacity', 80)  # 默认80%
        if isinstance(text_opacity, str):
            try:
                if not text_opacity.strip():
                    text_opacity = 80
                else:
                    text_opacity = int(float(text_opacity))  # 支持浮点数转换
            except (ValueError, TypeError):
                text_opacity = 80
        elif not isinstance(text_opacity, (int, float)):
            text_opacity = 80
        # 验证范围 0-100%
        if text_opacity < 0 or text_opacity > 100:
            text_opacity = 80
        self.text_opacity_slider.setValue(text_opacity)
        
    def on_opacity_changed(self, value):
        """不透明度改变事件"""
        self.opacity_label.setText(f"{value}%")
        
    def on_ui_opacity_changed(self, value):
        """极简模式UI不透明度改变事件"""
        self.ui_opacity_label.setText(f"{value}%")
        
    def on_text_opacity_changed(self, value):
        """极简模式文字不透明度改变事件"""
        self.text_opacity_label.setText(f"{value}%")
        
    def get_settings(self):
        """获取当前设置"""
        settings = {
            'opacity': self.opacity_slider.value() / 100.0,
            'font_family': self.font_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'minimal_ui_opacity': self.ui_opacity_slider.value(),
            'minimal_text_opacity': self.text_opacity_slider.value(),
            'auto_save_progress': self.auto_save_progress_cb.isChecked()
        }
        return settings
        
    def apply_settings(self):
        """应用设置"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        
    def accept_settings(self):
        """确认设置"""
        self.apply_settings()
        self.accept()