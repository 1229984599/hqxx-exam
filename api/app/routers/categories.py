from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.category import Category
from app.models.subject import Subject
from app.schemas.common import (
    CategoryCreate, CategoryUpdate, CategoryResponse, 
    MessageResponse
)
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/categories", tags=["题目分类管理"])


@router.get("/", summary="获取分类列表")
async def get_categories(
    subject_id: int = Query(None, description="学科ID"),
    parent_id: int = Query(None, description="父分类ID"),
    is_active: bool = Query(None, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取分类列表"""
    query = Category.all().prefetch_related("subject", "parent")

    if subject_id is not None:
        query = query.filter(subject_id=subject_id)

    if parent_id is not None:
        query = query.filter(parent_id=parent_id)

    if is_active is not None:
        query = query.filter(is_active=is_active)

    categories = await query.offset(skip).limit(limit).order_by("sort_order", "id")

    # 手动序列化避免循环引用
    result = []
    for category in categories:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "subject_id": category.subject_id,
            "parent_id": category.parent_id,
            "level": category.level,
            "is_active": category.is_active,
            "sort_order": category.sort_order,
            "description": category.description,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "subject": {
                "id": category.subject.id,
                "name": category.subject.name,
                "code": category.subject.code
            } if category.subject else None,
            "parent": {
                "id": category.parent.id,
                "name": category.parent.name,
                "code": category.parent.code
            } if category.parent else None
        }
        result.append(category_dict)

    return result


@router.get("/{category_id}", response_model=CategoryResponse, summary="获取分类详情")
async def get_category(category_id: int):
    """获取分类详情"""
    category = await Category.filter(id=category_id).prefetch_related(
        "subject", "parent", "children"
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse, summary="创建分类")
async def create_category(
    category_data: CategoryCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建分类"""
    # 检查学科是否存在
    subject = await Subject.filter(id=category_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Subject not found")
    
    # 检查父分类是否存在（如果指定了）
    if category_data.parent_id:
        parent = await Category.filter(id=category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    # 检查同一学科下代码是否已存在
    existing = await Category.filter(
        subject_id=category_data.subject_id, 
        code=category_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists in this subject")
    
    category = await Category.create(**category_data.dict())
    return await Category.filter(id=category.id).prefetch_related("subject", "parent").first()


@router.put("/{category_id}", response_model=CategoryResponse, summary="更新分类")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新分类"""
    category = await Category.filter(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 检查学科是否存在（如果要更新）
    if category_data.subject_id:
        subject = await Subject.filter(id=category_data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")
    
    # 检查父分类是否存在（如果要更新）
    if category_data.parent_id:
        parent = await Category.filter(id=category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    # 检查代码是否与其他分类冲突
    if category_data.code and category_data.subject_id:
        existing = await Category.filter(
            subject_id=category_data.subject_id,
            code=category_data.code
        ).exclude(id=category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category code already exists in this subject")
    
    update_data = category_data.dict(exclude_unset=True)
    await category.update_from_dict(update_data)
    await category.save()
    
    return await Category.filter(id=category_id).prefetch_related("subject", "parent").first()


@router.delete("/{category_id}", response_model=MessageResponse, summary="删除分类")
async def delete_category(
    category_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除分类"""
    category = await Category.filter(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await category.delete()
    return {"message": "Category deleted successfully"}
