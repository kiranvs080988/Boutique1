"""
Setup script for the Boutique Work Orders Management System.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Boutique Work Orders Management System - Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\n⚠️  Failed to install dependencies. Please run manually:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nTo start the server:")
    print("  python run_server.py")
    print("\nAPI will be available at:")
    print("  - Documentation: http://localhost:8000/docs")
    print("  - API Base: http://localhost:8000")
    print("\nThe system will automatically create sample data for testing.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
