from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, UploadFile, File
from sqlalchemy.orm import Session
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

router = APIRouter(prefix="/auth", tags=["Autenticación"])

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
async def upload_profile_image(
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

        image = Image.open(io.BytesIO(contents))
        

        is_animated_gif = False
        if file.content_type == "image/gif":
            try:
                image.seek(1)
                is_animated_gif = True
                image.seek(0)
            except EOFError:
                is_animated_gif = False
        

        upload_dir = Path("uploads/profiles")
        upload_dir.mkdir(parents=True, exist_ok=True)
        

        file_extension = file.content_type.split("/")[-1]
        if file_extension == "jpeg":
            file_extension = "jpg"
        
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = upload_dir / unique_filename
        

        if is_animated_gif:
            with open(file_path, "wb") as f:
                f.write(contents)
            

            if current_user.profile_image:
                old_file_path = Path(current_user.profile_image)
                if old_file_path.exists():
                    old_file_path.unlink()
            

            current_user.profile_image = str(file_path)
            current_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(current_user)
            
            return {
                "message": "Imagen de perfil actualizada exitosamente",
                "profile_image": str(file_path),
                "original_size": f"{len(contents) / 1024:.2f} KB",
                "final_size": f"{len(contents) / 1024:.2f} KB",
                "dimensions": f"{image.size[0]}x{image.size[1]}",
                "format": "GIF (animado)"
            }
        

        max_dimension = 2000
        width, height = image.size
        

        if width > max_dimension or height > max_dimension:
            ratio = min(max_dimension / width, max_dimension / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        

        if file_extension in ["jpg", "jpeg"] and image.mode in ("RGBA", "P"):

            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "RGBA":
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image)
            image = background
        

        if file_extension in ["jpg", "jpeg"]:
            image.save(file_path, "JPEG", quality=85, optimize=True)
        elif file_extension == "png":
            image.save(file_path, "PNG", optimize=True)
        elif file_extension == "webp":
            image.save(file_path, "WEBP", quality=85, optimize=True)
        elif file_extension == "gif":
            image.save(file_path, "GIF", optimize=True)
        

        if current_user.profile_image:
            old_file_path = Path(current_user.profile_image)
            if old_file_path.exists():
                old_file_path.unlink()
        

        current_user.profile_image = str(file_path)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        

        final_size = os.path.getsize(file_path)
        
        return {
            "message": "Imagen de perfil actualizada exitosamente",
            "profile_image": str(file_path),
            "original_size": f"{len(contents) / 1024:.2f} KB",
            "final_size": f"{final_size / 1024:.2f} KB",
            "dimensions": f"{image.size[0]}x{image.size[1]}",
            "format": file_extension.upper()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la imagen: {str(e)}"
        )

@router.delete("/profile-image", response_model=dict)
async def delete_profile_image(
    current_user: SteamUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.profile_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes una imagen de perfil configurada"
        )
    

    file_path = Path(current_user.profile_image)
    if file_path.exists():
        file_path.unlink()
    

    current_user.profile_image = None
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Imagen de perfil eliminada exitosamente"
    }
