from fastapi import Depends
from sqlalchemy.orm import Session

from auth import get_current_user, get_optional_user
from database import get_db
from service_mesh import ServiceMesh


def get_service_mesh(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
) -> ServiceMesh:
    return ServiceMesh(user=current_user, db=db)


def get_optional_service_mesh(
        current_user=Depends(get_optional_user),
        db: Session = Depends(get_db),
) -> ServiceMesh:
    return ServiceMesh(user=current_user, db=db)