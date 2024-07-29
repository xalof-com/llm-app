from fastapi import APIRouter, Body, Request
from typing import Any, Optional, Annotated
from app.hash import Hash, JWTToken

router = APIRouter(
    prefix="/auth"
)

@router.post("/access-token")
def ask_access_token(email:Annotated[str, Body()], pwd:Annotated[str, Body()]) -> Any:
    return JWTToken.get_access_token({'sub': email})