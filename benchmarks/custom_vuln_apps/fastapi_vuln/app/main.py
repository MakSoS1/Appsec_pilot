from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AppSec Pilot FastAPI Vulnerable Lab", version="0.1.0")
SECRET = "demo-secret"

USERS = {
    1: {"id": 1, "email": "demo_user@appsec.local", "role": "user", "name": "Demo User"},
    2: {"id": 2, "email": "second_user@appsec.local", "role": "user", "name": "Second User"},
    99: {"id": 99, "email": "demo_admin@appsec.local", "role": "admin", "name": "Demo Admin"},
}
ORDERS = {
    100: {"id": 100, "owner_id": 1, "total": 120.5, "status": "paid"},
    101: {"id": 101, "owner_id": 2, "total": 44.2, "status": "processing"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid token") from exc
    return USERS.get(payload["sub"], USERS[1])


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/login")
def login(payload: LoginRequest):
    user_id = 99 if "admin" in payload.username else 1
    return {"access_token": jwt.encode({"sub": user_id, "role": USERS[user_id]["role"]}, SECRET, algorithm="HS256"), "token_type": "bearer"}


@app.get("/api/users/{id}")
def get_user(id: int, user: dict = Depends(current_user)):
    # Intentional lab flaw: any authenticated user can read any profile.
    if id not in USERS:
        raise HTTPException(404, "User not found")
    return USERS[id]


@app.get("/api/orders/{id}")
def get_order(id: int, user: dict = Depends(current_user)):
    # Intentional lab flaw: object ownership is not checked.
    if id not in ORDERS:
        raise HTTPException(404, "Order not found")
    return ORDERS[id]


@app.get("/api/admin/reports")
def admin_reports(user: dict = Depends(current_user)):
    # Intentional lab flaw: role is not checked.
    return {"reports": [{"id": "rpt_001", "title": "Quarterly revenue", "sensitive": True}]}
