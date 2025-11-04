from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/{project_id}", response_model=List[schemas.EntityResponse])
def list_entities(
    project_id: int,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Fixed query with explicit select_from and join conditions
    query = db.query(
        models.Entity,
        func.count(models.EntityMention.id).label('mention_count'),
        func.min(models.Chapter.chapter_number).label('first_appearance'),
        func.max(models.Chapter.chapter_number).label('last_appearance')
    ).select_from(models.Entity).outerjoin(
        models.EntityMention,
        models.Entity.id == models.EntityMention.entity_id
    ).outerjoin(
        models.Chapter,
        models.EntityMention.chapter_id == models.Chapter.id
    ).filter(models.Entity.project_id == project_id)
    
    if entity_type:
        query = query.filter(models.Entity.entity_type == entity_type)
    
    results = query.group_by(models.Entity.id).all()
    
    return [
        {
            **entity.__dict__,
            'mention_count': count or 0,
            'first_appearance': first,
            'last_appearance': last
        }
        for entity, count, first, last in results
    ]

@router.get("/{entity_id}/mentions")
def get_entity_mentions(entity_id: int, db: Session = Depends(get_db)):
    mentions = db.query(models.EntityMention).join(
        models.Chapter,
        models.EntityMention.chapter_id == models.Chapter.id
    ).filter(
        models.EntityMention.entity_id == entity_id
    ).order_by(asc(models.Chapter.chapter_number)).all()
    
    return [
        {
            "chapter_id": m.chapter_id,
            "chapter_number": m.chapter.chapter_number,
            "chapter_title": m.chapter.title,
            "context": m.context,
            "mentioned_as": m.mentioned_as,
            "position": m.start_pos
        }
        for m in mentions
    ]

@router.put("/{entity_id}", response_model=schemas.EntityResponse)
def update_entity(
    entity_id: int,
    entity: schemas.EntityUpdate,
    db: Session = Depends(get_db)
):
    db_entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    for key, value in entity.model_dump(exclude_unset=True).items():
        setattr(db_entity, key, value)
    
    db.commit()
    db.refresh(db_entity)
    
    # Get mention count
    mention_count = db.query(func.count(models.EntityMention.id)).filter(
        models.EntityMention.entity_id == entity_id
    ).scalar() or 0
    
    return {**db_entity.__dict__, 'mention_count': mention_count}

@router.delete("/{entity_id}")
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    db.delete(entity)
    db.commit()
    return {"message": "Entity deleted"}