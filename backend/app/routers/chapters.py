from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..services.ner_service import process_chapter_ner

router = APIRouter()

@router.post("/{project_id}", response_model=schemas.ChapterResponse)
def create_chapter(
    project_id: int,
    chapter: schemas.ChapterCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    print(f"\n📝 Creating new chapter in project {project_id}", flush=True)
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    word_count = len(chapter.content.split())
    print(f"   Word count: {word_count}", flush=True)
    
    db_chapter = models.Chapter(
        **chapter.model_dump(),
        project_id=project_id,
        word_count=word_count
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    
    print(f"✓ Chapter created with ID: {db_chapter.id}", flush=True)
    print(f"⏰ Scheduling NER background task...", flush=True)
    
    # Run NER in background (English)
    background_tasks.add_task(process_chapter_ner, db_chapter.id, 'en')
    
    print(f"✓ Background task scheduled", flush=True)
    
    return db_chapter

@router.get("/{project_id}", response_model=List[schemas.ChapterResponse])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Chapter).filter(
        models.Chapter.project_id == project_id
    ).order_by(models.Chapter.chapter_number).all()

@router.get("/single/{chapter_id}", response_model=schemas.ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@router.put("/{chapter_id}", response_model=schemas.ChapterResponse)
def update_chapter(
    chapter_id: int,
    chapter: schemas.ChapterUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    print(f"\n📝 Updating chapter {chapter_id}", flush=True)
    
    db_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    update_data = chapter.model_dump(exclude_unset=True)
    
    # Recalculate word count if content changed
    if 'content' in update_data:
        update_data['word_count'] = len(update_data['content'].split())
        print(f"   Content changed, new word count: {update_data['word_count']}", flush=True)
        print(f"⏰ Scheduling NER background task...", flush=True)
        # Re-run NER if content changed
        background_tasks.add_task(process_chapter_ner, chapter_id, 'en')
        print(f"✓ Background task scheduled", flush=True)
    
    for key, value in update_data.items():
        setattr(db_chapter, key, value)
    
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@router.delete("/{chapter_id}")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(chapter)
    db.commit()
    return {"message": "Chapter deleted"}