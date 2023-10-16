from fastapi import BackgroundTasks, File, Form, Depends, UploadFile, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from typing import List
from database.models import User
import os
from dotenv import load_dotenv
import jwt

load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
secret_key = os.getenv('SECRET')


conf = ConnectionConfig(
    MAIL_USERNAME=username,
    MAIL_PASSWORD=password,
    MAIL_FROM=username,
    MAIL_PORT=1025,
    MAIL_FROM_NAME='EasyShopa',
    MAIL_SERVER='127.0.0.1',
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)


async def send_mail(email: List, instance: User):
    token_obj = {
        'id': instance.id,
        'username': instance.username
    }

    token = jwt.encode(token_obj, secret_key, algorithm='HS256')

    html_msg = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <body>
                <div style = "display: flex; align-items: center; justify-content: 
                center; flex-direction: column">

                    <h3> Account Verification </h3>
                    <br>

                    <p>
                    Thanks for choosing EasyShopas, please click the button below to verify your account.
                    </p>

                    <a style = "margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; 
                    text-decoration: none; background: #0275d8; color: white;" href="http://localhost:8000/verification/?token={token}"> 
                    Verify your email
                    </a>
                </div>
            </body>
        </head>
    </html>
    """

    message = MessageSchema(
        subject = 'EasyShopa Account Verification',
        body = html_msg,
        recipients = email,         # email.model_dump().get("email")
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message=message)