import sys
sys.path.insert(0, 'E:/Projects/novel-ner-app/backend')

from app.services.ner_service import process_chapter_ner

# Use chapter 3 which exists
chapter_id = 3

print(f"Testing NER processing for chapter {chapter_id}...")
try:
    process_chapter_ner(chapter_id, 'en')
    print("✓ NER processing completed successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()