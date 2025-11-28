

from pydantic import BaseModel, EmailStr, Field, validator, field_serializer
from pydantic import ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

class SteamUserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = Field(default='steam', pattern='^(steam|master)$')
    active: Optional[bool] = True

class SteamUserCreate(SteamUserBase):
    auth_uid: Optional[str] = None

class SteamUserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, pattern='^(steam|master)$')
    active: Optional[bool] = None

class SteamUser(SteamUserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    auth_uid: Optional[UUID] = None
    profile_image: Optional[str] = None
    
    @field_serializer('auth_uid')
    def serialize_uuid(self, value: Optional[UUID], _info) -> Optional[str]:
        return str(value) if value else None
    model_config = ConfigDict(from_attributes=True)



class MonthlyCollectionBase(BaseModel):
    due_date: date
    amount_per_member: Decimal = Field(..., gt=0)

class MonthlyCollectionCreate(MonthlyCollectionBase):
    pass

class MonthlyCollection(MonthlyCollectionBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MonthlyCollectionItemBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    paid: bool = False

class MonthlyCollectionItemCreate(MonthlyCollectionItemBase):
    collection_id: int
    member_id: int

class MonthlyCollectionItemUpdate(BaseModel):
    paid: bool
    paid_at: Optional[datetime] = None

class MonthlyCollectionItem(MonthlyCollectionItemBase):
    id: int
    collection_id: int
    member_id: int
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)




class DepositBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    note: Optional[str] = None

class DepositCreate(DepositBase):
    member_id: int
    date: Optional[datetime] = None

class Deposit(DepositBase):
    id: int
    member_id: int
    date: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GameProposalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., gt=0)

class GameProposalCreate(GameProposalBase):
    pass

class GameProposalUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern='^(proposed|voted|purchased|rejected)$')

class GameProposal(GameProposalBase):
    id: int
    proposer_id: int
    status: str
    proposed_at: datetime
    proposal_number: Optional[int] = None
    month_year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class GameProposalWithVotes(GameProposal):
    votes_count: int

    model_config = ConfigDict(from_attributes=True)

class VoteBase(BaseModel):
    vote: bool = True

class VoteCreate(BaseModel):
    pass

class Vote(VoteBase):
    id: int
    proposal_id: int
    member_id: int
    voted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PurchaseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    total_price: Decimal = Field(..., gt=0)
    was_on_sale: bool = False
    original_price: Optional[Decimal] = None

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseFromProposal(BaseModel):
    was_on_sale: bool = False
    original_price: Optional[Decimal] = None

class PurchaseUpdate(BaseModel):
    purchaser_id: int

class Purchase(PurchaseBase):
    id: int
    proposal_id: Optional[int] = None
    purchaser_id: Optional[int] = None
    owner_id: Optional[int] = None
    purchased_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PurchaseShareBase(BaseModel):
    share_amount: Decimal = Field(..., gt=0)
    paid: bool = False

class PurchaseShareCreate(PurchaseShareBase):
    purchase_id: int
    member_id: int

class PurchaseShareUpdate(BaseModel):
    paid: bool
    paid_at: Optional[datetime] = None

class PurchaseShare(PurchaseShareBase):
    id: int
    purchase_id: int
    member_id: int
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AdjustmentBase(BaseModel):
    amount: Decimal
    reason: Optional[str] = None

class AdjustmentCreate(AdjustmentBase):
    member_id: int

class Adjustment(AdjustmentBase):
    id: int
    member_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SettingBase(BaseModel):
    value: Optional[dict] = None

class SettingCreate(SettingBase):
    key: str

class SettingUpdate(SettingBase):
    pass

class Setting(SettingBase):
    key: str
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogCreate(BaseModel):
    actor_member_id: Optional[int] = None
    action: str
    payload: Optional[dict] = None

class AuditLog(AuditLogCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MemberBalance(BaseModel):
    member_id: int
    member_name: str
    total_deposits: Decimal
    total_collection_items: Decimal
    total_purchase_shares: Decimal
    total_adjustments: Decimal
    balance: Decimal
    
class CollectionWithItems(MonthlyCollection):
    items: List[MonthlyCollectionItem] = []

class ProposalWithVotes(GameProposal):
    votes: List[Vote] = []
    total_votes: int = 0
    votes_in_favor: int = 0

class PurchaseWithShares(Purchase):
    shares: List[PurchaseShare] = []
