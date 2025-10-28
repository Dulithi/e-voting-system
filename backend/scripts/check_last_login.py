"""
Check last_login_at values in database
"""
import sys
sys.path.insert(0, '..')

from shared.database import engine
from sqlalchemy import text

print("\n" + "="*70)
print("📊 CHECKING last_login_at VALUES IN DATABASE")
print("="*70 + "\n")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT email, last_login_at, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """))
    
    print(f"{'Email':<35} {'Last Login':<30} {'Registered':<20}")
    print("-" * 85)
    
    for row in result:
        email = row[0]
        last_login = row[1] if row[1] else "Never"
        created = row[2]
        print(f"{email:<35} {str(last_login):<30} {str(created):<20}")

print("\n" + "="*70)
print("✅ Query complete")
print("="*70 + "\n")
