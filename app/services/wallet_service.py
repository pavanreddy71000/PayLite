from app.models.wallet import Wallet
from app.models.transfer import Transfer
from app.schemas.transfer import TransferHistoryParams
from fastapi import HTTPException, status
from sqlalchemy import or_, and_
import math


def get_wallet(db, wallet_id):
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()

def deposit(db, wallet_id, amount):
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    wallet.balance += amount
    transfer = Transfer(
        sender_wallet_id = None,
        receiver_wallet_id = wallet_id,
        amount = amount
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer

def withdraw(db, wallet_id, amount):
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    if wallet.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    wallet.balance -= amount
    transfer = Transfer(
        sender_wallet_id = wallet_id,
        receiver_wallet_id = None,
        amount = amount
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer
 
def transfer(db, sender_wallet_id, receiver_wallet_id, amount):
    sender_wallet = get_wallet(db, sender_wallet_id)
    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender wallet not found")
    receiver_wallet = get_wallet(db, receiver_wallet_id)
    if not receiver_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver wallet not found")
    if sender_wallet_id == receiver_wallet_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to the same wallet")
    if sender_wallet.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    transfer = Transfer(
        sender_wallet_id = sender_wallet_id,
        receiver_wallet_id = receiver_wallet_id,
        amount = amount
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer

def get_transfer_history(db, wallet_id, params: TransferHistoryParams):
    query = db.query(Transfer).filter(or_(Transfer.sender_wallet_id == wallet_id, Transfer.receiver_wallet_id == wallet_id))
    if params.type is not None:
        if params.type == "deposit":
            query = query.filter(Transfer.sender_wallet_id == None)
        elif params.type == "withdrawal":
            query = query.filter(Transfer.receiver_wallet_id == None)
        elif params.type == "transfer":
            query = query.filter(and_(Transfer.sender_wallet_id != None, Transfer.receiver_wallet_id != None))
    if params.min_amount is not None:
        query = query.filter(Transfer.amount >= params.min_amount)
    if params.max_amount is not None:
        query = query.filter(Transfer.amount <= params.max_amount)
    if params.from_date is not None:
        query = query.filter(Transfer.created_at >= params.from_date)
    if params.to_date is not None:
        query = query.filter(Transfer.created_at <= params.to_date)
    ALLOWED_SORT_FIELDS = {"created_at": Transfer.created_at, "amount": Transfer.amount}
    field_name = params.sort.lstrip("-")
    if field_name not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {field_name}")
    column = ALLOWED_SORT_FIELDS[field_name]
    if params.sort.startswith("-"):
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())
    total = query.count()
    offset = (params.page - 1) * params.size
    query = query.offset(offset).limit(params.size)
    results = query.all()
    return {
        "items": results,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": math.ceil(total/params.size)
    }
