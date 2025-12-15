from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CourseCreateModel,CourseUpdateModel
from sqlmodel import select,desc
from src.db.models import Course
from datetime import datetime,date



class CourseService:
    ## GET ALL COURSE DETAILS################
    async def get_all_courses(self, session:AsyncSession):
        statement= select(Course).order_by(desc(Course.created_at))
        result= await session.exec(statement)
        return result.all()
    
    ## GET COURSE BY COURSE ID ##################
    async def get_course_by_id(self,course_uid:str, session:AsyncSession):
        statement= select(Course).where(Course.uid == course_uid)
        result= await session.exec(statement)
        course = result.first()

        return course if course is not None else None
    
    ## CREATE COURSE DETAILS###############
    async def create_course(self, course_data:CourseCreateModel, user_uid: str, session:AsyncSession):
        course_data_dict= course_data.model_dump()
        new_course= Course(**course_data_dict)
        new_course.user_uid= user_uid
        session.add(new_course)
        await session.commit()
        return new_course

    ## UPDATE THE COURSE DETAILS#############33
    async def update_course(self, course_uid:str, update_data:CourseUpdateModel, session:AsyncSession):
        course_to_update= await self.get_course_by_id(course_uid,session)

        if course_to_update is not None:
            
            update_data_dict=update_data.model_dump()

            for k,v in update_data_dict.items():  
                setattr(course_to_update,k,v)
            await session.commit()
            return course_to_update
        else:
            return None


    ## DELETE THE COURSE####################
    async def delete_course(self, course_uid:str, session:AsyncSession) -> bool:
        course_to_delete= await self.get_course_by_id(course_uid,session)
        
        if course_to_delete is None:
            return False  # not found

        await session.delete(course_to_delete)
        await session.commit()
        return True

 