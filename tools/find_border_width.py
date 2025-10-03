#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 查找所有设置resize_border_width的地方
with open('src/main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("所有设置resize_border_width的地方:")
for i, line in enumerate(lines):
    if 'resize_border_width' in line and '=' in line and not line.strip().startswith('#'):
        print(f"{i+1}: {line.strip()}")

print("\n所有设置_resize_border_width为具体值的地方:")
for i, line in enumerate(lines):
    if '_resize_border_width =' in line and not line.strip().startswith('#'):
        print(f"{i+1}: {line.strip()}")