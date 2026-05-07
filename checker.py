#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sites.wss2 import check_and_notify as check_wss2
from sites.mikrus import check_and_notify as check_mikrus

if __name__ == "__main__":
    print("=" * 50)
    print("Sprawdzanie zmian...")
    check_wss2()
    check_mikrus()
    print("Gotowe.")