import spacy
from sqlalchemy.orm import Session
from .. import models
from ..database import SessionLocal
import sys

nlp_en = None

def get_nlp():
    global nlp_en
    if nlp_en is None:
        print("🔄 Loading spaCy model...", flush=True)
        try:
            nlp_en = spacy.load("en_core_web_trf")
            print("✓ Loaded en_core_web_trf model", flush=True)
        except Exception as e:
            print(f"⚠ Could not load en_core_web_trf: {e}", flush=True)
            try:
                nlp_en = spacy.load("en_core_web_sm")
                print("✓ Loaded en_core_web_sm model", flush=True)
            except Exception as e2:
                print(f"✗ Failed to load spaCy model: {e2}", flush=True)
                raise
    return nlp_en

def process_chapter_ner(chapter_id: int, language: str):
    """Extract entities from chapter and create Entity + EntityMention records"""
    print(f"\n{'='*60}", flush=True)
    print(f"🚀 NER BACKGROUND TASK STARTED for Chapter {chapter_id}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    # Create a NEW database session for the background task
    db = SessionLocal()
    
    try:
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if not chapter:
            print(f"✗ Chapter {chapter_id} not found in database", flush=True)
            return
        
        print(f"✓ Found chapter: {chapter.title or 'Untitled'}", flush=True)
        print(f"   Project ID: {chapter.project_id}", flush=True)
        print(f"   Content length: {len(chapter.content)} characters", flush=True)
        print(f"   Content preview: {chapter.content[:100]}...", flush=True)
        
        # Clear existing mentions for this chapter
        deleted_count = db.query(models.EntityMention).filter(
            models.EntityMention.chapter_id == chapter_id
        ).delete()
        db.commit()
        print(f"✓ Cleared {deleted_count} existing mentions", flush=True)
        
        print("🔍 Loading NLP model...", flush=True)
        nlp = get_nlp()
        print("✓ NLP model loaded, processing text...", flush=True)
        
        doc = nlp(chapter.content)
        print(f"✓ Text processed, found {len(doc.ents)} raw entities", flush=True)
        
        # Entity type mapping
        type_mapping = {
            'PERSON': 'character',
            'GPE': 'location',  # Geopolitical entity
            'LOC': 'location',
            'ORG': 'organization',
            'FAC': 'location',  # Facility
            'PRODUCT': 'item',
            'EVENT': 'concept',
            'WORK_OF_ART': 'concept',
            'NORP': 'concept',  # Nationalities, religious/political groups
        }
        
        entities_found = 0
        mentions_created = 0
        skipped_entities = []
        
        for ent in doc.ents:
            print(f"   Processing: '{ent.text}' (type: {ent.label_})", flush=True)
            entity_type = type_mapping.get(ent.label_, None)
            
            # Skip if not a relevant entity type
            if not entity_type:
                skipped_entities.append(f"{ent.text} ({ent.label_})")
                continue
            
            entities_found += 1
            
            # Check if entity already exists (case-insensitive)
            existing_entity = db.query(models.Entity).filter(
                models.Entity.project_id == chapter.project_id,
                models.Entity.name.ilike(ent.text)
            ).first()
            
            if not existing_entity:
                existing_entity = models.Entity(
                    project_id=chapter.project_id,
                    name=ent.text,
                    entity_type=entity_type
                )
                db.add(existing_entity)
                db.commit()
                db.refresh(existing_entity)
                print(f"      ✓ Created new entity: {ent.text} ({entity_type})", flush=True)
            else:
                print(f"      ↻ Using existing entity: {ent.text} ({entity_type})", flush=True)
            
            # Create mention with context
            context_start = max(0, ent.start_char - 50)
            context_end = min(len(chapter.content), ent.end_char + 50)
            context = chapter.content[context_start:context_end]
            
            mention = models.EntityMention(
                entity_id=existing_entity.id,
                chapter_id=chapter.id,
                start_pos=ent.start_char,
                end_pos=ent.end_char,
                context=context,
                mentioned_as=ent.text
            )
            db.add(mention)
            mentions_created += 1
        
        db.commit()
        
        print(f"\n{'='*60}", flush=True)
        print(f"✅ NER COMPLETE", flush=True)
        print(f"   Entities found: {entities_found}", flush=True)
        print(f"   Mentions created: {mentions_created}", flush=True)
        if skipped_entities:
            print(f"   Skipped entities: {', '.join(skipped_entities[:5])}", flush=True)
        print(f"{'='*60}\n", flush=True)
        
    except Exception as e:
        print(f"\n{'='*60}", flush=True)
        print(f"❌ ERROR IN NER PROCESSING", flush=True)
        print(f"   Error: {e}", flush=True)
        print(f"{'='*60}\n", flush=True)
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()