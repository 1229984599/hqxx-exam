#!/usr/bin/env python3
"""
创建正确的田字格模板 - 一行两个田字格，居中显示，可快速修改颜色
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

def create_tianzige_row(char1, char2, grid_color="#333", text_color="#000"):
    """创建一行两个田字格"""
    return f'''
<div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 30px;">
    <!-- 第一个田字格 -->
    <div class="tianzige-container" style="position: relative;">
        <div class="tianzige" style="width: 80px; height: 80px; border: 3px solid {grid_color}; position: relative; background: white; display: flex; align-items: center; justify-content: center;">
            <!-- 十字辅助线 -->
            <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: {grid_color}; opacity: 0.5;"></div>
            <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: {grid_color}; opacity: 0.5;"></div>
            <!-- 汉字 -->
            <span class="tianzige-char" style="font-size: 36px; font-weight: bold; color: {text_color}; font-family: '楷体', 'KaiTi', serif; user-select: text;" contenteditable="true">{char1}</span>
        </div>
    </div>
    
    <!-- 第二个田字格 -->
    <div class="tianzige-container" style="position: relative;">
        <div class="tianzige" style="width: 80px; height: 80px; border: 3px solid {grid_color}; position: relative; background: white; display: flex; align-items: center; justify-content: center;">
            <!-- 十字辅助线 -->
            <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: {grid_color}; opacity: 0.5;"></div>
            <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: {grid_color}; opacity: 0.5;"></div>
            <!-- 汉字 -->
            <span class="tianzige-char" style="font-size: 36px; font-weight: bold; color: {text_color}; font-family: '楷体', 'KaiTi', serif; user-select: text;" contenteditable="true">{char2}</span>
        </div>
    </div>
</div>'''

def create_color_controls():
    """创建颜色控制面板"""
    return '''
<div style="background: #f8f9fa; border: 2px dashed #dee2e6; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
    <h4 style="margin: 0 0 15px 0; color: #495057; font-size: 16px;">🎨 快速颜色设置</h4>
    <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <!-- 田字格颜色 -->
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 14px; color: #6c757d;">田字格：</span>
            <button onclick="changeGridColor('#333')" style="width: 30px; height: 30px; background: #333; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="黑色"></button>
            <button onclick="changeGridColor('#dc3545')" style="width: 30px; height: 30px; background: #dc3545; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="红色"></button>
            <button onclick="changeGridColor('#007bff')" style="width: 30px; height: 30px; background: #007bff; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="蓝色"></button>
            <button onclick="changeGridColor('#28a745')" style="width: 30px; height: 30px; background: #28a745; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="绿色"></button>
        </div>
        
        <!-- 文字颜色 -->
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 14px; color: #6c757d;">文字：</span>
            <button onclick="changeTextColor('#000')" style="width: 30px; height: 30px; background: #000; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="黑色"></button>
            <button onclick="changeTextColor('#dc3545')" style="width: 30px; height: 30px; background: #dc3545; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="红色"></button>
            <button onclick="changeTextColor('#007bff')" style="width: 30px; height: 30px; background: #007bff; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="蓝色"></button>
            <button onclick="changeTextColor('#28a745')" style="width: 30px; height: 30px; background: #28a745; border: 2px solid #fff; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" title="绿色"></button>
        </div>
    </div>
    <p style="margin: 10px 0 0 0; font-size: 12px; color: #6c757d;">💡 点击颜色按钮快速更改田字格和文字颜色，双击文字可直接编辑</p>
</div>

<script>
function changeGridColor(color) {
    const grids = document.querySelectorAll('.tianzige');
    const lines = document.querySelectorAll('.tianzige > div');
    grids.forEach(grid => {
        grid.style.borderColor = color;
    });
    lines.forEach(line => {
        line.style.background = color;
    });
}

function changeTextColor(color) {
    const chars = document.querySelectorAll('.tianzige-char');
    chars.forEach(char => {
        char.style.color = color;
    });
}
</script>'''

def create_correct_template():
    """创建正确的田字格模板"""
    
    # 词汇对列表
    word_pairs = [
        ("你", "我"), ("耳", "目"), ("日", "月"), ("爸", "妈"), ("数", "学"),
        ("马", "路"), ("星", "星"), ("春", "天"), ("开", "关"), ("书", "包"),
        ("雨", "点"), ("金", "色"), ("青", "蛙"), ("桌", "子"), ("男", "女"),
        ("夏", "天"), ("树", "叶"), ("许", "多"), ("地", "方"), ("乌", "鸦"),
        ("拼", "音"), ("影", "子"), ("到", "处"), ("出", "去"), ("先", "后"),
        ("宝", "贝"), ("草", "原"), ("学", "校"), ("黑", "狗"), ("看", "见")
    ]
    
    # 开始构建HTML
    template_content = '''
<div style="font-family: '宋体', 'SimSun', serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h2 style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 30px; color: #333; border-bottom: 3px solid #333; padding-bottom: 15px;">一、"字"得其乐</h2>
'''
    
    # 添加颜色控制面板
    template_content += create_color_controls()
    
    # 添加田字格行
    for i, (char1, char2) in enumerate(word_pairs):
        if i % 5 == 0:  # 每5行添加一个分组标题
            group_num = i // 5 + 1
            template_content += f'''
    <div style="margin: 40px 0 20px 0;">
        <h3 style="font-size: 18px; font-weight: bold; color: #666; text-align: center;">{group_num}.</h3>
    </div>'''
        
        template_content += create_tianzige_row(char1, char2)
    
    # 添加说明
    template_content += '''
    <div style="margin-top: 40px; padding: 20px; background: #e8f4fd; border-radius: 8px; border-left: 4px solid #007bff;">
        <h4 style="margin: 0 0 10px 0; color: #007bff; font-size: 16px;">📖 使用说明</h4>
        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
            <li>每行显示两个田字格，每个田字格中有一个汉字</li>
            <li>双击汉字可以直接编辑修改</li>
            <li>使用上方的颜色按钮可以快速更改田字格边框和文字颜色</li>
            <li>田字格中的十字线帮助学生掌握汉字的结构和笔画位置</li>
            <li>适合打印后让学生临摹练习</li>
        </ul>
    </div>
</div>'''
    
    return template_content

def add_correct_tianzige_template():
    """添加正确的田字格模板"""
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，退出")
        return
    
    # 创建模板内容
    template_content = create_correct_template()
    
    # 通过API创建模板
    api_url = "http://localhost:8000/api/v1/templates/"
    
    template_data = {
        "name": "田字格练习模板（标准版）",
        "description": "一行两个田字格，居中显示，支持快速修改颜色和编辑文字，适用于汉字书写练习",
        "content": template_content,
        "category": "教学模板",
        "icon": "📝",
        "is_active": True,
        "sort_order": 0
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=template_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"标准田字格模板创建成功！ID: {result['id']}")
        else:
            print(f"创建模板失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"创建模板失败: {e}")

if __name__ == "__main__":
    add_correct_tianzige_template()
