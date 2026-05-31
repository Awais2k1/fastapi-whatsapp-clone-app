from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
)
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    try:
        new_user = AuthService.register(
            db=db,
            username=user.username,
            email=user.email,
            password=user.password
        )

        return {
            "id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    result = AuthService.login(
        db=db,
        email=data.email,
        password=data.password
    )

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return result

@router.post("/refresh")
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    result = AuthService.refresh_access_token(
        db,
        data.refresh_token
    )

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    return result

@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    success = AuthService.logout(
        db,
        data.refresh_token
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid refresh token"
        )

    return {
        "message": "Logged out successfully"
    }

