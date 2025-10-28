#!/usr/bin/env python3
"""Test threshold crypto import"""
import sys
from pathlib import Path

# Add backend directory to path (same as main.py does)
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("Testing threshold crypto import...")
print(f"Backend dir: {backend_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    from shared.threshold_crypto import (
        ThresholdCrypto, 
        generate_election_keypair_with_trustees,
        generate_trustee_keypair
    )
    print("✅ SUCCESS! ThresholdCrypto imported successfully")
    print(f"   ThresholdCrypto: {ThresholdCrypto}")
    print(f"   generate_election_keypair_with_trustees: {generate_election_keypair_with_trustees}")
except ImportError as e:
    print(f"❌ FAILED! Import error: {e}")
    import traceback
    traceback.print_exc()
