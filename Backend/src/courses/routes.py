from fastapi import APIRouter,status,Depends
from .schemas import Course, CourseUpdateModel,CourseCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.courses.service import CourseService
from src.db.main import get_session
from typing import List
from src.auth.dependencies import AccessTokenBearer,RoleChecker
from src.errors import CourseNotFound

course_router = APIRouter()
course_service= CourseService()
access_token_bearer = AccessTokenBearer()
role_checker= Depends(RoleChecker(['admin','user']))



####Create A Course Route #####
@course_router.post("/", status_code=status.HTTP_201_CREATED,response_model=Course, dependencies=[role_checker])
async def create_a_course(course_data: CourseCreateModel,session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    user_id = token_details.get('user')['user_uid']
    new_course = await course_service.create_course(course_data,user_id, session)
    return new_course


####Get All courses Route #####
@course_router.get("/", response_model=List[Course], dependencies=[role_checker])
async def get_all_courses(session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    courses = await course_service.get_all_courses(session)
    return courses


#####Get particular course Route #####
@course_router.get("/course/{uid}", response_model=Course, dependencies=[role_checker])
async def get_course_id(uid: str, session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer))-> dict:
    course = await course_service.get_course_by_id(uid, session)

    if course:
        return course
    else:
        return CourseNotFound()
 

####Update A Course Route #####
@course_router.patch("/{course_uid}", response_model=Course, dependencies=[role_checker])
async def update_course(course_uid: str,course_update_data:CourseUpdateModel, session: AsyncSession = Depends(get_session), _: dict= Depends(access_token_bearer)) -> dict:
            updated_course= await course_service.update_course(course_uid,course_update_data,session)

            if updated_course:
                 return updated_course
            else:
                 raise CourseNotFound()

####Delete A Course Route #####
@course_router.delete("/{course_uid}",status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def delete_course(course_uid: str, session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer)):
    course_to_delete = await course_service.delete_course(course_uid,session)

    if not course_to_delete:
        raise CourseNotFound()

    return {"status_code=":status.HTTP_204_NO_CONTENT,"detail=":"Delete successfully"}
 



        