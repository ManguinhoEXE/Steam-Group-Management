from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import SteamUser, GameProposal, Vote
from app.utils.auth import get_current_active_user, require_master_role
from app.schemas import schemas

router = APIRouter(prefix="/proposals", tags=["Game Proposals"])

SYSTEM_START_DATE = datetime(2025, 1, 1)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_proposal(
    proposal_data: schemas.GameProposalCreate,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    existing_proposal = db.query(GameProposal).filter(
        GameProposal.proposer_id == current_user.id,
        GameProposal.status.in_(['proposed', 'voted'])
    ).first()
    
    if existing_proposal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya tienes una propuesta activa: '{existing_proposal.title}' (ID: {existing_proposal.id}, Estado: {existing_proposal.status})"
        )
    

    now = datetime.utcnow()
    month_year = int(now.strftime("%Y%m"))
    

    existing_month_proposal = db.query(GameProposal).filter(
        GameProposal.month_year == month_year
    ).first()
    
    if existing_month_proposal:

        proposal_number = existing_month_proposal.proposal_number
    else:

        max_proposal = db.query(func.max(GameProposal.proposal_number)).scalar()
        proposal_number = (max_proposal + 1) if max_proposal else 1
    

    new_proposal = GameProposal(
        title=proposal_data.title,
        proposer_id=current_user.id,
        price=proposal_data.price,
        status='proposed',
        proposal_number=proposal_number,
        month_year=month_year
    )
    
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    
    return {
        "message": "Propuesta creada exitosamente",
        "proposal": {
            "id": new_proposal.id,
            "title": new_proposal.title,
            "price": new_proposal.price,
            "proposer_id": new_proposal.proposer_id,
            "proposer_name": current_user.name,
            "status": new_proposal.status,
            "proposal_number": new_proposal.proposal_number,
            "month_year": new_proposal.month_year,
            "proposed_at": new_proposal.proposed_at
        }
    }

@router.get("/", response_model=List[schemas.GameProposal])
async def get_all_proposals(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    
    query = db.query(GameProposal)
    
    if status_filter:
        query = query.filter(GameProposal.status == status_filter)
    
    proposals = query.order_by(GameProposal.proposed_at.desc()).all()
    return proposals

@router.get("/my-vote")
async def get_my_current_vote(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    vote = db.query(Vote, GameProposal).join(
        GameProposal, Vote.proposal_id == GameProposal.id
    ).filter(
        Vote.member_id == current_user.id,
        GameProposal.status == 'proposed'
    ).first()
    
    if not vote:
        return {
            "has_vote": False,
            "message": "No tienes ningún voto activo"
        }
    
    vote_obj, proposal = vote
    

    total_votes = db.query(Vote).filter(Vote.proposal_id == proposal.id).count()
    
    return {
        "has_vote": True,
        "vote": {
            "proposal_id": int(proposal.id),
            "proposal_title": proposal.title,
            "proposer_id": int(proposal.proposer_id),
            "price": int(proposal.price),
            "voted_at": vote_obj.voted_at,
            "total_votes": total_votes
        }
    }

@router.get("/{proposal_id}")
async def get_proposal_with_votes(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    
    proposal = db.query(GameProposal).filter(GameProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propuesta con ID {proposal_id} no encontrada"
        )
    

    total_votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).count()
    

    votes_detail = db.query(Vote, SteamUser).join(
        SteamUser, Vote.member_id == SteamUser.id
    ).filter(Vote.proposal_id == proposal_id).all()
    
    votes_list = [
        {
            "member_id": vote.member_id,
            "member_name": user.name,
            "voted_at": vote.voted_at
        }
        for vote, user in votes_detail
    ]
    

    total_users = db.query(SteamUser).filter(
        SteamUser.active == True,
        SteamUser.id != proposal.proposer_id
    ).count()
    
    return {
        "proposal": {
            "id": proposal.id,
            "title": proposal.title,
            "price": proposal.price,
            "status": proposal.status,
            "proposed_at": proposal.proposed_at,
            "proposer_id": proposal.proposer_id
        },
        "voting_summary": {
            "votes_favor": total_votes,
            "total_votes": total_votes,
            "eligible_voters": total_users,
            "participation_rate": f"{(total_votes / total_users * 100):.1f}%" if total_users > 0 else "0%"
        },
        "votes": votes_list
    }

@router.post("/{proposal_id}/vote")
async def vote_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    proposal = db.query(GameProposal).filter(GameProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propuesta con ID {proposal_id} no encontrada"
        )
    

    if proposal.status != 'proposed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede votar. La propuesta está en estado: {proposal.status}"
        )
    

    if proposal.proposer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes votar tu propia propuesta"
        )
    

    existing_vote = db.query(Vote).join(
        GameProposal, Vote.proposal_id == GameProposal.id
    ).filter(
        Vote.member_id == current_user.id,
        GameProposal.status == 'proposed'
    ).first()
    
    previous_proposal_title = None
    vote_changed = False
    
    if existing_vote:

        if existing_vote.proposal_id == proposal_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya has votado en esta propuesta"
            )
        

        previous_proposal = db.query(GameProposal).filter(
            GameProposal.id == existing_vote.proposal_id
        ).first()
        
        previous_proposal_title = previous_proposal.title if previous_proposal else "Propuesta anterior"
        
        db.delete(existing_vote)
        vote_changed = True
    

    new_vote = Vote(
        proposal_id=proposal_id,
        member_id=current_user.id,
        vote=True
    )
    
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    

    total_votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).count()
    
    message = "Voto cambiado exitosamente" if vote_changed else "Voto registrado exitosamente"
    
    response = {
        "message": message,
        "vote": {
            "proposal_id": proposal_id,
            "proposal_title": proposal.title,
            "member_id": current_user.id,
            "member_name": current_user.name,
            "voted_at": new_vote.voted_at
        },
        "current_votes": total_votes
    }
    
    if vote_changed:
        response["previous_vote"] = {
            "proposal_title": previous_proposal_title,
            "message": f"Tu voto anterior en '{previous_proposal_title}' ha sido eliminado"
        }
    
    return response

