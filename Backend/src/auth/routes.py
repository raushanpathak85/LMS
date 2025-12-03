from fastapi import APIRouter, Depends,status,BackgroundTasks
from .schemas import UserCreateModel,UserModel,UserLoginModel,UserBooksModel,EmailModel,PasswordResetRequestModel,PasswordResetConfirmModel
from .service import UserService    
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession   
from fastapi.exceptions import HTTPException
from .utils import create_access_token,decode_token,generate_password_hash,verify_password,create_url_safe_token,decode_url_safe_token
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime
from .dependencies import RefreshTokenBearer,AccessTokenBearer,get_current_user,RoleChecker
from src.mail import mail,create_message
from src.config import Config
from src.db.main import get_session

from src.errors import(
    UserAlreadyExists,
    InvalidCredentials,
    InvalidToken,
    UserNotFound

)


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY = 2



@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>We are pleased to welcome you to GIANTMIND SOLUTIONS PRIVATE LIMITED.</h1>"
    subject = "Welcome To you"

    message= create_message(recipients=emails,subject="Welcome!!",body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}

########### User Signup Route ###########
@auth_router.post("/signup",status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    
    user_exists = await user_service.user_exists(email,session)

    if user_exists:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user( user_data, session)

    token= create_url_safe_token({"email": email})
    link= f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message= f"""
    <h1> Verify your Email </h1>
    <p>Welcome to GIANTMIND SOLUTIONS PRIVATE LIMITED.</p>
    <p>Your user account has been successfully created in our system.</p>
    <p> Please click this <a href= "{link}">link</a> to verify your email </p>
    <p>If you did not request this account or believe this message was sent in error,</p> 
    <p>please contact the admin team immediately.</p>
    """

    message= create_message(recipients=[email],subject="Verify Your Email.",body=html_message)
    ##await mail.send_message(message)
    bg_tasks.add_task(mail.send_message,message)
    return {
        "message": "Account Created! Check email to verify your account ",
        "user": new_user
    
    }

@auth_router.get('/verify/{token}')
async def verify_user_account(token: str,session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email= token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(content= {
            "message": "Account verified successfully",

        }, status_code= status.HTTP_200_OK)
    
    return JSONResponse(content= {
        "message": "Error occured during verification"
    }, status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)




########### User Login Route ###########
@auth_router.post("/login")
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid= verify_password(password, user.password_hash)

        if password_valid:
            access_token= create_access_token(user_data= {'email': user.email,'user_uid': str(user.uid),"role": user.role})
            
            refresh_token= create_access_token(user_data= {'email': user.email,'user_uid': str(user.uid)},refresh= True,expiry= timedelta (days= REFRESH_TOKEN_EXPIRY))
            
            return JSONResponse(
                content = {
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)                        
                         
                    }           
                
                }
            )
        
    raise InvalidCredentials()


#############Get New Access Token Route #############
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data = token_details['user']
        )

        return JSONResponse(content={
            "access_token": new_access_token
        })
        
    
    raise InvalidToken()

#############Current User Route #############
@auth_router.get("/me",response_model= UserBooksModel)
async def get_current_user(user = Depends(get_current_user),_:bool=Depends( role_checker)):
    return user

####Password Reset Request ####################
@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>We received a request to reset the password associated with your account.</p>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    <If you did not request this reset, please ignore this message. Your account will remain secure. </p>
    """
    subject = "Reset Your Password"
    message = create_message(recipients= [email],subject= "Reset your password", body= html_message)
    await mail.send_message(message)
    #mail.send_message(html_message)
    #send_email.delay([email], subject, html_message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


##############
@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str,passwords: PasswordResetConfirmModel,session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},status_code=status.HTTP_200_OK)

    return JSONResponse(content={"message": "Error occured during password reset."},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
