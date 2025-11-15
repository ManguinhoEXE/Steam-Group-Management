from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, text
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import SteamUser, Deposit, PurchaseShare
from app.utils.auth import get_current_active_user, require_master_role
from app.schemas import schemas

router = APIRouter(prefix="/deposits", tags=["Deposits"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: schemas.DepositCreate,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    

    member = db.query(SteamUser).filter(SteamUser.id == deposit_data.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {deposit_data.member_id} no encontrado"
        )
    

    new_deposit = Deposit(
        member_id=deposit_data.member_id,
        amount=deposit_data.amount,
        note=deposit_data.note,
        date=deposit_data.date if deposit_data.date else datetime.utcnow()
    )
    
    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)
    
    return {
        "message": "Depósito registrado exitosamente",
        "deposit": {
            "id": new_deposit.id,
            "member_id": new_deposit.member_id,
            "member_name": member.name,
            "amount": new_deposit.amount,
            "note": new_deposit.note,
            "date": new_deposit.date,
            "created_at": new_deposit.created_at
        }
    }

@router.get("/user/{user_id}", response_model=List[schemas.Deposit])
async def get_user_deposits(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    user = db.query(SteamUser).filter(SteamUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    

    deposits = db.query(Deposit).filter(
        Deposit.member_id == user_id
    ).order_by(Deposit.date.desc()).all()
    
    return deposits

@router.get("/", response_model=List[schemas.Deposit])
async def get_all_deposits(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    deposits = db.query(Deposit).order_by(Deposit.date.desc()).all()
    return deposits

@router.get("/balance/{user_id}")
async def get_user_balance(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    user = db.query(SteamUser).filter(SteamUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    

    total_deposits = db.query(func.sum(Deposit.amount)).filter(
        Deposit.member_id == user_id
    ).scalar() or 0
    

    total_expenses = db.query(func.sum(PurchaseShare.share_amount)).filter(
        PurchaseShare.member_id == user_id,
        PurchaseShare.paid == True
    ).scalar() or 0
    
    current_balance = int(total_deposits) - int(total_expenses)
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "profile_image": user.profile_image,
        "total_deposits": int(total_deposits),
        "total_expenses": int(total_expenses),
        "current_balance": current_balance
    }

@router.get("/balances/all")
async def get_all_balances(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    users = db.query(SteamUser).filter(SteamUser.active == True).all()
    
    balances = []
    for user in users:

        total_deposits = db.query(func.sum(Deposit.amount)).filter(
            Deposit.member_id == user.id
        ).scalar() or 0
        
        total_expenses = db.query(func.sum(PurchaseShare.share_amount)).filter(
            PurchaseShare.member_id == user.id,
            PurchaseShare.paid == True
        ).scalar() or 0
        
        current_balance = int(total_deposits) - int(total_expenses)
        
        balances.append({
            "user_id": user.id,
            "user_name": user.name,
            "profile_image": user.profile_image,
            "role": user.role,
            "total_deposits": int(total_deposits),
            "total_expenses": int(total_expenses),
            "current_balance": current_balance
        })
    

    balances.sort(key=lambda x: x["current_balance"], reverse=True)
    
    return {
        "balances": balances,
        "total_users": len(balances),
        "grand_total": sum(b["current_balance"] for b in balances)
    }

