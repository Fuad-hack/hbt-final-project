"""
Create default admin user
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from werkzeug.security import generate_password_hash

async def create_admin():
    """Create admin user"""
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("⚠️ Admin user already exists")
            return
        
        # Create admin with werkzeug password hash
        password = "admin123"
        password_hash = generate_password_hash(password)
        
        admin = User(
            username="admin",
            email="admin@itdt.com",
            password_hash=password_hash,
            full_name="System Administrator",
            role="admin"
        )
        session.add(admin)
        await session.commit()
        
        print("✅ Admin user created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@itdt.com")

if __name__ == "__main__":
    asyncio.run(create_admin())
