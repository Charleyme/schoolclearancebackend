from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from app.database import get_db
from app.models.user import User
import os
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM","HS256")

oauth2_scheme = HTTPBearer()
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
      
        if not user:
             raise HTTPException(
                status_code=401,
                detail="user not found",
            )
        if not user.is_active:
              raise HTTPException(
                status_code=403,
                detail="Account deactivated",         
            )

        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

def require_roles(*roles):
    def role_checker( current_user: User =  Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail='You are not authorized to perform this action'
            )
        return current_user
    return role_checker
        
        