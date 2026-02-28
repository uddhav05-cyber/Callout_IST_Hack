"""
View Architecture Diagrams
Opens all generated diagrams in your default image viewer
"""

import os
import sys
from pathlib import Path

def view_diagrams():
    """Open all diagram PNG files"""
    
    # Get the diagrams directory
    diagrams_dir = Path(__file__).parent
    
    # Find all PNG files
    png_files = sorted(diagrams_dir.glob("*.png"))
    
    if not png_files:
        print("❌ No diagram files found!")
        print("Run 'python generate_architecture.py' first to generate diagrams.")
        return
    
    print("📊 Found {} diagrams:".format(len(png_files)))
    print()
    
    for i, png_file in enumerate(png_files, 1):
        file_size = png_file.stat().st_size / 1024  # KB
        print(f"  {i}. {png_file.name} ({file_size:.1f} KB)")
    
    print()
    print("Opening diagrams in your default image viewer...")
    print()
    
    # Open each diagram
    for png_file in png_files:
        try:
            # Use the appropriate command based on OS
            if sys.platform == "win32":
                os.startfile(str(png_file))
            elif sys.platform == "darwin":  # macOS
                os.system(f"open '{png_file}'")
            else:  # Linux
                os.system(f"xdg-open '{png_file}'")
            
            print(f"✓ Opened: {png_file.name}")
        
        except Exception as e:
            print(f"❌ Error opening {png_file.name}: {e}")
    
    print()
    print("✓ All diagrams opened!")
    print()
    print("Diagram descriptions:")
    print("  1. System Overview - High-level architecture")
    print("  2. Verification Pipeline - 7-stage process")
    print("  3. Self-Hosted Architecture - Cost savings")
    print("  4. Multilingual Pipeline - 19 languages")
    print("  5. Deployment Architecture - Production setup")
    print("  6. Data Flow - Concrete example")

if __name__ == "__main__":
    view_diagrams()
