#!/usr/bin/env python3
"""
创建完整的田字格模板，包含所有三组词汇
"""

import requests
import json

def get_auth_token():
    """获取认证token"""
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            result = response.json()
            return result.get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def create_tianzige_for_word(word, show_example=True):
    """为单个词汇创建田字格HTML"""
    chars = list(word)
    html = f'<div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">'
    html += f'<span style="min-width: 40px; font-weight: bold;">{word}</span>'
    
    # 为每个字符创建田字格
    for i, char in enumerate(chars):
        # 示例田字格（带字符）
        if show_example:
            html += f'''
            <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">{char}</span>
            </div>'''
        
        # 练习田字格（空白）
        html += f'''
        <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
            <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
            <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
        </div>'''
    
    # 额外的练习田字格
    for _ in range(2):
        html += f'''
        <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
            <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
            <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
        </div>'''
    
    html += '</div>'
    return html

def create_complete_template():
    """创建完整的田字格模板"""
    
    # 所有词汇分组
    word_groups = [
        {
            "title": "1.",
            "words": ["你我", "耳目", "日月", "爸妈", "数学", "马路", "星星", "春天", "开关", "书包"]
        },
        {
            "title": "2.",
            "words": ["雨点", "金色", "青蛙", "桌子", "男女", "夏天", "树叶", "许多", "地方", "乌鸦"]
        },
        {
            "title": "3.",
            "words": ["拼音", "影子", "到处", "出去", "先后", "宝贝", "草原", "学校", "黑狗", "看见"]
        }
    ]
    
    # 开始构建HTML
    template_content = '''
<div style="font-family: 'SimSun', '宋体', serif; line-height: 2.5; padding: 20px; max-width: 1200px; margin: 0 auto;">
    <h2 style="text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 10px;">一、"字"得其乐</h2>
'''
    
    # 为每组词汇创建田字格
    for group in word_groups:
        template_content += f'''
    <div style="margin-bottom: 40px;">
        <div style="display: flex; align-items: flex-start; margin-bottom: 25px; font-size: 16px;">
            <div style="width: 30px; font-weight: bold; color: #666; margin-top: 20px;">{group["title"]}</div>
            <div style="flex: 1;">
'''
        
        # 为每个词汇创建田字格
        for word in group["words"]:
            template_content += create_tianzige_for_word(word, show_example=True)
        
        template_content += '''
            </div>
        </div>
    </div>
'''
    
    # 添加说明
    template_content += '''
    <p style="margin-top: 30px; font-size: 14px; color: #666; text-align: center;">
        <strong>使用说明：</strong>每个汉字都有对应的田字格，浅色字为示例，学生可以在空白田字格中练习书写。每个词汇提供示例字和多个练习格。
    </p>
</div>
'''
    
    return template_content

def add_complete_tianzige_template():
    """添加完整的田字格模板"""
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，退出")
        return
    
    # 创建模板内容
    template_content = create_complete_template()
    
    # 通过API创建模板
    api_url = "http://localhost:8000/api/v1/templates/"
    
    template_data = {
        "name": "语文田字格练习模板（完整版）",
        "description": "包含完整的三组词汇练习，每个汉字都有示例字和练习田字格，适用于小学语文汉字书写练习",
        "content": template_content,
        "category": "教学模板",
        "icon": "📝",
        "is_active": True,
        "sort_order": 1
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=template_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"完整田字格模板创建成功！ID: {result['id']}")
        else:
            print(f"创建模板失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"创建模板失败: {e}")

if __name__ == "__main__":
    add_complete_tianzige_template()
