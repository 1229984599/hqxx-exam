from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class Role(Model):
    """角色模型"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="角色名称")
    code = fields.CharField(max_length=50, unique=True, description="角色代码")
    description = fields.CharField(max_length=200, null=True, description="角色描述")
    is_active = fields.BooleanField(default=True, description="是否启用")
    is_system = fields.BooleanField(default=False, description="是否系统角色")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.CharField(max_length=100, null=True, description="创建者")
    
    class Meta:
        table = "roles"
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class Permission(Model):
    """权限模型"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, description="权限名称")
    code = fields.CharField(max_length=100, unique=True, description="权限代码")
    resource = fields.CharField(max_length=50, description="资源名称")  # questions, admins, system
    action = fields.CharField(max_length=20, description="操作类型")  # view, create, edit, delete, export
    description = fields.CharField(max_length=200, null=True, description="权限描述")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    
    class Meta:
        table = "permissions"
        ordering = ["resource", "action"]
    
    def __str__(self):
        return f"{self.resource}:{self.action}"


class RolePermission(Model):
    """角色权限关联模型"""
    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField("models.Role", related_name="role_permissions", description="角色")
    permission = fields.ForeignKeyField("models.Permission", related_name="permission_roles", description="权限")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    created_by = fields.CharField(max_length=100, null=True, description="创建者")
    
    class Meta:
        table = "role_permissions"
        unique_together = (("role", "permission"),)
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.code}"


class AdminRole(Model):
    """管理员角色关联模型"""
    id = fields.IntField(pk=True)
    admin = fields.ForeignKeyField("models.Admin", related_name="admin_roles", description="管理员")
    role = fields.ForeignKeyField("models.Role", related_name="role_admins", description="角色")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    created_by = fields.CharField(max_length=100, null=True, description="创建者")
    
    class Meta:
        table = "admin_roles"
        unique_together = (("admin", "role"),)
    
    def __str__(self):
        return f"{self.admin.username} - {self.role.name}"


class RoleCode:
    """角色代码常量"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    SUBJECT_ADMIN = "subject_admin"
    VIEWER = "viewer"


class PermissionCode:
    """权限代码常量"""
    # 试题管理权限
    QUESTIONS_VIEW = "questions:view"
    QUESTIONS_CREATE = "questions:create"
    QUESTIONS_EDIT = "questions:edit"
    QUESTIONS_DELETE = "questions:delete"
    QUESTIONS_EXPORT = "questions:export"
    QUESTIONS_BATCH = "questions:batch"
    
    # 用户管理权限
    ADMINS_VIEW = "admins:view"
    ADMINS_CREATE = "admins:create"
    ADMINS_EDIT = "admins:edit"
    ADMINS_DELETE = "admins:delete"
    
    # 基础数据权限
    BASIC_DATA_VIEW = "basic_data:view"
    BASIC_DATA_EDIT = "basic_data:edit"
    
    # 模板管理权限
    TEMPLATES_VIEW = "templates:view"
    TEMPLATES_CREATE = "templates:create"
    TEMPLATES_EDIT = "templates:edit"
    TEMPLATES_DELETE = "templates:delete"
    
    # 系统管理权限
    SYSTEM_VIEW = "system:view"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_LOGS = "system:logs"
    
    # 统计分析权限
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"


class ResourceType:
    """资源类型常量"""
    QUESTIONS = "questions"
    ADMINS = "admins"
    BASIC_DATA = "basic_data"
    TEMPLATES = "templates"
    SYSTEM = "system"
    ANALYTICS = "analytics"


class ActionType:
    """操作类型常量"""
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    EXPORT = "export"
    BATCH = "batch"
    CONFIG = "config"
    BACKUP = "backup"
    LOGS = "logs"
