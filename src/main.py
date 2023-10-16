from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tortoise.contrib.fastapi import register_tortoise
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save

from database.models import *
from authentication import hash_password, verify_token
from src.email import send_mail

from typing import Optional, Type, List


app = FastAPI()


@post_save(User)
async def create_business(
    sender: 'Type[User]',
    instance: User,
    created: bool,
    db: 'Optional[BaseDBAsyncClient]',
    update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name = instance.username, owner = instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)

        await send_mail([instance.email], instance)


@app.post('/registration')
async def register(user: user_pydantic_in):
    user_info = user.dict(exclude_onset=True)
    password = user_info['password']
    user_info['password'] = hash_password(password=password)

    print('unpacked', **user_info)

    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)

    return{
        'status': '200',
        'data': new_user.username,
        'message': f'Hello {new_user.username}, welcome aboard! Please check ypur email to verify your account'
    }



templates = Jinja2Templates(directory='templates')
@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified():
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse('verification.html', 
                                          {'request': request, 'username': user.username})
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'Authenticate': 'Bearer'}
        )

@app.get('/')
def index():
    return {'message': 'Hello there'}

register_tortoise(
    app=app,
    db_url='sqlite://database.sqlite3',
    modules={'models': ['database.models']},
    generate_schemas=True,
    add_exception_handlers=True
)