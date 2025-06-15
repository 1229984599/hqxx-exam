from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.template import Template
from app.models.subject import Subject
from app.schemas.common import (
    TemplateCreate, TemplateUpdate, TemplateResponse, 
    MessageResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode

router = APIRouter(prefix="/templates", tags=["模板管理"])


@router.get("/", summary="获取模板列表")
async def get_templates(
    category: str = Query(None, description="模板分类"),
    subject_id: int = Query(None, description="学科ID"),
    is_active: bool = Query(None, description="是否激活"),
    is_system: bool = Query(None, description="是否系统模板"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    current_admin = Depends(get_current_active_admin)
):
    """获取模板列表"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.TEMPLATES_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")
    query = Template.all().prefetch_related("subject")

    if category:
        query = query.filter(category=category)

    if subject_id is not None:
        query = query.filter(subject_id=subject_id)

    if is_active is not None:
        query = query.filter(is_active=is_active)

    if is_system is not None:
        query = query.filter(is_system=is_system)

    if search:
        query = query.filter(name__icontains=search)

    templates = await query.offset(skip).limit(limit).order_by("sort_order", "-created_at")

    # 手动序列化
    result = []
    for template in templates:
        template_dict = {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "content": template.content,
            "category": template.category,
            "icon": template.icon,
            "subject_id": template.subject_id,
            "is_active": template.is_active,
            "is_system": template.is_system,
            "sort_order": template.sort_order,
            "usage_count": template.usage_count,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "subject": {
                "id": template.subject.id,
                "name": template.subject.name,
                "code": template.subject.code,
                "color": template.subject.color
            } if template.subject else None
        }
        result.append(template_dict)

    return result


@router.get("/categories", summary="获取模板分类列表")
async def get_template_categories():
    """获取模板分类列表"""
    categories = await Template.all().distinct().values_list("category", flat=True)
    return [{"value": cat, "label": cat} for cat in categories if cat]


@router.get("/{template_id}", summary="获取模板详情")
async def get_template(template_id: int):
    """获取模板详情"""
    template = await Template.filter(id=template_id).prefetch_related("subject").first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "category": template.category,
        "icon": template.icon,
        "subject_id": template.subject_id,
        "is_active": template.is_active,
        "is_system": template.is_system,
        "sort_order": template.sort_order,
        "usage_count": template.usage_count,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
        "subject": {
            "id": template.subject.id,
            "name": template.subject.name,
            "code": template.subject.code,
            "color": template.subject.color
        } if template.subject else None
    }


@router.post("/", summary="创建模板")
async def create_template(
    template_data: TemplateCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建模板"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.TEMPLATES_CREATE):
        raise HTTPException(status_code=403, detail="Permission denied")
    # 验证学科是否存在（如果指定了）
    if template_data.subject_id:
        subject = await Subject.filter(id=template_data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")

    template_dict = template_data.dict()
    
    # 处理学科关联
    if template_data.subject_id:
        subject = await Subject.filter(id=template_data.subject_id).first()
        template_dict['subject'] = subject
        del template_dict['subject_id']

    template = await Template.create(**template_dict)

    # 重新获取完整数据
    template = await Template.filter(id=template.id).prefetch_related("subject").first()

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "category": template.category,
        "icon": template.icon,
        "subject_id": template.subject_id,
        "is_active": template.is_active,
        "is_system": template.is_system,
        "sort_order": template.sort_order,
        "usage_count": template.usage_count,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
        "subject": {
            "id": template.subject.id,
            "name": template.subject.name,
            "code": template.subject.code,
            "color": template.subject.color
        } if template.subject else None
    }


@router.put("/{template_id}", summary="更新模板")
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新模板"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.TEMPLATES_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    template = await Template.filter(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 检查是否为系统模板
    if template.is_system and not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Cannot modify system template")

    update_data = template_data.dict(exclude_unset=True)

    # 验证并设置学科关联（如果要更新）
    if template_data.subject_id is not None:
        if template_data.subject_id:
            subject = await Subject.filter(id=template_data.subject_id).first()
            if not subject:
                raise HTTPException(status_code=400, detail="Subject not found")
            update_data['subject'] = subject
        else:
            update_data['subject'] = None
        del update_data['subject_id']

    # 更新模板数据
    for field, value in update_data.items():
        setattr(template, field, value)
    await template.save()

    # 重新获取完整数据
    template = await Template.filter(id=template_id).prefetch_related("subject").first()

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "category": template.category,
        "icon": template.icon,
        "subject_id": template.subject_id,
        "is_active": template.is_active,
        "is_system": template.is_system,
        "sort_order": template.sort_order,
        "usage_count": template.usage_count,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
        "subject": {
            "id": template.subject.id,
            "name": template.subject.name,
            "code": template.subject.code,
            "color": template.subject.color
        } if template.subject else None
    }


@router.delete("/{template_id}", response_model=MessageResponse, summary="删除模板")
async def delete_template(
    template_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除模板"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.TEMPLATES_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")

    template = await Template.filter(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 检查是否为系统模板
    if template.is_system and not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Cannot delete system template")
    
    await template.delete()
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/use", summary="使用模板")
async def use_template(template_id: int):
    """使用模板（增加使用次数）"""
    template = await Template.filter(id=template_id, is_active=True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or inactive")
    
    # 增加使用次数
    template.usage_count += 1
    await template.save()
    
    return {
        "id": template.id,
        "name": template.name,
        "content": template.content,
        "category": template.category,
        "icon": template.icon
    }
