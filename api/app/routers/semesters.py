from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.semester import Semester
from app.schemas.common import (
    SemesterCreate, SemesterUpdate, SemesterResponse, 
    PaginatedResponse, MessageResponse
)
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/semesters", tags=["学期管理"])


@router.get("/", response_model=List[SemesterResponse], summary="获取学期列表")
async def get_semesters(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学期列表"""
    query = Semester.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    semesters = await query.offset(skip).limit(limit).order_by("sort_order", "id")
    return semesters


@router.get("/{semester_id}", response_model=SemesterResponse, summary="获取学期详情")
async def get_semester(semester_id: int):
    """获取学期详情"""
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    return semester


@router.post("/", response_model=SemesterResponse, summary="创建学期")
async def create_semester(
    semester_data: SemesterCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建学期"""
    # 检查代码是否已存在
    existing = await Semester.filter(code=semester_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Semester code already exists")
    
    semester = await Semester.create(**semester_data.dict())
    return semester


@router.put("/{semester_id}", response_model=SemesterResponse, summary="更新学期")
async def update_semester(
    semester_id: int,
    semester_data: SemesterUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新学期"""
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    # 检查代码是否与其他学期冲突
    if semester_data.code:
        existing = await Semester.filter(code=semester_data.code).exclude(id=semester_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Semester code already exists")
    
    # 更新学期数据
    update_data = semester_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(semester, field, value)
    await semester.save()
    return semester


@router.delete("/{semester_id}", response_model=MessageResponse, summary="删除学期")
async def delete_semester(
    semester_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除学期"""
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    await semester.delete()
    return {"message": "Semester deleted successfully"}
