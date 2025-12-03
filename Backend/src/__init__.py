from fastapi import FastAPI,status
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.students.routes import student_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware

# @asynccontextmanager
# async def life_span(app: FastAPI):
#     # Startup code
#     print(f"Server is Starting up...")
#     from src.db.models import Book
#     await init_db()
#     yield
#     # Shutdown code
#     print(f"Server has been Stopped.")

version = 'v1'

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version= version,
  
)

register_all_errors(app)
register_middleware(app)


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])
app.include_router(student_router, prefix=f"/api/{version}/student", tags=['student'])
app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=['reviews'])