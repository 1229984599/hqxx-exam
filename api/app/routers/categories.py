from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.category import Category
from app.models.subject import Subject
from app.schemas.common import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    MessageResponse, BatchUpdateRequest, BatchDeleteRequest,
    BatchCopyRequest, BatchOperationResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode

router = APIRouter(prefix="/categories", tags=["题目分类管理"])


@router.get("/", summary="获取分类列表")
async def get_categories(
    subject_id: int = Query(None, description="学科ID"),
    parent_id: int = Query(None, description="父分类ID"),
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量")
):
    """获取分类列表"""
    query = Category.all()

    if subject_id is not None:
        query = query.filter(subject_id=subject_id)

    if parent_id is not None:
        query = query.filter(parent_id=parent_id)

    if is_active is not None:
        query = query.filter(is_active=is_active)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    categories = await query.offset(skip).limit(limit).order_by("sort_order", "id")

    # 手动构建响应数据
    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "subject_id": category.subject_id,
            "parent_id": category.parent_id if category.parent_id else None,
            "level": category.level,
            "is_active": category.is_active,
            "sort_order": category.sort_order,
            "description": category.description,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        })

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
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

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


@router.put("/{category_id}", summary="更新分类")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新分类"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

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
    if category_data.code:
        # 获取要检查的学科ID：优先使用更新数据中的学科ID，否则使用当前分类的学科ID
        subject_id_to_check = category_data.subject_id if category_data.subject_id is not None else category.subject_id

        existing = await Category.filter(
            subject_id=subject_id_to_check,
            code=category_data.code
        ).exclude(id=category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category code already exists in this subject")
    
    # 更新分类数据
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    await category.save()
    
    return await Category.filter(id=category_id).prefetch_related("subject", "parent").first()


@router.delete("/{category_id}", response_model=MessageResponse, summary="删除分类")
async def delete_category(
    category_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除分类"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    category = await Category.filter(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await category.delete()
    return {"message": "Category deleted successfully"}


@router.post("/batch-update", response_model=BatchOperationResponse, summary="批量更新分类")
async def batch_update_categories(
    request: BatchUpdateRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量更新分类"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for category_id in request.get_ids():
        try:
            category = await Category.filter(id=category_id).first()
            if not category:
                failed_count += 1
                failed_items.append({"id": category_id, "error": "Category not found"})
                continue

            # 更新分类数据
            for field, value in request.update_data.items():
                if hasattr(category, field):
                    setattr(category, field, value)

            await category.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": category_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量更新完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-delete", response_model=BatchOperationResponse, summary="批量删除分类")
async def batch_delete_categories(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除分类"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for category_id in request.get_ids():
        try:
            category = await Category.filter(id=category_id).first()
            if not category:
                failed_count += 1
                failed_items.append({"id": category_id, "error": "Category not found"})
                continue

            await category.delete()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": category_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-copy", response_model=BatchOperationResponse, summary="批量复制分类")
async def batch_copy_categories(
    request: BatchCopyRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量复制分类"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []
    copy_count = request.copy_data.get('copy_count', 1)
    name_suffix = request.copy_data.get('name_suffix', '_副本')

    for category_id in request.get_ids():
        try:
            category = await Category.filter(id=category_id).first()
            if not category:
                failed_count += 1
                failed_items.append({"id": category_id, "error": "Category not found"})
                continue

            for i in range(copy_count):
                # 创建副本
                copy_name = f"{category.name}{name_suffix}"
                if copy_count > 1:
                    copy_name += f"_{i+1}"

                copy_code = f"{category.code}_copy"
                if copy_count > 1:
                    copy_code += f"_{i+1}"

                # 确保代码在同一学科下唯一性
                counter = 1
                original_copy_code = copy_code
                while await Category.filter(subject_id=category.subject_id, code=copy_code).exists():
                    copy_code = f"{original_copy_code}_{counter}"
                    counter += 1

                await Category.create(
                    name=copy_name,
                    code=copy_code,
                    subject_id=category.subject_id,
                    parent_id=category.parent_id,
                    level=category.level,
                    is_active=category.is_active,
                    sort_order=category.sort_order,
                    description=category.description
                )
                success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": category_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()) * copy_count,
        message=f"批量复制完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )
