#!/usr/bin/env python3
"""修复异步调用"""
import os
import re

commands_dir = os.path.dirname(os.path.abspath(__file__)) + '/commands'

for filename in os.listdir(commands_dir):
    if not filename.endswith('.py') or filename == '__init__.py':
        continue
    
    filepath = os.path.join(commands_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加 asyncio 导入
    if 'import asyncio' not in content:
        content = 'import asyncio\n' + content
    
    # 包装 api_client 调用
    content = re.sub(
        r'(?<!asyncio\.run\()api_client\.([a-z_]+)\(',
        r'asyncio.run(api_client.\1(',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filename}")

print("Done!")
