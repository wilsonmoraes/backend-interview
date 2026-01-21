from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db


def get_current_user(
    x_user_id: int = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> models.User:
    user = (
        db.query(models.User)
        .filter(models.User.id == x_user_id, models.User.owner_id == x_user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    return user


def get_optional_user(
    x_user_id: Optional[int] = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if x_user_id is None:
        return None
    user = (
        db.query(models.User)
        .filter(models.User.id == x_user_id, models.User.owner_id == x_user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    return user