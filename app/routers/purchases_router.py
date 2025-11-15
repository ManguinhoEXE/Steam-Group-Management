from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models import SteamUser, GameProposal, Purchase, PurchaseShare, Deposit
from app.utils.auth import get_current_active_user, require_master_role
from app.schemas import schemas

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("/from-proposal/{proposal_id}", status_code=status.HTTP_201_CREATED)
async def create_purchase_from_proposal(
    proposal_id: int,
    purchase_data: schemas.PurchaseFromProposal,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    

    proposal = db.query(GameProposal).filter(GameProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propuesta con ID {proposal_id} no encontrada"
        )
    
    if proposal.status != 'voted':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La propuesta debe estar aprobada (voted). Estado actual: {proposal.status}"
        )
    

    active_users = db.query(SteamUser).filter(SteamUser.active == True).all()
    total_users = len(active_users)
    
    if total_users != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El grupo debe tener exactamente 6 usuarios activos. Actualmente hay {total_users}"
        )
    

    proposer = db.query(SteamUser).filter(SteamUser.id == proposal.proposer_id).first()
    if not proposer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propietario con ID {proposal.proposer_id} no encontrado"
        )
    

    final_price = proposal.price
    

    was_on_sale = purchase_data.was_on_sale
    original_price_value = int(purchase_data.original_price) if purchase_data.original_price else None
    

    final_price_int = int(final_price)
    

    owner_share = int(final_price_int * 0.40)
    remaining = final_price_int - owner_share
    share_per_other = int(remaining / 5)
    

    total_calculated = owner_share + (share_per_other * 5)
    remainder = final_price_int - total_calculated
    owner_final_share = owner_share + remainder
    

    def get_user_balance(user_id: int) -> int:
        deposits = db.query(func.sum(Deposit.amount)).filter(Deposit.member_id == user_id).scalar() or 0
        expenses = db.query(func.sum(PurchaseShare.share_amount)).filter(
            PurchaseShare.member_id == user_id,
            PurchaseShare.paid == True
        ).scalar() or 0

        return int(deposits) - int(expenses)
    

    proposer_balance = get_user_balance(proposer.id)
    if proposer_balance < owner_final_share:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente para {proposer.name} (propietario). Necesita: ${owner_final_share:,}, Tiene: ${proposer_balance:,}"
        )
    

    insufficient_balance_users = []
    for user in active_users:
        if user.id != proposer.id:
            user_balance = get_user_balance(user.id)
            if user_balance < share_per_other:
                insufficient_balance_users.append({
                    "name": user.name,
                    "required": share_per_other,
                    "balance": user_balance
                })
    
    if insufficient_balance_users:
        details = "\n".join([
            f"- {u['name']}: Necesita ${u['required']:,}, Tiene ${u['balance']:,}"
            for u in insufficient_balance_users
        ])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente para algunos usuarios:\n{details}"
        )
    

    new_purchase = Purchase(
        proposal_id=proposal_id,
        title=proposal.title,
        total_price=final_price,
        purchaser_id=current_user.id,
        was_on_sale=was_on_sale,
        original_price=original_price_value
    )
    
    db.add(new_purchase)
    db.flush()
    

    shares_created = []
    

    new_owner_balance = proposer_balance - owner_final_share
    owner_share_obj = PurchaseShare(
        purchase_id=new_purchase.id,
        member_id=proposer.id,
        share_amount=owner_final_share,
        paid=True,
        paid_at=datetime.utcnow()
    )
    db.add(owner_share_obj)
    shares_created.append({
        "member_id": proposer.id,
        "member_name": proposer.name,
        "share_amount": owner_final_share,
        "role": "PROPIETARIO (40%)",
        "previous_balance": proposer_balance,
        "new_balance": new_owner_balance
    })
    

    for user in active_users:
        if user.id != proposer.id:
            user_balance = get_user_balance(user.id)
            new_user_balance = user_balance - share_per_other
            
            other_share = PurchaseShare(
                purchase_id=new_purchase.id,
                member_id=user.id,
                share_amount=share_per_other,
                paid=True,
                paid_at=datetime.utcnow()
            )
            db.add(other_share)
            
            shares_created.append({
                "member_id": user.id,
                "member_name": user.name,
                "share_amount": share_per_other,
                "role": "PARTICIPANTE (12%)",
                "previous_balance": user_balance,
                "new_balance": new_user_balance
            })
    

    proposal.status = 'purchased'
    
    db.commit()
    db.refresh(new_purchase)
    
    return {
        "message": "✅ Compra realizada y saldos descontados exitosamente",
        "purchase": {
            "id": new_purchase.id,
            "title": new_purchase.title,
            "total_price": new_purchase.total_price,
            "was_on_sale": new_purchase.was_on_sale,
            "original_price": new_purchase.original_price,
            "purchaser_id": new_purchase.purchaser_id,
            "purchaser_name": current_user.name,
            "purchased_at": new_purchase.purchased_at
        },
        "shares_breakdown": {
            "total_price": final_price_int,
            "owner_pays_40%": owner_final_share,
            "others_pay_60%": remaining,
            "per_other_user_12%": share_per_other,
            "proposer": {
                "id": proposer.id,
                "name": proposer.name,
                "amount": owner_final_share
            }
        },
        "balance_changes": shares_created
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_manual_purchase(
    purchase_data: schemas.PurchaseCreate,
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    

    active_users = db.query(SteamUser).filter(SteamUser.active == True).all()
    total_users = len(active_users)
    
    if total_users != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El grupo debe tener exactamente 6 usuarios activos. Actualmente hay {total_users}"
        )
    

    owner = db.query(SteamUser).filter(
        SteamUser.id == owner_id,
        SteamUser.active == True
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {owner_id} no encontrado o no está activo"
        )
    

    total_price = int(purchase_data.total_price)
    owner_share = int(total_price * 0.40)
    remaining = total_price - owner_share
    share_per_other = int(remaining / 5)
    

    total_calculated = owner_share + (share_per_other * 5)
    remainder = total_price - total_calculated
    owner_final_share = owner_share + remainder
    

    def get_user_balance(user_id: int) -> int:
        deposits = db.query(func.sum(Deposit.amount)).filter(Deposit.member_id == user_id).scalar() or 0
        expenses = db.query(func.sum(PurchaseShare.share_amount)).filter(
            PurchaseShare.member_id == user_id,
            PurchaseShare.paid == True
        ).scalar() or 0

        return int(deposits) - int(expenses)
    

    owner_balance = get_user_balance(owner.id)
    if owner_balance < owner_final_share:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente para {owner.name} (propietario). Necesita: ${owner_final_share:,}, Tiene: ${owner_balance:,}"
        )
    

    insufficient_balance_users = []
    for user in active_users:
        if user.id != owner.id:
            user_balance = get_user_balance(user.id)
            if user_balance < share_per_other:
                insufficient_balance_users.append({
                    "name": user.name,
                    "required": share_per_other,
                    "balance": user_balance
                })
    
    if insufficient_balance_users:
        details = "\n".join([
            f"- {u['name']}: Necesita ${u['required']:,}, Tiene ${u['balance']:,}"
            for u in insufficient_balance_users
        ])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente para algunos usuarios:\n{details}"
        )
    

    new_purchase = Purchase(
        proposal_id=None,
        title=purchase_data.title,
        total_price=total_price,
        purchaser_id=current_user.id,
        was_on_sale=purchase_data.was_on_sale,
        original_price=purchase_data.original_price
    )
    
    db.add(new_purchase)
    db.flush()
    

    shares_created = []
    

    owner_share_obj = PurchaseShare(
        purchase_id=new_purchase.id,
        member_id=owner.id,
        share_amount=owner_final_share,
        paid=True,
        paid_at=datetime.utcnow()
    )
    db.add(owner_share_obj)
    shares_created.append({
        "member_id": owner.id,
        "member_name": owner.name,
        "share_amount": owner_final_share,
        "role": "PROPIETARIO (40%)",
        "previous_balance": owner_balance,
        "new_balance": owner_balance - owner_final_share
    })
    

    for user in active_users:
        if user.id != owner.id:
            user_balance = get_user_balance(user.id)
            share = PurchaseShare(
                purchase_id=new_purchase.id,
                member_id=user.id,
                share_amount=share_per_other,
                paid=True,
                paid_at=datetime.utcnow()
            )
            db.add(share)
            shares_created.append({
                "member_id": user.id,
                "member_name": user.name,
                "share_amount": share_per_other,
                "role": "PARTICIPANTE (12%)",
                "previous_balance": user_balance,
                "new_balance": user_balance - share_per_other
            })
    
    db.commit()
    db.refresh(new_purchase)
    
    return {
        "message": "✅ Compra manual realizada y saldos descontados exitosamente",
        "purchase": {
            "id": new_purchase.id,
            "title": new_purchase.title,
            "total_price": new_purchase.total_price,
            "was_on_sale": new_purchase.was_on_sale,
            "original_price": new_purchase.original_price,
            "purchaser_id": new_purchase.purchaser_id,
            "purchaser_name": current_user.name,
            "purchased_at": new_purchase.purchased_at
        },
        "shares_breakdown": {
            "total_price": total_price,
            "owner_pays_40%": owner_final_share,
            "others_pay_60%": remaining,
            "per_other_user_12%": share_per_other,
            "owner": {
                "id": owner.id,
                "name": owner.name,
                "amount": owner_final_share
            }
        },
        "balance_changes": shares_created
    }

