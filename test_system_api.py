#!/usr/bin/env python3
"""
快速测试系统管理API是否正常工作
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_system_stats():
    """测试系统统计API"""
    try:
        # 首先需要登录获取token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("🔐 正在登录...")
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(login_response.text)
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ 登录成功")
        
        # 测试系统统计API
        print("📊 测试系统统计API...")
        stats_response = requests.get(f"{BASE_URL}/system/stats", headers=headers)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ 系统统计API正常工作")
            print(f"📈 数据库大小: {stats_data.get('database_size', {})}")
            print(f"📊 数据质量: {stats_data.get('data_quality', {})}")
            print(f"⚡ 性能指标: {stats_data.get('performance_metrics', {})}")
            return True
        else:
            print(f"❌ 系统统计API错误: {stats_response.status_code}")
            print(stats_response.text)
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

def test_system_health():
    """测试系统健康检查API"""
    try:
        print("🏥 测试系统健康检查...")
        health_response = requests.get(f"{BASE_URL}/system/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ 系统健康检查正常")
            print(f"🟢 状态: {health_data.get('status')}")
            print(f"🗄️ 数据库: {health_data.get('database')}")
            return True
        else:
            print(f"❌ 系统健康检查错误: {health_response.status_code}")
            print(health_response.text)
            return False
            
    except Exception as e:
        print(f"❌ 健康检查过程中出现异常: {str(e)}")
        return False

def test_analytics_dashboard():
    """测试分析仪表板API"""
    try:
        print("📊 测试分析仪表板API...")
        dashboard_response = requests.get(f"{BASE_URL}/analytics/dashboard")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ 分析仪表板API正常工作")
            print(f"📈 基础统计: {dashboard_data.get('basic_stats', {})}")
            print(f"📊 难度分布: {len(dashboard_data.get('difficulty_distribution', []))} 项")
            print(f"📚 学科分布: {len(dashboard_data.get('subject_distribution', []))} 项")
            return True
        else:
            print(f"❌ 分析仪表板API错误: {dashboard_response.status_code}")
            print(dashboard_response.text)
            return False
            
    except Exception as e:
        print(f"❌ 分析仪表板测试过程中出现异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试系统管理API...")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("系统健康检查", test_system_health),
        ("分析仪表板", test_analytics_dashboard),
        ("系统统计", test_system_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 测试: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # 输出测试结果汇总
    print("=" * 50)
    print("📋 测试结果汇总:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！系统管理功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    print("\n💡 提示:")
    print("  - 后端服务: http://localhost:8000")
    print("  - 管理界面: http://localhost:3002")
    print("  - API文档: http://localhost:8000/docs")
