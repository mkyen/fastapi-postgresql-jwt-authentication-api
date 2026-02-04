from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.models import Item, User

router = APIRouter(prefix="/items", tags=["Items"])

def get_item_or_404(item_id: int, user_id: int, db: Session):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_item = Item(**item.dict(), owner_id=user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/", response_model=List[ItemResponse])
def list_items(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Item).filter(Item.owner_id == user.id).all()

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_item_or_404(item_id, user.id, db)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = get_item_or_404(item_id, user.id, db)
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.delete(get_item_or_404(item_id, user.id, db))
    db.commit()