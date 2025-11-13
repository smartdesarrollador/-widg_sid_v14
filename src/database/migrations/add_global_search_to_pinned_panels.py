"""
Migración: Agregar soporte para paneles de búsqueda global en pinned_panels
Fecha: 2025-11-12
Versión: 1.0

Esta migración agrega columnas a la tabla pinned_panels para soportar
paneles de búsqueda global además de paneles de categorías.

Columnas agregadas:
- panel_type: 'category' o 'global_search'
- search_query: Texto de búsqueda para paneles global_search
- advanced_filters: Filtros avanzados serializados en JSON
- state_filter: Filtro de estado ('normal', 'archived', 'inactive', 'all')
- filter_config: Configuración general de filtros en JSON
- keyboard_shortcut: Atajo de teclado como 'Ctrl+Shift+1'
"""


def upgrade(conn):
    """Agregar columnas para soporte de búsqueda global"""
    print("[*] Agregando columnas a pinned_panels para búsqueda global...")

    # Verificar qué columnas ya existen
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(pinned_panels)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Define columns to add
    columns_to_add = {
        'panel_type': "TEXT DEFAULT 'category'",
        'search_query': "TEXT DEFAULT NULL",
        'advanced_filters': "TEXT DEFAULT NULL",
        'state_filter': "TEXT DEFAULT 'normal'",
        'filter_config': "TEXT DEFAULT NULL",
        'keyboard_shortcut': "TEXT DEFAULT NULL"
    }

    added_count = 0

    # Add missing columns
    for column_name, column_def in columns_to_add.items():
        if column_name not in existing_columns:
            alter_query = f"ALTER TABLE pinned_panels ADD COLUMN {column_name} {column_def}"
            print(f"    [+] Agregando columna: {column_name}")
            conn.execute(alter_query)
            added_count += 1
        else:
            print(f"    [~] Columna ya existe: {column_name}")

    conn.commit()

    if added_count > 0:
        print(f"[OK] {added_count} columnas agregadas exitosamente")
    else:
        print("[OK] Todas las columnas ya existen")


def downgrade(conn):
    """
    Revertir migración (SQLite no soporta DROP COLUMN directamente)

    NOTA: SQLite no soporta DROP COLUMN antes de versión 3.35.0.
    Para revertir completamente, sería necesario:
    1. Crear tabla temporal sin las columnas
    2. Copiar datos
    3. Eliminar tabla original
    4. Renombrar tabla temporal

    Por simplicidad, esta migración no es reversible automáticamente.
    """
    print("[!] ADVERTENCIA: SQLite no soporta DROP COLUMN directamente")
    print("[!] La reversión de esta migración requiere intervención manual")
    print("[!] Las columnas agregadas permanecerán en la tabla")
