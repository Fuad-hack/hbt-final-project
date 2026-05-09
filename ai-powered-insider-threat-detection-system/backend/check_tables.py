"""
Check PostgreSQL tables
"""
import asyncio
from sqlalchemy import text
from app.database import engine
from app.config import settings

async def check_tables():
    """Check if tables exist in PostgreSQL"""
    async with engine.begin() as conn:
        # Check schema exists
        result = await conn.execute(
            text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema")
            .bindparams(schema=settings.DATABASE_SCHEMA)
        )
        schema = result.fetchone()
        print(f"Schema '{settings.DATABASE_SCHEMA}': {'EXISTS' if schema else 'NOT FOUND'}")
        
        if schema:
            # List tables in schema
            result = await conn.execute(
                text("""SELECT table_name 
                   FROM information_schema.tables 
                   WHERE table_schema = :schema
                   ORDER BY table_name""")
                .bindparams(schema=settings.DATABASE_SCHEMA)
            )
            tables = result.fetchall()
            print(f"\nTables in {settings.DATABASE_SCHEMA} schema:")
            for table in tables:
                print(f"  - {table[0]}")
            
            if not tables:
                print("  (No tables found - need to run migration)")
        
        # Close connection
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
