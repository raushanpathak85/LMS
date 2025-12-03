from fastapi import APIRouter, Depends,status
from .schemas import StudentCreateModel,StudentLoginModel,EmailModel,PasswordResetRequestModel,PasswordResetConfirmModel,StudentModel
from .service import StudentService    
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession   
from fastapi.exceptions import HTTPException
from src.auth.utils import generate_password_hash,verify_password,create_url_safe_token,decode_url_safe_token
from fastapi.responses import JSONResponse
from src.auth.dependencies import RoleChecker,AccessTokenBearer
from src.mail import mail,create_message
from src.config import Config
from src.db.main import get_session

from src.errors import(
    StudentAlreadyExists,
    InvalidCredentials,
    StudentNotFound

)

access_token_bearer = AccessTokenBearer()
student_router = APIRouter()
student_service = StudentService()
role_checker= Depends(RoleChecker(['admin','user']))

REFRESH_TOKEN_EXPIRY = 2



@student_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>We are pleased to welcome you to GIANTMIND SOLUTIONS PRIVATE LIMITED.</h1>"
    subject = "Welcome To you"

    message= create_message(recipients=emails,subject="Welcome!!",body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}

########### Student creation Route ###########
@student_router.post("/",status_code=status.HTTP_201_CREATED)
async def create_a_student(student_data: StudentCreateModel,session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    email= student_data.email
    student_exists = await student_service.student_exists(email,session)
    
    if student_exists:
        raise StudentAlreadyExists()
    
    user_uid = token_details.get('user')['user_uid']
    new_student = await student_service.create_student(student_data,user_uid, session)
    
         
    token= create_url_safe_token({"email": email})
    link= f"http://{Config.DOMAIN}/api/v1/student/verify/{token}"

    html_message= f"""
    <h1> Verify your Email </h1>
    <p>Welcome to GIANTMIND SOLUTIONS PRIVATE LIMITED.</p>
    <p>Your student account has been successfully created in our system.</p>
    <p> Please click this <a href= "{link}">link</a> to verify your email </p>
    <p>If you did not request this account or believe this message was sent in error,</p> 
    <p>please contact the admin team immediately.</p>
    """

    message= create_message(recipients=[email],subject="Verify Your Email.",body=html_message)
    await mail.send_message(message)
    
    return {
        "message": "Account Created! Check email to verify your account ",
        "student":  new_student
       
    }
### Verify the account ######
@student_router.get('/verify/{token}')
async def verify_student_account(token: str,session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    student_email= token_data.get('email')

    if student_email:
        student = await student_service.get_student_by_email(student_email,session)
        
        if not student:
            raise StudentNotFound()
        await student_service.update_student(student, {"is_verified": True}, session)

        return JSONResponse(content= {
            "message": "Account verified successfully",

        }, status_code= status.HTTP_200_OK)
    
    return JSONResponse(content= {
        "message": "Error occured during verification"
    }, status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)




########### Student Login Route ###########
@student_router.post("/login")
async def login_student(login_data: StudentLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    student = await student_service.get_student_by_email(email, session)

    if student is not None:
        password_valid= verify_password(password, student.password_hash)

        if password_valid:
                        
            return JSONResponse(
                content = {
                    "message": "Login successful",
                    "student": {
                        "email": student.email,
                        "uid": str(student.uid)                        
                         
                    }           
                
                }
            )
        
    raise InvalidCredentials()

####Password Reset Request ####################
@student_router.post("/password-reset-request")
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
@student_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str,passwords: PasswordResetConfirmModel,session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)

    token_data = decode_url_safe_token(token)
    student_email = token_data.get("email")

    if student_email:
        student = await student_service.get_student_by_email(student_email, session)

        if not student:
            raise StudentNotFound()

        passwd_hash = generate_password_hash(new_password)
        await student_service.update_student(student, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},status_code=status.HTTP_200_OK)

    return JSONResponse(content={"message": "Error occured during password reset."},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)