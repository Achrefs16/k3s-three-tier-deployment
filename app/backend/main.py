from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
from contextlib import asynccontextmanager

# Database connection pool
pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    # Startup: Create database pool
    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        database=os.getenv("DB_NAME", "studentdb")
    )
    
    # Create table if not exists
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                grade VARCHAR(10)
            )
        ''')
    
    yield
    
    # Shutdown: Close database pool
    await pool.close()

app = FastAPI(title="Student Management API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: int
    grade: str

class StudentCreate(BaseModel):
    name: str
    email: str
    age: int
    grade: str

@app.get("/")
async def root():
    return {"message": "Student Management API"}

@app.get("/api/students", response_model=List[Student])
async def get_students():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM students ORDER BY id")
        return [dict(row) for row in rows]

@app.get("/api/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM students WHERE id = $1", student_id)
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)

@app.post("/api/students", response_model=Student)
async def create_student(student: StudentCreate):
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """INSERT INTO students (name, email, age, grade) 
                   VALUES ($1, $2, $3, $4) RETURNING *""",
                student.name, student.email, student.age, student.grade
            )
            return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Email already exists")

@app.put("/api/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentCreate):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE students 
               SET name=$1, email=$2, age=$3, grade=$4 
               WHERE id=$5 RETURNING *""",
            student.name, student.email, student.age, student.grade, student_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM students WHERE id = $1", student_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully"}