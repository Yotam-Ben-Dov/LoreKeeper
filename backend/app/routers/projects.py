from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # project is Pydantic schema - use model_dump()
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # db_project is SQLAlchemy model - use __dict__
    return {**db_project.__dict__, 'chapter_count': 0}

@router.get("/", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(
        models.Project,
        func.count(models.Chapter.id).label('chapter_count')
    ).outerjoin(models.Chapter).group_by(models.Project.id).all()
    
    # project is SQLAlchemy model - use __dict__
    return [
        {**project.__dict__, 'chapter_count': count}
        for project, count in projects
    ]

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    result = db.query(
        models.Project,
        func.count(models.Chapter.id).label('chapter_count')
    ).outerjoin(models.Chapter).filter(
        models.Project.id == project_id
    ).group_by(models.Project.id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # project is SQLAlchemy model - use __dict__
    project, count = result
    return {**project.__dict__, 'chapter_count': count}

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}