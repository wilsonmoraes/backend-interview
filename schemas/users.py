from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., description="User name.", examples=["Maria Silva"])
    email: EmailStr = Field(..., description="User email.", examples=["maria@example.com"])


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int = Field(..., description="User identifier.", examples=[1])

    class Config:
        from_attributes = True