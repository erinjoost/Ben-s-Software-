#!/usr/bin/env python3
"""
Ben's Accessible Menu System - Main Entry Point

A comprehensive accessibility application featuring:
- Cross-platform window management
- Speech synthesis and audio feedback
- Entertainment content management
- Communication assistance
- System controls and settings
- Games library

© 2025 NARBE House – Licensed under CC BY-NC 4.0
"""

from core.app import App


def main():
    """Main entry point for the Accessible Menu System."""
    print("Starting Ben's Accessible Menu System...")
    
    try:
        app = App()
        print("✅ Application initialized successfully!")
        app.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()