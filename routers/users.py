from typing import List

from fastapi import APIRouter, Depends

import schemas
from dependencies import get_optional_service_mesh, get_service_mesh
from service_mesh import ServiceMesh
from services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=201)
async def create_user(user: schemas.UserCreate, mesh: ServiceMesh = Depends(get_optional_service_mesh)):
    """
    Create a new user.
    """
    return mesh.get_service(UserService).create_user(user)


@router.get("/", response_model=List[schemas.User])
async def list_users(mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    List all users.
    """
    return mesh.get_service(UserService).list_users()


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific user by ID.
    """
    return mesh.get_service(UserService).get_user(user_id)