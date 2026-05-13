#!/usr/bin/env python3
"""Simple test to verify App.py loads without model being initialized"""

import sys

print("[TEST] Starting quick validation...")

try:
    print("[TEST] Creating Flask app context...")
    from App import app, SYSTEM, optimizer
    print(f"✅ App loaded (System prompt: {len(SYSTEM)} chars)")
    print(f"✅ Optimizer ready")
    print(f"✅ Flask app: {app}")
    print("\n[SUCCESS] App is ready! Model will load on first chat request.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
