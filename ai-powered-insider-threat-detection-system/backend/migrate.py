"""
Database Migration Script
Creates all tables from SQLAlchemy ORM models
"""
import asyncio
from app.database import engine, init_db

async def migrate():
    """Run database migration"""
    print("🔄 Starting database migration...")
    print(f"   Creating schema and tables...")
    
    try:
        await init_db()
        print("✅ Migration completed successfully!")
        print("\n📊 Created tables:")
        
        # List created tables
        from sqlalchemy import text
        from app.config import settings
        
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""SELECT table_name 
                   FROM information_schema.tables 
                   WHERE table_schema = :schema
                   ORDER BY table_name""")
                .bindparams(schema=settings.DATABASE_SCHEMA)
            )
            tables = result.fetchall()
            for table in tables:
                print(f"   ✓ {table[0]}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
