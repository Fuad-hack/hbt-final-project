"""
Show all tables in PostgreSQL
"""
import asyncio
from sqlalchemy import text
from app.database import engine
from app.config import settings

async def show_all():
    """Show tables in all schemas"""
    async with engine.begin() as conn:
        # All schemas
        print("📁 SCHEMAS:")
        result = await conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name"
        ))
        schemas = result.fetchall()
        for s in schemas:
            print(f"  📂 {s[0]}")
        
        print(f"\n🔍 Looking for tables in: {settings.DATABASE_SCHEMA}")
        
        # Tables in threat_detection
        result = await conn.execute(
            text("""SELECT table_name, table_type
               FROM information_schema.tables 
               WHERE table_schema = :schema
               ORDER BY table_name""")
            .bindparams(schema=settings.DATABASE_SCHEMA)
        )
        tables = result.fetchall()
        
        if tables:
            print(f"\n✅ FOUND {len(tables)} TABLES:")
            for t in tables:
                print(f"   📋 {t[0]} ({t[1]})")
        else:
            print("\n❌ NO TABLES FOUND!")
        
        # Also check public schema
        print("\n📋 Tables in 'public' schema:")
        result = await conn.execute(
            text("""SELECT table_name 
               FROM information_schema.tables 
               WHERE table_schema = 'public'
               ORDER BY table_name""")
        )
        public_tables = result.fetchall()
        if public_tables:
            for t in public_tables:
                print(f"   📋 {t[0]}")
        else:
            print("   (empty)")
        
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(show_all())
