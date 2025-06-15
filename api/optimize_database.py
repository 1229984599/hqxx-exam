#!/usr/bin/env python3
"""
数据库性能优化脚本
添加索引、优化查询性能
"""

import asyncio
import sqlite3
from pathlib import Path


async def optimize_database():
    """优化数据库性能"""
    db_path = "api/db.sqlite3"
    
    if not Path(db_path).exists():
        print(f"数据库文件 {db_path} 不存在")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🚀 开始数据库性能优化...")
        
        # 添加性能优化索引
        performance_indexes = [
            # 试题表索引优化
            "CREATE INDEX IF NOT EXISTS idx_questions_semester_grade ON questions(semester_id, grade_id);",
            "CREATE INDEX IF NOT EXISTS idx_questions_subject_category ON questions(subject_id, category_id);",
            "CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);",
            "CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_questions_updated_at ON questions(updated_at);",
            "CREATE INDEX IF NOT EXISTS idx_questions_is_active ON questions(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_questions_composite ON questions(semester_id, grade_id, subject_id, category_id, is_active);",
            
            # 管理员表索引
            "CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username);",
            "CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);",
            "CREATE INDEX IF NOT EXISTS idx_admins_is_active ON admins(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_admins_is_superuser ON admins(is_superuser);",
            
            # 基础数据表索引
            "CREATE INDEX IF NOT EXISTS idx_semesters_name ON semesters(name);",
            "CREATE INDEX IF NOT EXISTS idx_semesters_is_active ON semesters(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_grades_name ON grades(name);",
            "CREATE INDEX IF NOT EXISTS idx_grades_is_active ON grades(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name);",
            "CREATE INDEX IF NOT EXISTS idx_subjects_is_active ON subjects(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);",
            "CREATE INDEX IF NOT EXISTS idx_categories_subject ON categories(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_categories_is_active ON categories(is_active);",
            
            # 模板表索引
            "CREATE INDEX IF NOT EXISTS idx_templates_name ON templates(name);",
            "CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);",
            "CREATE INDEX IF NOT EXISTS idx_templates_is_active ON templates(is_active);",
            
            # 系统日志表索引（已存在，但确保完整）
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level_module ON system_logs(level, module);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_user_timestamp ON system_logs(user, timestamp);",
            
            # 系统配置表索引（已存在，但确保完整）
            "CREATE INDEX IF NOT EXISTS idx_system_configs_type_active ON system_configs(config_type, is_active);",
        ]
        
        print("📊 添加性能索引...")
        for index_sql in performance_indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ 索引创建成功: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
            except Exception as e:
                print(f"⚠️ 索引创建跳过: {e}")
        
        # 分析表统计信息
        print("\n📈 分析表统计信息...")
        tables = [
            'questions', 'admins', 'semesters', 'grades', 
            'subjects', 'categories', 'templates', 
            'system_logs', 'system_configs'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table};")
                print(f"✅ 分析完成: {table}")
            except Exception as e:
                print(f"⚠️ 分析跳过: {table} - {e}")
        
        # 优化数据库
        print("\n🔧 优化数据库...")
        cursor.execute("VACUUM;")
        print("✅ 数据库压缩完成")
        
        cursor.execute("PRAGMA optimize;")
        print("✅ 查询优化完成")
        
        # 提交更改
        conn.commit()
        print("\n✅ 数据库性能优化完成")
        
        # 显示优化结果
        print("\n📊 优化结果统计:")
        
        # 获取表大小信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        total_size = 0
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  📋 {table_name}: {count} 条记录")
                total_size += count
        
        print(f"  📊 总记录数: {total_size}")
        
        # 获取索引信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';")
        indexes = cursor.fetchall()
        print(f"  🔍 性能索引数: {len(indexes)}")
        
        # 获取数据库文件大小
        db_size = Path(db_path).stat().st_size
        print(f"  💾 数据库大小: {db_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"❌ 数据库优化失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 开始数据库性能优化...")
    asyncio.run(optimize_database())
    print("🎉 优化完成!")
