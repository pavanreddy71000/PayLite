from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.services.wallet_service import deposit, withdraw, transfer, get_transfer_history
from app.schemas.wallet import WalletResponse
from app.schemas.transfer import TransferCreate, DepositCreate, WithdrawCreate, TransferResponse, TransferHistoryParams, PaginatedTransferResponse
from app.db.session import get_db
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/wallets')

@router.get("/me", response_model=WalletResponse, status_code=status.HTTP_200_OK)
def current_user_wallet(current_user = Depends(get_current_user)):
    wallet = current_user.wallet
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet

@router.post("/me/deposit", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def deposit_money(deposit_data: DepositCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    wallet = current_user.wallet
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    transfer_info = deposit(db, wallet.id, deposit_data.amount)
    return transfer_info
    
@router.post("/me/withdraw", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def withdraw_money(withdraw_data: WithdrawCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    wallet = current_user.wallet
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    transfer_info = withdraw(db, wallet.id, withdraw_data.amount)
    return transfer_info

@router.post("/me/transfer", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def transfer_money(transfer_data: TransferCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    wallet = current_user.wallet
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    transfer_info = transfer(db, wallet.id, transfer_data.receiver_wallet_id, transfer_data.amount)
    return transfer_info

@router.get("/me/history", response_model=PaginatedTransferResponse, status_code=status.HTTP_200_OK)
def transfer_history(parms: TransferHistoryParams = Depends(), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    wallet = current_user.wallet
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    history = get_transfer_history(db, wallet.id, parms)
    return history