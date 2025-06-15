#!/usr/bin/env python3
"""
修复system_configs表的config_value字段类型
"""

import sqlite3
import json
from pathlib import Path

def fix_config_table():
    """修复配置表字段类型"""
    db_path = Path("api/db.sqlite3")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 检查当前表结构...")
        cursor.execute("PRAGMA table_info(system_configs)")
        columns = cursor.fetchall()
        print(f"当前字段: {columns}")
        
        # 检查是否需要修复
        config_value_column = None
        for col in columns:
            if col[1] == 'config_value':
                config_value_column = col
                break
        
        if config_value_column and config_value_column[2] == 'JSON':
            print("🔧 需要修复config_value字段类型...")
            
            # 1. 备份现有数据
            print("📦 备份现有数据...")
            cursor.execute("SELECT * FROM system_configs")
            existing_data = cursor.fetchall()
            print(f"备份了 {len(existing_data)} 条记录")
            
            # 2. 创建新表
            print("🆕 创建新表...")
            cursor.execute("""
                CREATE TABLE system_configs_new (
                    id INTEGER PRIMARY KEY,
                    config_key VARCHAR(100) NOT NULL UNIQUE,
                    config_value TEXT NOT NULL,
                    config_type VARCHAR(50) NOT NULL,
                    description VARCHAR(500),
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100)
                )
            """)
            
            # 3. 迁移数据
            print("📋 迁移数据...")
            for row in existing_data:
                cursor.execute("""
                    INSERT INTO system_configs_new 
                    (id, config_key, config_value, config_type, description, is_active, created_at, updated_at, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
            
            # 4. 删除旧表，重命名新表
            print("🔄 替换表...")
            cursor.execute("DROP TABLE system_configs")
            cursor.execute("ALTER TABLE system_configs_new RENAME TO system_configs")
            
            # 5. 创建索引
            print("📊 创建索引...")
            cursor.execute("CREATE UNIQUE INDEX idx_system_configs_key ON system_configs(config_key)")
            cursor.execute("CREATE INDEX idx_system_configs_type ON system_configs(config_type)")
            
            conn.commit()
            print("✅ 表结构修复完成")
            
        else:
            print("✅ 表结构已经正确，无需修复")
        
        # 验证修复结果
        print("🔍 验证修复结果...")
        cursor.execute("PRAGMA table_info(system_configs)")
        new_columns = cursor.fetchall()
        print(f"新字段结构: {new_columns}")
        
        cursor.execute("SELECT COUNT(*) FROM system_configs")
        count = cursor.fetchone()[0]
        print(f"数据记录数: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 开始修复system_configs表...")
    success = fix_config_table()
    if success:
        print("🎉 修复完成！")
    else:
        print("💥 修复失败！")
