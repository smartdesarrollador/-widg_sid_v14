import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from core.pinned_panels_manager import PinnedPanelsManager

# Initialize DB
db = DBManager()

# Initialize PinnedPanelsManager
panels_mgr = PinnedPanelsManager(db)

# Get global search panels
print("\nCalling get_global_search_panels(active_only=True)...")
global_panels = panels_mgr.get_global_search_panels(active_only=True)

print(f"\nFound {len(global_panels)} global search panels:")
for panel in global_panels:
    print(f"  - ID: {panel['id']}, Name: {panel.get('custom_name', 'N/A')}, Type: {panel.get('panel_type', 'N/A')}")

# Also check what get_pinned_panels returns
print("\n\nCalling db.get_pinned_panels(active_only=True)...")
all_panels = db.get_pinned_panels(active_only=True)

print(f"\nFound {len(all_panels)} total panels:")
for panel in all_panels:
    print(f"  - ID: {panel['id']}, cat_id: {panel.get('category_id', 'None')}, Type: {panel.get('panel_type', 'N/A')}, Name: {panel.get('custom_name', 'N/A')}")

db.close()
