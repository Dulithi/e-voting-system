"""
Create a test voting code for development/testing
"""
import psycopg
import sys
import uuid
from datetime import datetime

# Database connection
DB_CONFIG = {
    "dbname": "evoting_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def create_test_voting_code(election_id: str):
    """Create a test voting code for an election"""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Generate test codes
        main_code = "TEST-MAIN-12345"
        confirmation_code = "TEST-CONF-67890"
        
        # Check if election exists
        cur.execute(
            "SELECT election_id FROM elections WHERE election_id::text = %s",
            (election_id,)
        )
        if not cur.fetchone():
            print(f"❌ Election {election_id} not found!")
            return False
        
        # Check if code already exists
        cur.execute(
            "SELECT code_id FROM voting_codes WHERE main_voting_code = %s",
            (main_code,)
        )
        if cur.fetchone():
            print(f"✅ Test voting code already exists: {main_code}")
            return True
        
        # Insert test voting code
        cur.execute("""
            INSERT INTO voting_codes 
            (election_id, main_voting_code, confirmation_code, issued_at)
            VALUES (%s::uuid, %s, %s, %s)
            RETURNING code_id
        """, (election_id, main_code, confirmation_code, datetime.utcnow()))
        
        code_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Test voting code created successfully!")
        print(f"   Code ID: {code_id}")
        print(f"   Election ID: {election_id}")
        print(f"   Main Code: {main_code}")
        print(f"   Confirmation Code: {confirmation_code}")
        print(f"\n💡 Use this main code in the mobile app for testing")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating test voting code: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_test_voting_code.py <election_id>")
        print("\nTo find elections:")
        print("  psql -U postgres -d evoting_db -c \"SELECT election_id, title FROM elections;\"")
        sys.exit(1)
    
    election_id = sys.argv[1]
    create_test_voting_code(election_id)
