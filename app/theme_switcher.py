#!/usr/bin/env python3
"""
Theme Switcher Utility for Report App
Allows easy switching between light and dark modes
"""

import argparse
import sys
from config_manager import ConfigManager

def main():
    parser = argparse.ArgumentParser(description='Switch between light and dark themes')
    parser.add_argument('mode', choices=['light', 'dark', 'miv'], 
                       help='Theme mode to switch to')
    parser.add_argument('--config-dir', '-c', 
                       help='Path to .streamlit config directory')
    
    args = parser.parse_args()
    
    # Initialize config manager
    config_manager = ConfigManager(args.config_dir)
    
    # Determine settings based on mode
    if args.mode == 'dark':
        template_enabled = True
        dark_mode = True
        print("Switching to Dark Mode...")
    elif args.mode == 'light':
        template_enabled = True
        dark_mode = False
        print("Switching to Light Mode (MIV)...")
    elif args.mode == 'miv':
        template_enabled = True
        dark_mode = False
        print("Switching to MIV Framework (Light)...")
    
    # Switch configuration
    success, config_type = config_manager.switch_config(template_enabled, dark_mode)
    
    if success:
        print(f"✅ Successfully switched to: {config_type}")
        print("🔄 Restart your Streamlit app to see the changes")
    else:
        print(f"❌ Failed to switch theme: {config_type}")
        sys.exit(1)

if __name__ == "__main__":
    main()
