#!/usr/bin/env python3
"""
创建系统日志表的脚本
运行此脚本来添加系统日志功能所需的数据库表
"""

import asyncio
import sqlite3
from pathlib import Path


async def create_log_table():
    """创建系统日志表"""
    db_path = "api/db.sqlite3"
    
    if not Path(db_path).exists():
        print(f"数据库文件 {db_path} 不存在")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建系统日志表
        create_logs_table_sql = """
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level VARCHAR(20) NOT NULL,
            module VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            details JSON,
            user VARCHAR(100),
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            request_id VARCHAR(100),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_logs_table_sql)

        # 创建系统配置表
        create_configs_table_sql = """
        CREATE TABLE IF NOT EXISTS system_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value JSON NOT NULL,
            config_type VARCHAR(50) NOT NULL,
            description VARCHAR(500),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(100)
        );
        """

        cursor.execute(create_configs_table_sql)

        # 创建角色表
        create_roles_table_sql = """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(200),
            is_active BOOLEAN DEFAULT 1,
            is_system BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100)
        );
        """

        cursor.execute(create_roles_table_sql)

        # 创建权限表
        create_permissions_table_sql = """
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            code VARCHAR(100) UNIQUE NOT NULL,
            resource VARCHAR(50) NOT NULL,
            action VARCHAR(20) NOT NULL,
            description VARCHAR(200),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_permissions_table_sql)

        # 创建角色权限关联表
        create_role_permissions_table_sql = """
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
            UNIQUE(role_id, permission_id)
        );
        """

        cursor.execute(create_role_permissions_table_sql)

        # 创建管理员角色关联表
        create_admin_roles_table_sql = """
        CREATE TABLE IF NOT EXISTS admin_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            FOREIGN KEY (admin_id) REFERENCES admins (id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
            UNIQUE(admin_id, role_id)
        );
        """

        cursor.execute(create_admin_roles_table_sql)
        
        # 创建索引以提高查询性能
        indexes = [
            # 日志表索引
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_module ON system_logs(module);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_user ON system_logs(user);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level_timestamp ON system_logs(level, timestamp);",
            # 配置表索引
            "CREATE INDEX IF NOT EXISTS idx_system_configs_key ON system_configs(config_key);",
            "CREATE INDEX IF NOT EXISTS idx_system_configs_type ON system_configs(config_type);",
            "CREATE INDEX IF NOT EXISTS idx_system_configs_active ON system_configs(is_active);",
            # 角色权限表索引
            "CREATE INDEX IF NOT EXISTS idx_roles_code ON roles(code);",
            "CREATE INDEX IF NOT EXISTS idx_roles_active ON roles(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(code);",
            "CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);",
            "CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);",
            "CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);",
            "CREATE INDEX IF NOT EXISTS idx_admin_roles_admin ON admin_roles(admin_id);",
            "CREATE INDEX IF NOT EXISTS idx_admin_roles_role ON admin_roles(role_id);"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # 提交更改
        conn.commit()
        print("✅ 系统日志表和配置表创建成功")
        
        # 插入一些示例日志
        sample_logs = [
            ("info", "system", "系统启动", None, "system", None, None, None),
            ("info", "auth", "管理员登录", '{"username": "admin"}', "admin", "127.0.0.1", "Mozilla/5.0", None),
            ("warning", "questions", "试题更新", '{"question_id": 1}', "admin", "127.0.0.1", "Mozilla/5.0", None),
        ]
        
        insert_sql = """
        INSERT INTO system_logs (level, module, message, details, user, ip_address, user_agent, request_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.executemany(insert_sql, sample_logs)
        conn.commit()
        print("✅ 示例日志数据插入成功")

        # 插入一些示例配置
        sample_configs = [
            ('backup.method', '"local"', 'backup', '备份方式配置', 1),
            ('backup.auto', 'false', 'backup', '自动备份配置', 1),
            ('system.basic', '{"schoolName": "红旗小学", "systemName": "红旗小学考试管理系统"}', 'system', '基础系统配置', 1),
        ]

        config_insert_sql = """
        INSERT OR IGNORE INTO system_configs (config_key, config_value, config_type, description, is_active)
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.executemany(config_insert_sql, sample_configs)
        conn.commit()
        print("✅ 示例配置数据插入成功")

        # 插入系统角色
        system_roles = [
            ('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', 1, 1),
            ('管理员', 'admin', '普通管理员，拥有大部分权限', 1, 1),
            ('教师', 'teacher', '教师角色，可以管理试题', 1, 1),
            ('学科管理员', 'subject_admin', '学科管理员，可以管理特定学科的试题', 1, 1),
            ('查看者', 'viewer', '只读权限，只能查看数据', 1, 1),
        ]

        role_insert_sql = """
        INSERT OR IGNORE INTO roles (name, code, description, is_active, is_system)
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.executemany(role_insert_sql, system_roles)
        conn.commit()
        print("✅ 系统角色数据插入成功")

        # 插入系统权限
        system_permissions = [
            # 试题管理权限
            ('查看试题', 'questions:view', 'questions', 'view', '查看试题列表和详情'),
            ('创建试题', 'questions:create', 'questions', 'create', '创建新试题'),
            ('编辑试题', 'questions:edit', 'questions', 'edit', '编辑试题信息'),
            ('删除试题', 'questions:delete', 'questions', 'delete', '删除试题'),
            ('导出试题', 'questions:export', 'questions', 'export', '导出试题数据'),
            ('批量操作试题', 'questions:batch', 'questions', 'batch', '批量操作试题'),

            # 用户管理权限
            ('查看用户', 'admins:view', 'admins', 'view', '查看管理员列表'),
            ('创建用户', 'admins:create', 'admins', 'create', '创建新管理员'),
            ('编辑用户', 'admins:edit', 'admins', 'edit', '编辑管理员信息'),
            ('删除用户', 'admins:delete', 'admins', 'delete', '删除管理员'),

            # 基础数据权限
            ('查看基础数据', 'basic_data:view', 'basic_data', 'view', '查看学期、年级、学科、分类'),
            ('编辑基础数据', 'basic_data:edit', 'basic_data', 'edit', '编辑基础数据'),

            # 模板管理权限
            ('查看模板', 'templates:view', 'templates', 'view', '查看模板列表'),
            ('创建模板', 'templates:create', 'templates', 'create', '创建新模板'),
            ('编辑模板', 'templates:edit', 'templates', 'edit', '编辑模板'),
            ('删除模板', 'templates:delete', 'templates', 'delete', '删除模板'),

            # 系统管理权限
            ('查看系统信息', 'system:view', 'system', 'view', '查看系统统计和信息'),
            ('系统配置', 'system:config', 'system', 'config', '修改系统配置'),
            ('系统备份', 'system:backup', 'system', 'backup', '创建和管理系统备份'),
            ('查看系统日志', 'system:logs', 'system', 'logs', '查看系统操作日志'),

            # 统计分析权限
            ('查看统计', 'analytics:view', 'analytics', 'view', '查看数据统计分析'),
            ('导出统计', 'analytics:export', 'analytics', 'export', '导出统计数据'),
        ]

        permission_insert_sql = """
        INSERT OR IGNORE INTO permissions (name, code, resource, action, description)
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.executemany(permission_insert_sql, system_permissions)
        conn.commit()
        print("✅ 系统权限数据插入成功")

        # 查询验证
        cursor.execute("SELECT COUNT(*) FROM system_logs")
        log_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM system_configs")
        config_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM permissions")
        permission_count = cursor.fetchone()[0]
        print(f"📊 当前日志记录数: {log_count}")
        print(f"📊 当前配置记录数: {config_count}")
        print(f"📊 当前角色数: {role_count}")
        print(f"📊 当前权限数: {permission_count}")
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 开始创建系统表...")
    asyncio.run(create_log_table())
    print("🎉 完成!")
