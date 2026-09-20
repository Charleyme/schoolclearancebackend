from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserRegister, UserLogin
from app.models.user import User
from app.auth.security import hash_password, verify_password, create_access_token



def register(db: Session, user_data: UserRegister):
   existing_username= db.query(User).filter(User.username == user_data.username).first()
   if existing_username:
      raise HTTPException(
         status_code= 400,
         detail="Username already exists"
      )
   existing_email = db.query(User).filter(User.email == user_data.email).first()
   if existing_email:
      raise HTTPException(
         status_code=400,
         detail="Email already exists"
      )
   new_user = User(
      username = user_data.username,
      email=user_data.email,
      password_hash = hash_password(user_data.password),
      role = "student"
   )
   db.add(new_user)
   db.commit()
   db.refresh(new_user)

   return new_user
def login_user(db: Session, user_data: UserLogin):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(
            status_code= 401,
            detail="Invalid username or password"
        )
    if not  verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    token = create_access_token(user.id, user.username,user.role)
    return{
        "message": "Login successful",
        "username": user.username,
        "user":{
            'id': user.id,
            'username': user.username,
            "role": user.role,
        },
        "access_token": token,
        "token_type": "bearer" 
    }
