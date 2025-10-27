"""Quick test to verify auth-service config loads correctly"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.config import settings
    
    print("✓ Config loaded successfully!")
    print(f"  Database: {settings.database_url[:40]}...")
    print(f"  JWT Secret: {settings.jwt_secret_key[:30]}...")
    print(f"  CORS Origins: {settings.allowed_origins}")
    print(f"  Service Port: {settings.service_port}")
    print()
    print("✓ Ready to start service!")
    
except Exception as e:
    print(f"✗ Error loading config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
