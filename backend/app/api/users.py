from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app import db
import uuid
import hashlib

router = APIRouter()


class UserCreateRequest(BaseModel):
    nickname: str


class UserResponse(BaseModel):
    id: str
    nickname: str


class UserUpdateRequest(BaseModel):
    nickname: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    message: str = ""


@router.post("", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    """创建新用户（返回随机 ID）"""
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    db.create_or_update_user(user_id, request.nickname)
    return UserResponse(id=user_id, nickname=request.nickname)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.get_user_by_username(request.username)
    if existing:
        return AuthResponse(success=False, message="用户名已存在")
    
    user_id = db.register_user(request.username, request.password, request.nickname)
    if not user_id:
        return AuthResponse(success=False, message="注册失败")
    
    return AuthResponse(success=True, user=UserResponse(id=user_id, nickname=request.nickname), message="注册成功")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """用户登录"""
    user = db.login_user(request.username, request.password)
    if not user:
        return AuthResponse(success=False, message="用户名或密码错误")
    
    return AuthResponse(success=True, user=UserResponse(id=user['id'], nickname=user['nickname']), message="登录成功")


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
