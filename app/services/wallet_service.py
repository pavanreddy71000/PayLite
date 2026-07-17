from app.models.wallet import Wallet
from app.models.transfer import Transfer
from app.schemas.transfer import TransferHistoryParams
from app.exceptions import WalletNotFoundError, InsufficientFundsError, InvalidTransferError
from sqlalchemy import or_, and_, select, func
import math


async def get_wallet(db, wallet_id):
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    return result.scalar_one_or_none()

async def deposit(db, wallet_id, amount):
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise WalletNotFoundError()
    wallet.balance += amount
    transfer = Transfer(
        sender_wallet_id = None,
        receiver_wallet_id = wallet_id,
        amount = amount
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    return transfer

async def withdraw(db, wallet_id, amount):
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise WalletNotFoundError()
    if wallet.balance < amount:
        raise InsufficientFundsError()
    wallet.balance -= amount
    transfer = Transfer(
        sender_wallet_id = wallet_id,
        receiver_wallet_id = None,
        amount = amount
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    return transfer
 
async def transfer(db, sender_wallet_id, receiver_wallet_id, amount):
    sender_wallet = await get_wallet(db, sender_wallet_id)
    if not sender_wallet:
        raise WalletNotFoundError("Sender wallet not found")
    receiver_wallet = await get_wallet(db, receiver_wallet_id)
    if not receiver_wallet:
        raise WalletNotFoundError("Receiver wallet not found")
    if sender_wallet_id == receiver_wallet_id:
        raise InvalidTransferError("Cannot transfer to the same wallet")
    if sender_wallet.balance < amount:
        raise InsufficientFundsError()
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    transfer = Transfer(
        sender_wallet_id = sender_wallet_id,
        receiver_wallet_id = receiver_wallet_id,
        amount = amount
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    return transfer

async def get_transfer_history(db, wallet_id, params: TransferHistoryParams):
    query = select(Transfer).where(or_(Transfer.sender_wallet_id == wallet_id, Transfer.receiver_wallet_id == wallet_id))
    if params.type is not None:
        if params.type == "deposit":
            query = query.where(Transfer.sender_wallet_id == None)
        elif params.type == "withdrawal":
            query = query.where(Transfer.receiver_wallet_id == None)
        elif params.type == "transfer":
            query = query.where(and_(Transfer.sender_wallet_id != None, Transfer.receiver_wallet_id != None))
    if params.min_amount is not None:
        query = query.where(Transfer.amount >= params.min_amount)
    if params.max_amount is not None:
        query = query.where(Transfer.amount <= params.max_amount)
    if params.from_date is not None:
        query = query.where(Transfer.created_at >= params.from_date)
    if params.to_date is not None:
        query = query.where(Transfer.created_at <= params.to_date)
    ALLOWED_SORT_FIELDS = {"created_at": Transfer.created_at, "amount": Transfer.amount}
    field_name = params.sort.lstrip("-")
    if field_name not in ALLOWED_SORT_FIELDS:
        raise InvalidTransferError(f"Invalid sort field: {field_name}")
    column = ALLOWED_SORT_FIELDS[field_name]
    if params.sort.startswith("-"):
        query = query.order_by(column.desc(), Transfer.id.desc())
    else:
        query = query.order_by(column.asc(), Transfer.id.asc())
    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    offset = (params.page - 1) * params.size
    query = query.offset(offset).limit(params.size)
    results = await db.execute(query)
    results = results.scalars().all()
    return {
        "items": results,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": math.ceil(total/params.size)
    }
