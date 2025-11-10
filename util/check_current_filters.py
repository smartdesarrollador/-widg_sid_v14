"""
Script para verificar el estado actual de filtros en paneles anclados
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DBManager
from src.core.pinned_panels_manager import PinnedPanelsManager
import json

db = DBManager()
manager = PinnedPanelsManager(db)

print("=" * 80)
print("ESTADO ACTUAL DE PANELES ANCLADOS")
print("=" * 80)

panels = db.get_pinned_panels(active_only=True)

for panel in panels:
    print(f"\nPanel ID: {panel['id']}")
    print(f"  Categoria: {panel['category_id']}")
    print(f"  Nombre: {panel.get('custom_name', '(sin nombre)')}")
    print(f"  Shortcut: {panel.get('keyboard_shortcut', '(ninguno)')}")

    filter_config = panel.get('filter_config')
    print(f"  Filter Config: ", end="")

    if not filter_config:
        print("[VACIO] NULL")
    else:
        print(f"[EXISTE] {len(filter_config)} chars")
        try:
            filters = json.loads(filter_config)
            print(f"\n  Filtros guardados:")
            print(f"    - Advanced Filters: {filters.get('advanced_filters', {})}")
            print(f"    - State Filter: {filters.get('state_filter', 'normal')}")
            print(f"    - Search Text: '{filters.get('search_text', '')}'")
        except:
            print("    [ERROR] No se pudo parsear JSON")

db.close()

print("\n" + "=" * 80)
print("\nSi filter_config esta NULL/VACIO, significa que:")
print("  1. El panel fue anclado ANTES del fix")
print("  2. O los filtros nunca se aplicaron DESPUES de anclar")
print("\nPrueba:")
print("  1. Aplica filtros al panel YA ANCLADO")
print("  2. Espera 2 segundos (auto-guardado)")
print("  3. Ejecuta este script de nuevo")
print("=" * 80)