@router.delete("/my-vote")
async def remove_my_vote(
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(get_current_active_user)
):
    

    vote = db.query(Vote).join(
        GameProposal, Vote.proposal_id == GameProposal.id
    ).filter(
        Vote.member_id == current_user.id,
        GameProposal.status == 'proposed'
    ).first()
    
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes ningún voto activo para eliminar"
        )
    

    proposal = db.query(GameProposal).filter(GameProposal.id == vote.proposal_id).first()
    proposal_title = proposal.title if proposal else "Desconocido"
    
    db.delete(vote)
    db.commit()
    
    return {
        "message": "Voto eliminado exitosamente",
        "removed_from": {
            "proposal_id": vote.proposal_id,
            "proposal_title": proposal_title
        }
    }

@router.post("/{proposal_id}/select-winner")
async def select_winner(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    

    winner_proposal = db.query(GameProposal).filter(GameProposal.id == proposal_id).first()
    if not winner_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propuesta con ID {proposal_id} no encontrada"
        )
    
    if winner_proposal.status != 'proposed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La propuesta debe estar en estado 'proposed'. Estado actual: {winner_proposal.status}"
        )
    

    winner_votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).count()
    

    winner_proposal.status = 'voted'
    

    rejected_proposals = db.query(GameProposal).filter(
        GameProposal.status == 'proposed',
        GameProposal.id != proposal_id
    ).all()
    
    rejected_count = 0
    rejected_list = []
    for prop in rejected_proposals:
        prop.status = 'rejected'
        rejected_count += 1
        votes_count = db.query(Vote).filter(Vote.proposal_id == prop.id).count()
        rejected_list.append({
            "id": prop.id,
            "title": prop.title,
            "votes": votes_count
        })
    
    db.commit()
    
    return {
        "message": "Ganador seleccionado exitosamente",
        "winner": {
            "id": winner_proposal.id,
            "title": winner_proposal.title,
            "proposer_id": winner_proposal.proposer_id,
            "price": winner_proposal.price,
            "votes": winner_votes,
            "status": "voted"
        },
        "rejected_proposals": {
            "count": rejected_count,
            "proposals": rejected_list
        }
    }

@router.delete("/{proposal_id}")
async def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: SteamUser = Depends(require_master_role)
):
    
    proposal = db.query(GameProposal).filter(GameProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propuesta con ID {proposal_id} no encontrada"
        )
    
    db.delete(proposal)
    db.commit()
    
    return {"message": f"Propuesta '{proposal.title}' eliminada exitosamente"}
