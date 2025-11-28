from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime
import uuid
import os
from pathlib import Path
from PIL import Image
import io

from app.database import get_db
from app.models import SteamUser, AuditLog
from app.schemas import schemas
from app.schemas import auth_schemas
from app.utils.auth import (
    register_user_supabase,
    login_user_supabase,
    create_access_token,
    create_refresh_token,
    verify_token,
    set_auth_cookies,
    clear_auth_cookies,
    get_current_user,
    get_current_active_user,
    REFRESH_COOKIE_NAME
)
from app.utils.cloudinary_config import upload_profile_image as cloudinary_upload, delete_profile_image as cloudinary_delete

router = APIRouter(prefix="/auth", tags=["Autenticación"])

from app.utils.auth import supabase

@router.post("/password-reset-request", response_model=dict)
async def password_reset_request(data: auth_schemas.PasswordReset):
    """Solicita el envío de un email de reseteo de contraseña usando Supabase."""
    response = supabase.auth.reset_password_email(data.email)
    if response is None:
        return {"message": "Correo de reseteo enviado. Revisa tu bandeja de entrada."}
    if response.get('error'):
        raise HTTPException(status_code=400, detail=response['error']['message'])
    return {"message": "Correo de reseteo enviado. Revisa tu bandeja de entrada."}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: auth_schemas.UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):

    existing_user = db.query(SteamUser).filter(SteamUser.name == user_data.name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    

    supabase_user = register_user_supabase(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    

    new_user = SteamUser(
        name=user_data.name,
        auth_uid=supabase_user["auth_uid"],
        role=user_data.role,
        active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    access_token = create_access_token(data={"sub": str(new_user.auth_uid)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.auth_uid)})
    

    set_auth_cookies(response, access_token, refresh_token)
    

    
    return {
        "message": "Usuario registrado exitosamente",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "role": new_user.role,
            "email": user_data.email
        }
    }

@router.post("/login", response_model=dict)
async def login(
    credentials: auth_schemas.UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):

    supabase_response = login_user_supabase(
        email=credentials.email,
        password=credentials.password
    )
    

    user = db.query(SteamUser).filter(
        SteamUser.auth_uid == supabase_response["auth_uid"]
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base de datos local"
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    

    access_token = create_access_token(data={"sub": str(user.auth_uid)})
    refresh_token = create_refresh_token(data={"sub": str(user.auth_uid)})
    

    set_auth_cookies(response, access_token, refresh_token)
    

    
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "email": credentials.email
        }
    }

@router.post("/logout")
async def logout(
    response: Response,
    current_user: SteamUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):

    clear_auth_cookies(response)
    

    
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no proporcionado"
        )
    

    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    auth_uid = payload.get("sub")
    

    user = db.query(SteamUser).filter(SteamUser.auth_uid == auth_uid).first()
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido"
        )
    

    new_access_token = create_access_token(data={"sub": str(user.auth_uid)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.auth_uid)})
    

    set_auth_cookies(response, new_access_token, new_refresh_token)
    
    return {"message": "Tokens refrescados exitosamente"}

@router.get("/me", response_model=schemas.SteamUser)
async def get_me(current_user: SteamUser = Depends(get_current_active_user)):
    return current_user

@router.get("/verify")
async def verify_auth(current_user: SteamUser = Depends(get_current_active_user)):
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "role": current_user.role
        }
    }

@router.post("/upload-profile-image", response_model=dict)
async def upload_profile_image_endpoint(
    file: UploadFile = File(...),
    current_user: SteamUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    allowed_content_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de imagen no permitido. Usa: JPG, PNG, WebP o GIF"
        )
    
    contents = await file.read()
    
    max_size = 5 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La imagen es muy pesada. Tamaño máximo: 5 MB. Tu imagen: {len(contents) / (1024*1024):.2f} MB"
        )
    
    try:
        old_public_id = None
        if current_user.profile_image and "cloudinary.com" in current_user.profile_image:
            parts = current_user.profile_image.split("/")
            if "steam_group/profiles" in current_user.profile_image:
                old_public_id = f"steam_group/profiles/{parts[-1].split('.')[0]}"

        result = cloudinary_upload(contents, current_user.id, file.filename)

        # Check if upload actually succeeded and URL is present
        if not result or not result.get("url"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al subir la imagen a Cloudinary. Intenta de nuevo más tarde."
            )

        if old_public_id:
            try:
                cloudinary_delete(old_public_id)
            except Exception:
                pass

        current_user.profile_image = result["url"]
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return {
            "message": "Imagen de perfil actualizada exitosamente",
            "profile_image": result["url"],
            "original_size": f"{len(contents) / 1024:.2f} KB",
            "final_size": f"{result['bytes'] / 1024:.2f} KB",
            "dimensions": f"{result['width']}x{result['height']}",
            "format": result["format"].upper()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la imagen: {str(e)}"
        )

@router.delete("/profile-image", response_model=dict)
async def delete_profile_image_endpoint(
    current_user: SteamUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.profile_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes una imagen de perfil configurada"
        )
    
    if "cloudinary.com" in current_user.profile_image:
        parts = current_user.profile_image.split("/")
        if "steam_group/profiles" in current_user.profile_image:
            public_id = f"steam_group/profiles/{parts[-1].split('.')[0]}"
            try:
                cloudinary_delete(public_id)
            except:
                pass
    
    current_user.profile_image = None
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Imagen de perfil eliminada exitosamente"
    }

@router.get("/users", response_model=list)
async def get_all_users(
    current_user: SteamUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from app.models.models import Deposit, PurchaseShare

    users = db.query(SteamUser).all()
    user_ids = [u.id for u in users]

    # Subquery para depósitos
    deposits_sum = dict(
        db.query(Deposit.member_id, func.coalesce(func.sum(Deposit.amount), 0))
        .filter(Deposit.member_id.in_(user_ids))
        .group_by(Deposit.member_id)
        .all()
    )

    # Subquery para gastos
    expenses_sum = dict(
        db.query(PurchaseShare.member_id, func.coalesce(func.sum(PurchaseShare.share_amount), 0))
        .filter(PurchaseShare.member_id.in_(user_ids))
        .group_by(PurchaseShare.member_id)
        .all()
    )

    users_data = []
    for user in users:
        total_deposits = deposits_sum.get(user.id, 0)
        total_expenses = expenses_sum.get(user.id, 0)
        current_balance = total_deposits - total_expenses
        user_data = {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "active": user.active,
            "profile_image": user.profile_image,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "auth_uid": str(user.auth_uid) if user.auth_uid else None,
            "balance": {
                "total_deposits": total_deposits,
                "total_expenses": total_expenses,
                "current_balance": current_balance
            }
        }
        users_data.append(user_data)
    return users_data
