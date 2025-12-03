from src.db.models import Student
from .schemas import StudentCreateModel
from src.auth.utils import generate_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

class StudentService:
    async def get_student_by_email(self, email: str, session: AsyncSession):
        statement =  select(Student).where(Student.email == email)
        result = await session.exec(statement)
        student = result.first()
        return student
    
    async def student_exists(self, email, session: AsyncSession):
        student = await self.get_student_by_email(email, session)

        return True if student is not None else False
    
      
    async def create_student(self, student_data:StudentCreateModel, user_uid: str, session:AsyncSession):
        student_data_dict= student_data.model_dump()
        new_student= Student(**student_data_dict)
        new_student.password_hash = generate_password_hash(student_data_dict['password'])
        new_student.user_uid= user_uid
        new_student.role= 'student'
        session.add(new_student)
        await session.commit()
       # await session.refresh(new_student)
        return new_student

    
    
    async def update_student(self, student: Student, student_data: dict, session: AsyncSession):
        for k,v in student_data.items():
            setattr(student, k,v)
        await session.commit()
        return student