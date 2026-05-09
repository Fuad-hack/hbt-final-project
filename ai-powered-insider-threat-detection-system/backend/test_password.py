"""
Test password verification
"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash

async def test_password():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        user = result.scalar_one_or_none()
        
        if user:
            print(f'User found: {user.username}')
            print(f'Password hash: {user.password_hash[:50]}...')
            print(f'Hash type: {user.password_hash.split("$")[0] if "$" in user.password_hash else "unknown"}')
            
            # Test password verification
            test_pass = 'admin123'
            is_valid = check_password_hash(user.password_hash, test_pass)
            print(f'Password valid: {is_valid}')
            
            # If not valid, regenerate
            if not is_valid:
                print('\n⚠️ Password invalid! Regenerating...')
                new_hash = generate_password_hash(test_pass)
                user.password_hash = new_hash
                await session.commit()
                print('✅ New password hash saved!')
                
                # Verify again
                is_valid2 = check_password_hash(new_hash, test_pass)
                print(f'New password valid: {is_valid2}')
        else:
            print('❌ User not found!')
            print('\nCreating admin user...')
            from create_admin import create_admin
            await create_admin()

if __name__ == "__main__":
    asyncio.run(test_password())
