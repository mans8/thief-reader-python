#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档阅读器模块
支持PDF、Markdown、TXT格式的文档阅读
"""

import os
import PyPDF2
import markdown
from PyQt5.QtCore import QObject

class DocumentReader(QObject):
    """文档阅读器类"""
    
    def __init__(self):
        super().__init__()
        
    def read_document(self, file_path):
        """
        读取文档内容
        
        Args:
            file_path (str): 文档路径
            
        Returns:
            str: 文档内容，失败返回None
        """
        if not os.path.exists(file_path):
            return None
            
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self._read_pdf(file_path)
            elif file_ext == '.md':
                return self._read_markdown(file_path)
            elif file_ext == '.txt':
                return self._read_text(file_path)
            else:
                return None
        except Exception as e:
            print(f"读取文档时出错: {e}")
            return None
            
    def _read_pdf(self, file_path):
        """读取PDF文件"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        content.append(f"--- 第 {page_num + 1} 页 ---\n")
                        content.append(text)
                        content.append("\n\n")
                
                return ''.join(content)
                
        except Exception as e:
            raise Exception(f"PDF读取错误: {e}")
            
    def _read_markdown(self, file_path):
        """读取Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                
            # 转换为HTML并返回纯文本版本
            html = markdown.markdown(md_content, extensions=['codehilite', 'fenced_code', 'tables'])
            
            # 添加基本的CSS样式
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{ 
                        font-family: 'Microsoft YaHei', Arial, sans-serif; 
                        line-height: 1.6; 
                        color: #333; 
                        max-width: 100%; 
                        margin: 0;
                        padding: 20px;
                        background-color: transparent;
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        color: #2c3e50; 
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    h1 {{ font-size: 1.8em; border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #bdc3c7; padding-bottom: 0.3em; }}
                    h3 {{ font-size: 1.3em; color: #34495e; }}
                    code {{ 
                        background-color: #f8f9fa; 
                        padding: 2px 4px; 
                        border-radius: 3px; 
                        font-family: 'Consolas', 'Monaco', monospace;
                        color: #e74c3c;
                    }}
                    pre {{ 
                        background-color: #f8f9fa; 
                        padding: 15px; 
                        border-radius: 5px; 
                        overflow-x: auto;
                        border-left: 4px solid #3498db;
                    }}
                    pre code {{ 
                        background-color: transparent; 
                        padding: 0;
                        color: #2c3e50;
                    }}
                    blockquote {{ 
                        border-left: 4px solid #bdc3c7; 
                        margin: 1.5em 0; 
                        padding-left: 1em; 
                        color: #7f8c8d;
                        font-style: italic;
                    }}
                    ul, ol {{ margin: 1em 0; padding-left: 2em; }}
                    li {{ margin: 0.5em 0; }}
                    table {{ 
                        border-collapse: collapse; 
                        width: 100%; 
                        margin: 1em 0;
                    }}
                    th, td {{ 
                        border: 1px solid #bdc3c7; 
                        padding: 8px 12px; 
                        text-align: left;
                    }}
                    th {{ 
                        background-color: #ecf0f1; 
                        font-weight: bold;
                    }}
                    a {{ color: #3498db; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    strong {{ color: #2c3e50; }}
                    em {{ color: #7f8c8d; }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            return styled_html
            
        except Exception as e:
            raise Exception(f"Markdown读取错误: {e}")
            
    def _read_text(self, file_path):
        """读取文本文件"""
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
                    
            # 如果所有编码都失败，使用错误处理
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
                
        except Exception as e:
            raise Exception(f"文本文件读取错误: {e}")
            
    def get_supported_formats(self):
        """获取支持的文件格式"""
        return ['.pdf', '.md', '.txt']
        
    def is_supported_format(self, file_path):
        """检查是否为支持的文件格式"""
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.get_supported_formats()