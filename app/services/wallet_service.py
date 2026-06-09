from app.models.wallet import Wallet
from app.models.transfer import Transfer
from fastapi import HTTPException, status


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
