"""
Debug login process
"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.user import User
from werkzeug.security import check_password_hash

async def debug_login():
    """Mimic the login function exactly"""
    username = 'admin'
    password = 'admin123'
    
    print(f'Login attempt: {username}')
    
    async with AsyncSessionLocal() as session:
        # Step 1: Get user (like login function)
        result = await session.execute(
            select(User).where(User.username == username.lower())
        )
        user = result.scalar_one_or_none()
        
        print(f'User found: {user is not None}')
        
        if user:
            print(f'Username: {user.username}')
            print(f'Password hash: {user.password_hash[:30]}...')
            
            # Step 2: Check password
            is_valid = check_password_hash(user.password_hash, password)
            print(f'Password check: {is_valid}')
            
            if not is_valid:
                print('\n⚠️ Password mismatch!')
                # Debug: Try to understand why
                print(f'Input password: {password}')
                print(f'Stored hash: {user.password_hash}')
        else:
            print('❌ User not found in database!')

if __name__ == "__main__":
    asyncio.run(debug_login())
