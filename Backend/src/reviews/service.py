from src.db.models import Review
from src.auth.service import UserService
from src.courses.service import CourseService
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status
from .schemas import ReviewCreateModel
import logging
from src.errors import CourseNotFound,UserNotFound

course_Service= CourseService()
user_service= UserService()

class ReviewService:

    async def add_review_to_book(self,user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            book= await course_Service.get_book(book_uid=book_uid, session=session)
            user= await user_service.get_user_by_email(email=user_email,session=session)
            review_data_dict= review_data.model_dump()
            new_review= Review(**review_data_dict)

            if not book:
                raise CourseNotFound()
            if not user:
                raise UserNotFound()

            new_review.user= user
            new_review.book=book
            session.add(new_review)
            await session.commit()
            return new_review
        

        except Exception as e:
            logging.exception(e)
            raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,detail= "Oops....Something went wrong")
        


        