@router.get("/", response_model=List[schemas.Purchase])
async def get_all_purchases(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    purchases = db.query(Purchase).order_by(Purchase.purchased_at.desc()).all()
    return purchases

@router.get("/{purchase_id}")
async def get_purchase_with_shares(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compra con ID {purchase_id} no encontrada"
        )
    

    shares = db.query(PurchaseShare, SteamUser).join(
        SteamUser, PurchaseShare.member_id == SteamUser.id
    ).filter(PurchaseShare.purchase_id == purchase_id).all()
    
    shares_list = [
        {
            "share_id": share.id,
            "member_id": share.member_id,
            "member_name": user.name,
            "share_amount": share.share_amount,
            "paid": share.paid,
            "paid_at": share.paid_at
        }
        for share, user in shares
    ]
    

    total_paid = sum(s.share_amount for s, u in shares if s.paid)
    total_pending = sum(s.share_amount for s, u in shares if not s.paid)
    users_paid = sum(1 for s, u in shares if s.paid)
    users_pending = sum(1 for s, u in shares if not s.paid)
    
    return {
        "purchase": {
            "id": purchase.id,
            "title": purchase.title,
            "total_price": purchase.total_price,
            "was_on_sale": purchase.was_on_sale,
            "original_price": purchase.original_price,
            "purchaser_id": purchase.purchaser_id,
            "purchased_at": purchase.purchased_at
        },
        "shares": shares_list,
        "summary": {
            "total_amount": purchase.total_price,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "users_paid": users_paid,
            "users_pending": users_pending,
            "completion_rate": f"{(users_paid / len(shares) * 100):.1f}%" if shares else "0%"
        }
    }

@router.get("/my-shares/pending")
async def get_my_pending_shares(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    
    pending_shares = db.query(PurchaseShare, Purchase).join(
        Purchase, PurchaseShare.purchase_id == Purchase.id
    ).filter(
        PurchaseShare.member_id == current_user.id,
        PurchaseShare.paid == False
    ).all()
    
    pending_list = [
        {
            "share_id": share.id,
            "purchase_id": purchase.id,
            "game_title": purchase.title,
            "share_amount": share.share_amount,
            "purchased_at": purchase.purchased_at
        }
        for share, purchase in pending_shares
    ]
    
    total_pending = sum(share.share_amount for share, _ in pending_shares)
    
    return {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "pending_shares": pending_list,
        "total_pending": total_pending,
        "count": len(pending_list)
    }
