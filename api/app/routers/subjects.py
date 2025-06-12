from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.subject import Subject
from app.schemas.common import (
    SubjectCreate, SubjectUpdate, SubjectResponse, 
    MessageResponse
)
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/subjects", tags=["学科管理"])


@router.get("/", response_model=List[SubjectResponse], summary="获取学科列表")
async def get_subjects(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学科列表"""
    query = Subject.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    subjects = await query.offset(skip).limit(limit).order_by("sort_order", "id")
    return subjects


@router.get("/{subject_id}", response_model=SubjectResponse, summary="获取学科详情")
async def get_subject(subject_id: int):
    """获取学科详情"""
    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.post("/", response_model=SubjectResponse, summary="创建学科")
async def create_subject(
    subject_data: SubjectCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建学科"""
    # 检查代码是否已存在
    existing = await Subject.filter(code=subject_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    
    subject = await Subject.create(**subject_data.dict())
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse, summary="更新学科")
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新学科"""
    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # 检查代码是否与其他学科冲突
    if subject_data.code:
        existing = await Subject.filter(code=subject_data.code).exclude(id=subject_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Subject code already exists")
    
    # 更新学科数据
    update_data = subject_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    await subject.save()
    return subject


@router.delete("/{subject_id}", response_model=MessageResponse, summary="删除学科")
async def delete_subject(
    subject_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除学科"""
    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    await subject.delete()
    return {"message": "Subject deleted successfully"}
