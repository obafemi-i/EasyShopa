from fastapi import HTTPException, status
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import os

from database.models import User

load_dotenv()

secret_key = os.getenv('SECRET')

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password):
    return password_context.hash(password)

async def verify_token(token:str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'Authenticate': 'Bearer'}
        )
    
    return user


async def authenticate_user(username, password):
    user = await User.get(username=username)

#     if user and verify_password
# async def token_generator(username: str, password: str):
#     pass