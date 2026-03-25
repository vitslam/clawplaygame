from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app import db
import uuid

router = APIRouter()


class UserCreateRequest(BaseModel):
    nickname: str


class UserResponse(BaseModel):
    id: str
    nickname: str


class UserUpdateRequest(BaseModel):
    nickname: str


@router.post("", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    """创建新用户（返回随机 ID）"""
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    db.create_or_update_user(user_id, request.nickname)
    return UserResponse(id=user_id, nickname=request.nickname)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """获取用户信息"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(**user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, request: UserUpdateRequest):
    """更新用户昵称"""
    db.create_or_update_user(user_id, request.nickname)
    return UserResponse(id=user_id, nickname=request.nickname)


@router.post("/{user_id}/heartbeat")
async def user_heartbeat(user_id: str):
    """更新用户活跃时间（心跳）"""
    success = db.update_user_last_seen(user_id)
    return {"success": success}
