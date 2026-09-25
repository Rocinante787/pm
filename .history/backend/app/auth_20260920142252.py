from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    name: str
    token: str

@router.post("/login", response_model=UserResponse)
async def login(credentials: LoginRequest):
    if credentials.username == "user" and credentials.password == "password":
        return UserResponse(
            username="user",
            name="Demo User",
            token="token-user-pm-session",
        )
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.get("/me")
async def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    if token == "token-user-pm-session":
        return {"username": "user", "name": "Demo User"}
    raise HTTPException(status_code=401, detail="Invalid token")

