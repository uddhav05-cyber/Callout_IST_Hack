"""
Interactive Diagram Viewer
Select and view specific diagrams
"""

import os
import sys
from pathlib import Path

def show_menu():
    """Display menu of available diagrams"""
    print()
    print("=" * 60)
    print("  CALLOUT ARCHITECTURE DIAGRAMS")
    print("=" * 60)
    print()
    print("Available diagrams:")
    print()
    print("  1. System Overview")
    print("     → High-level architecture with all components")
    print()
    print("  2. Verification Pipeline")
    print("     → Detailed 7-stage verification process")
    print()
    print("  3. Self-Hosted API Architecture")
    print("     → Self-hosted vs external API routing")
    print()
    print("  4. Multilingual Pipeline")
    print("     → 19 languages with native processing")
    print()
    print("  5. Deployment Architecture")
    print("     → Production-ready deployment setup")
    print()
    print("  6. Data Flow Example")
    print("     → Concrete example with real data")
    print()
    print("  A. View ALL diagrams")
    print("  Q. Quit")
    print()
    print("=" * 60)

def open_diagram(diagram_path):
    """Open a diagram in the default viewer"""
    try:
        if sys.platform == "win32":
            os.startfile(str(diagram_path))
        elif sys.platform == "darwin":  # macOS
            os.system(f"open '{diagram_path}'")
        else:  # Linux
            os.system(f"xdg-open '{diagram_path}'")
        
        print(f"✓ Opened: {diagram_path.name}")
        return True
    
    except Exception as e:
        print(f"❌ Error opening diagram: {e}")
        return False

def main():
    """Main interactive loop"""
    
    # Get the diagrams directory
    diagrams_dir = Path(__file__).parent
    
    # Map choices to files
    diagram_files = {
        '1': '01_system_overview.png',
        '2': '02_verification_pipeline.png',
        '3': '03_self_hosted_architecture.png',
        '4': '04_multilingual_pipeline.png',
        '5': '05_deployment_architecture.png',
        '6': '06_data_flow.png'
    }
    
    while True:
        show_menu()
        
        choice = input("Select a diagram (1-6, A, Q): ").strip().upper()
        
        if choice == 'Q':
            print()
            print("👋 Goodbye!")
            print()
            break
        
        elif choice == 'A':
            print()
            print("Opening all diagrams...")
            print()
            for file_name in diagram_files.values():
                diagram_path = diagrams_dir / file_name
                if diagram_path.exists():
                    open_diagram(diagram_path)
                else:
                    print(f"❌ File not found: {file_name}")
            print()
            input("Press Enter to continue...")
        
        elif choice in diagram_files:
            file_name = diagram_files[choice]
            diagram_path = diagrams_dir / file_name
            
            if diagram_path.exists():
                print()
                print(f"Opening: {file_name}")
                print()
                open_diagram(diagram_path)
                print()
                input("Press Enter to continue...")
            else:
                print()
                print(f"❌ File not found: {file_name}")
                print("Run 'python generate_architecture.py' to generate diagrams.")
                print()
                input("Press Enter to continue...")
        
        else:
            print()
            print("❌ Invalid choice. Please select 1-6, A, or Q.")
            print()
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("👋 Goodbye!")
        print()
