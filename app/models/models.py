from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, ForeignKey, Integer, JSON, UniqueConstraint, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Modelo para proposals_turn
class ProposalsTurn(Base):
    __tablename__ = 'proposals_turn'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(Boolean, nullable=False, default=True)

class SteamUser(Base):
    __tablename__ = 'steamuser'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    role = Column(Text, nullable=False, default='steam')
    auth_uid = Column(UUID(as_uuid=True), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    profile_image = Column(Text, nullable=True)
    collection_items = relationship('MonthlyCollectionItem', back_populates='member')
    deposits = relationship('Deposit', back_populates='member')
    proposals = relationship('GameProposal', back_populates='proposer')
    votes = relationship('Vote', back_populates='member')
    purchases = relationship('Purchase', back_populates='purchaser', foreign_keys='Purchase.purchaser_id')
    purchase_shares = relationship('PurchaseShare', back_populates='member')
    adjustments = relationship('Adjustment', back_populates='member')
    audit_logs = relationship('AuditLog', back_populates='actor_member')

class MonthlyCollection(Base):
    __tablename__ = 'monthly_collections'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    due_date = Column(Date, nullable=False)
    amount_per_member = Column(Integer, nullable=False, default=10000)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    items = relationship('MonthlyCollectionItem', back_populates='collection', cascade='all, delete-orphan')

class MonthlyCollectionItem(Base):
    __tablename__ = 'monthly_collection_items'
    __table_args__ = (UniqueConstraint('collection_id', 'member_id', name='monthly_collection_items_collection_id_member_id_key'), {'schema': 'public'})
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    collection_id = Column(BigInteger, ForeignKey('public.monthly_collections.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    paid = Column(Boolean, nullable=False, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    collection = relationship('MonthlyCollection', back_populates='items')
    member = relationship('SteamUser', back_populates='collection_items')

class Deposit(Base):
    __tablename__ = 'deposits'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    member = relationship('SteamUser', back_populates='deposits')

class GameProposal(Base):
    __tablename__ = 'game_proposals'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    proposer_id = Column(BigInteger, ForeignKey('public.steamuser.id'), nullable=False)
    price = Column(Integer, nullable=False)
    proposed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(Text, nullable=False, default='proposed')
    proposal_number = Column(Integer, nullable=True)
    month_year = Column(Integer, nullable=True)
    proposer = relationship('SteamUser', back_populates='proposals')
    votes = relationship('Vote', back_populates='proposal', cascade='all, delete-orphan')
    purchases = relationship('Purchase', back_populates='proposal')

class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = (UniqueConstraint('proposal_id', 'member_id', name='votes_proposal_id_member_id_key'), {'schema': 'public'})
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    proposal_id = Column(BigInteger, ForeignKey('public.game_proposals.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id'), nullable=False)
    vote = Column(Boolean, nullable=False)
    voted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    proposal = relationship('GameProposal', back_populates='votes')
    member = relationship('SteamUser', back_populates='votes')

class Purchase(Base):
    __tablename__ = 'purchases'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    proposal_id = Column(BigInteger, ForeignKey('public.game_proposals.id'), nullable=True)
    title = Column(Text, nullable=False)
    total_price = Column(Integer, nullable=False)
    purchaser_id = Column(BigInteger, ForeignKey('public.steamuser.id'), nullable=False)
    owner_id = Column(BigInteger, ForeignKey('public.steamuser.id'), nullable=False)
    purchased_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    was_on_sale = Column(Boolean, nullable=False, default=False)
    original_price = Column(Integer, nullable=True)
    proposal = relationship('GameProposal', back_populates='purchases')
    purchaser = relationship('SteamUser', back_populates='purchases', foreign_keys=[purchaser_id])
    owner = relationship('SteamUser', foreign_keys=[owner_id])
    shares = relationship('PurchaseShare', back_populates='purchase', cascade='all, delete-orphan')

class PurchaseShare(Base):
    __tablename__ = 'purchase_shares'
    __table_args__ = (UniqueConstraint('purchase_id', 'member_id', name='purchase_shares_purchase_id_member_id_key'), {'schema': 'public'})
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(BigInteger, ForeignKey('public.purchases.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id'), nullable=False)
    share_amount = Column(Integer, nullable=False)
    paid = Column(Boolean, nullable=False, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    purchase = relationship('Purchase', back_populates='shares')
    member = relationship('SteamUser', back_populates='purchase_shares')

class Adjustment(Base):
    __tablename__ = 'adjustments'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    member = relationship('SteamUser', back_populates='adjustments')

class Balance(Base):
    __tablename__ = 'balance'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(BigInteger, ForeignKey('public.steamuser.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_deposits = Column(Integer, nullable=False, default=0)
    total_expenses = Column(Integer, nullable=False, default=0)
    current_balance = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    member = relationship('SteamUser', backref='balance')

class Setting(Base):
    __tablename__ = 'settings'
    __table_args__ = {'schema': 'public'}
    key = Column(Text, primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = {'schema': 'public'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor_member_id = Column(BigInteger, ForeignKey('public.steamuser.id', ondelete='SET NULL'), nullable=True)
    action = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    actor_member = relationship('SteamUser', back_populates='audit_logs')
