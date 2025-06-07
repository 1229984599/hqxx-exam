from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.grade import Grade
from app.schemas.common import (
    GradeCreate, GradeUpdate, GradeResponse, 
    MessageResponse
)
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/grades", tags=["年级管理"])


@router.get("/", response_model=List[GradeResponse], summary="获取年级列表")
async def get_grades(
    is_active: bool = Query(None, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取年级列表"""
    query = Grade.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    grades = await query.offset(skip).limit(limit).order_by("sort_order", "level")
    return grades


@router.get("/{grade_id}", response_model=GradeResponse, summary="获取年级详情")
async def get_grade(grade_id: int):
    """获取年级详情"""
    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.post("/", response_model=GradeResponse, summary="创建年级")
async def create_grade(
    grade_data: GradeCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建年级"""
    # 检查代码是否已存在
    existing = await Grade.filter(code=grade_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Grade code already exists")
    
    grade = await Grade.create(**grade_data.dict())
    return grade


@router.put("/{grade_id}", response_model=GradeResponse, summary="更新年级")
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新年级"""
    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    # 检查代码是否与其他年级冲突
    if grade_data.code:
        existing = await Grade.filter(code=grade_data.code).exclude(id=grade_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Grade code already exists")
    
    update_data = grade_data.dict(exclude_unset=True)
    await grade.update_from_dict(update_data)
    await grade.save()
    return grade


@router.delete("/{grade_id}", response_model=MessageResponse, summary="删除年级")
async def delete_grade(
    grade_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除年级"""
    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    await grade.delete()
    return {"message": "Grade deleted successfully"}
