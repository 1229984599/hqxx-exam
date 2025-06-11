#!/usr/bin/env python3
"""
添加田字格模板到数据库的脚本
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

def add_tianzige_template():
    """添加田字格模板"""
    
    # 田字格模板的HTML内容 - 每个汉字对应一个田字格
    template_content = '''
<div style="font-family: 'SimSun', '宋体', serif; line-height: 2.5; padding: 20px; max-width: 1000px; margin: 0 auto;">
    <h2 style="text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 10px;">一、"字"得其乐</h2>

    <!-- 第1组练习 -->
    <div style="margin-bottom: 40px;">
        <div style="display: flex; align-items: flex-start; margin-bottom: 25px; font-size: 16px;">
            <div style="width: 30px; font-weight: bold; color: #666; margin-top: 20px;">1.</div>
            <div style="flex: 1;">
                <!-- 你我 -->
                <div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">
                    <span style="min-width: 40px; font-weight: bold;">你我</span>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">你</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 15px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">我</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                </div>

                <!-- 耳目 -->
                <div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">
                    <span style="min-width: 40px; font-weight: bold;">耳目</span>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">耳</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 15px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">目</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                </div>

                <!-- 日月 -->
                <div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">
                    <span style="min-width: 40px; font-weight: bold;">日月</span>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">日</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 15px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">月</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                </div>

                <!-- 爸妈 -->
                <div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">
                    <span style="min-width: 40px; font-weight: bold;">爸妈</span>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">爸</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 15px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">妈</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                </div>

                <!-- 数学 -->
                <div style="display: flex; align-items: center; margin-bottom: 15px; gap: 10px;">
                    <span style="min-width: 40px; font-weight: bold;">数学</span>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">数</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 15px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                        <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ccc;">学</span>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white; margin-right: 5px;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                    <div style="width: 50px; height: 50px; border: 2px solid #333; position: relative; display: inline-block; background: white;">
                        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #999;"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #999;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <p style="margin-top: 30px; font-size: 14px; color: #666; text-align: center;">
        <strong>使用说明：</strong>每个汉字都有对应的田字格，浅色字为示例，学生可以在空白田字格中练习书写。
    </p>
</div>
'''

    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，退出")
        return

    # 通过API创建模板
    api_url = "http://localhost:8000/api/v1/templates/"

    template_data = {
        "name": "语文田字格练习模板（每字对应）",
        "description": "每个汉字都有对应的田字格，包含示例字和练习格，适用于小学语文汉字书写练习",
        "content": template_content,
        "category": "教学模板",
        "icon": "📝",
        "is_active": True,
        "sort_order": 2
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=template_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"田字格模板创建成功！ID: {result['id']}")
        else:
            print(f"创建模板失败: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"创建模板失败: {e}")

if __name__ == "__main__":
    add_tianzige_template()
