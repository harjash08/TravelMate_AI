from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.redis import redis_client
from db.database import get_db
from db.models import UserModel
import redis 
import json
from types import SimpleNamespace
from core.security import (
    oauth2_scheme,
    verify_access_token
)


def is_authenticated(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_access_token(token)

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    cached_key=f"user{user_id}"
    try:
        
        cached_user=redis_client.get(cached_key)

    except redis.RedisError:
        cached_user = None
    if cached_user:
        return SimpleNamespace(**json.loads(cached_user))

    user = db.query(UserModel).filter(
        UserModel.user_id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    user_data = {
        "id": user.user_id,
        "username": user.username,
        "email": user.email
    }

    # Step 6: Store in Redis for 5 minutes
    try:
        redis_client.setex(
            cached_key,
            300,
            json.dumps(user_data)
        )
    except redis.RedisError:
        pass

    return user.user_id

    