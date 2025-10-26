#!/usr/bin/env python3
"""
Quick launcher for the Interactive SuperOps IT Technician Agent
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from src.interactive_agent import main
    main()