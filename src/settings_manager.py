#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理器模块
负责应用设置的保存和加载
"""

import os
import configparser
from PyQt5.QtCore import QObject

class SettingsManager(QObject):
    """设置管理器类"""
    
    def __init__(self):
        super().__init__()
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "settings.ini")
        self.progress_file = os.path.join(self.config_dir, "progress.ini")
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 默认设置
        self.default_settings = {
            'window': {
                'opacity': '1.0',
                'width': '1000',
                'height': '700',
                'x': '100',
                'y': '100',
                'stay_on_top': 'False',
                'maximized': 'False'
            },
            'appearance': {
                'font_family': 'Microsoft YaHei',
                'font_size': '12',
                'bg_color': '#ffffff',
                'text_color': '#000000',
                'theme': 'light'
            },
            'minimal_mode': {
                'minimal_ui_opacity': '20',        # 极简模式UI透明度 (0-100%)
                'minimal_text_opacity': '80'       # 极简模式文字透明度 (0-100%)
            },
            'behavior': {
                'auto_save_progress': 'True',
                'show_page_numbers': 'True',
                'remember_window_position': 'True',
                'boss_key': 'Ctrl+Shift+H'
            },
            'recent': {
                'max_recent_files': '10'
            }
        }
        
    def load_settings(self):
        """加载设置"""
        config = configparser.ConfigParser()
        
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_file):
            self._create_default_config()
            
        try:
            config.read(self.config_file, encoding='utf-8')
            settings = {}
            
            # 读取所有设置
            for section_name in self.default_settings:
                if config.has_section(section_name):
                    for key, default_value in self.default_settings[section_name].items():
                        if config.has_option(section_name, key):
                            value = config.get(section_name, key)
                            # 类型转换
                            settings[key] = self._convert_value(value, default_value)
                        else:
                            settings[key] = self._convert_value(default_value, default_value)
                else:
                    # 如果段不存在，使用默认值
                    for key, default_value in self.default_settings[section_name].items():
                        settings[key] = self._convert_value(default_value, default_value)
                        
            # 加载最近文档列表
            recent_files = []
            if config.has_section('recent_files'):
                for i in range(int(settings.get('max_recent_files', 10))):
                    key = f'file_{i}'
                    if config.has_option('recent_files', key):
                        file_path = config.get('recent_files', key)
                        if os.path.exists(file_path):
                            recent_files.append(file_path)
                            
            settings['recent_files'] = recent_files
            
            return settings
            
        except Exception as e:
            print(f"加载设置时出错: {e}")
            return self._get_default_settings_dict()
            
    def save_settings(self, settings):
        """保存设置"""
        try:
            config = configparser.ConfigParser()
            
            # 创建各个段
            for section_name in self.default_settings:
                config.add_section(section_name)
                
            # 保存窗口设置
            if 'window_geometry' in settings:
                geometry = settings['window_geometry']
                config.set('window', 'x', str(geometry[0]))
                config.set('window', 'y', str(geometry[1]))
                config.set('window', 'width', str(geometry[2]))
                config.set('window', 'height', str(geometry[3]))
                
            # 保存其他设置
            for key, value in settings.items():
                if key == 'recent_files':
                    continue
                elif key == 'window_geometry':
                    continue
                else:
                    # 根据键名确定要保存到哪个段
                    section = self._get_section_for_key(key)
                    if section:
                        config.set(section, key, str(value))
                        
            # 保存最近文档
            if 'recent_files' in settings:
                if not config.has_section('recent_files'):
                    config.add_section('recent_files')
                    
                recent_files = settings['recent_files']
                for i, file_path in enumerate(recent_files):
                    config.set('recent_files', f'file_{i}', file_path)
                    
            # 写入文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            print(f"保存设置时出错: {e}")
            
    def save_reading_progress(self, file_path, position):
        """保存阅读进度"""
        try:
            config = configparser.ConfigParser()
            
            # 读取现有进度文件
            if os.path.exists(self.progress_file):
                config.read(self.progress_file, encoding='utf-8')
                
            # 确保有progress段
            if not config.has_section('progress'):
                config.add_section('progress')
                
            # 保存进度（使用文件路径的hash作为键）
            import hashlib
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            config.set('progress', file_hash, f"{file_path}|{position}")
            
            # 写入文件
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            print(f"保存阅读进度时出错: {e}")
            
    def get_reading_position(self, file_path):
        """获取阅读进度"""
        try:
            if not os.path.exists(self.progress_file):
                return 0
                
            config = configparser.ConfigParser()
            config.read(self.progress_file, encoding='utf-8')
            
            if not config.has_section('progress'):
                return 0
                
            import hashlib
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            
            if config.has_option('progress', file_hash):
                progress_data = config.get('progress', file_hash)
                parts = progress_data.split('|')
                if len(parts) == 2 and parts[0] == file_path:
                    return int(parts[1])
                    
            return 0
            
        except Exception as e:
            print(f"获取阅读进度时出错: {e}")
            return 0
            
    def _create_default_config(self):
        """创建默认配置文件"""
        config = configparser.ConfigParser()
        
        # 添加默认设置
        for section_name, section_data in self.default_settings.items():
            config.add_section(section_name)
            for key, value in section_data.items():
                config.set(section_name, key, str(value))
                
        # 写入文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
            
    def _get_default_settings_dict(self):
        """获取默认设置字典"""
        settings = {}
        for section_data in self.default_settings.values():
            for key, value in section_data.items():
                settings[key] = self._convert_value(value, value)
        settings['recent_files'] = []
        return settings
        
    def _convert_value(self, value, default_value):
        """类型转换"""
        # 处理字符串值
        if isinstance(value, str) and value.strip() == '':
            # 如果是空字符串，使用默认值
            value = default_value
            
        if isinstance(default_value, str):
            return str(value)
        elif str(default_value).lower() in ['true', 'false']:
            return str(value).lower() == 'true'
        elif '.' in str(default_value):
            try:
                # 确保是有效的浮点数字符串
                float_val = float(str(value))
                return float_val
            except (ValueError, TypeError):
                try:
                    return float(str(default_value))
                except (ValueError, TypeError):
                    return 1.0  # 透明度默认值
        else:
            try:
                return int(value)
            except (ValueError, TypeError):
                # 如果转换失败，尝试从默认值获取
                try:
                    return int(str(default_value))
                except (ValueError, TypeError):
                    return 12 if 'font_size' in str(default_value) else 0
                
    def _get_section_for_key(self, key):
        """根据键名获取对应的配置段"""
        for section_name, section_data in self.default_settings.items():
            if key in section_data:
                return section_name
        return None