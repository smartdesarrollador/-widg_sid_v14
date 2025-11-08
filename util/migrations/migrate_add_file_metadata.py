"""
Migration Script: Add File Metadata Fields to Items Table
Fecha: 2025-11-08
Fase 1 - Plan de Implementación PATH Avanzado

Este script agrega campos de metadatos a la tabla 'items' para soportar
la gestión avanzada de archivos con tipo PATH.

Campos agregados:
- file_size: Tamaño del archivo en bytes
- file_type: Categoría del archivo (IMAGEN, VIDEO, PDF, etc.)
- file_extension: Extensión con punto (.jpg, .mp4, .pdf)
- original_filename: Nombre original del archivo
- file_hash: Hash SHA256 para detección de duplicados
"""

import sqlite3
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """
    Obtiene la ruta de la base de datos

    Returns:
        Path: Ruta absoluta a widget_sidebar.db
    """
    # Desde util/migrations/ subir dos niveles para llegar a raíz
    script_dir = Path(__file__).parent
    db_path = script_dir.parent.parent / "widget_sidebar.db"
    return db_path


def check_columns_exist(cursor: sqlite3.Cursor) -> dict:
    """
    Verifica qué columnas ya existen en la tabla items

    Args:
        cursor: Cursor de la base de datos

    Returns:
        dict: Diccionario con nombre de columna y si existe
    """
    cursor.execute("PRAGMA table_info(items)")
    columns = cursor.fetchall()
    existing_columns = {col[1] for col in columns}

    columns_to_add = {
        'file_size': 'file_size' in existing_columns,
        'file_type': 'file_type' in existing_columns,
        'file_extension': 'file_extension' in existing_columns,
        'original_filename': 'original_filename' in existing_columns,
        'file_hash': 'file_hash' in existing_columns
    }

    return columns_to_add


def migrate_add_file_metadata(db_path: str = None) -> bool:
    """
    Ejecuta la migración para agregar campos de metadatos de archivos

    Args:
        db_path: Ruta opcional a la base de datos

    Returns:
        bool: True si la migración fue exitosa

    Raises:
        Exception: Si ocurre un error durante la migración
    """
    # Configurar codificación UTF-8 para Windows
    import io
    import sys
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 70)
    print("MIGRACION: Agregar Campos de Metadatos de Archivos")
    print("=" * 70)

    # Obtener ruta de BD
    if db_path is None:
        db_path = get_db_path()
    else:
        db_path = Path(db_path)

    if not db_path.exists():
        logger.error(f"Base de datos no encontrada: {db_path}")
        print(f"\nERROR: Base de datos no encontrada en {db_path}")
        return False

    print(f"\nBase de datos: {db_path}")
    print(f"Tamanio actual: {db_path.stat().st_size / 1024:.2f} KB")

    try:
        # Conectar a la base de datos
        print("\n[1/4] Conectando a la base de datos...")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        print("OK - Conexion establecida")

        # Verificar columnas existentes
        print("\n[2/4] Verificando estructura actual...")
        existing_columns = check_columns_exist(cursor)

        columns_status = []
        for col_name, exists in existing_columns.items():
            status = "[OK] Ya existe" if exists else "[  ] Por agregar"
            columns_status.append(f"   - {col_name}: {status}")

        print("\n".join(columns_status))

        # Determinar qué columnas agregar
        columns_to_add = [col for col, exists in existing_columns.items() if not exists]

        if not columns_to_add:
            print("\nOK - Todas las columnas ya existen. No se requiere migracion.")
            conn.close()
            return True

        print(f"\nSe agregaran {len(columns_to_add)} columnas nuevas")

        # Agregar columnas
        print("\n[3/4] Ejecutando ALTER TABLE statements...")

        # Definición de columnas con sus tipos
        column_definitions = {
            'file_size': 'INTEGER DEFAULT NULL',
            'file_type': 'VARCHAR(50) DEFAULT NULL',
            'file_extension': 'VARCHAR(10) DEFAULT NULL',
            'original_filename': 'VARCHAR(255) DEFAULT NULL',
            'file_hash': 'VARCHAR(64) DEFAULT NULL'
        }

        for col_name in columns_to_add:
            col_def = column_definitions[col_name]
            sql = f"ALTER TABLE items ADD COLUMN {col_name} {col_def}"

            try:
                cursor.execute(sql)
                print(f"   OK - Columna agregada: {col_name}")
                logger.info(f"Column added: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   WARN - Columna ya existe: {col_name}")
                else:
                    raise

        # Commit cambios
        conn.commit()
        print("\nOK - Cambios guardados en la base de datos")

        # Verificar que las columnas se agregaron
        print("\n[4/4] Verificando migracion...")
        final_columns = check_columns_exist(cursor)

        all_exist = all(final_columns.values())

        if all_exist:
            print("OK - Todas las columnas fueron agregadas exitosamente")

            # Mostrar estructura final
            cursor.execute("PRAGMA table_info(items)")
            columns_info = cursor.fetchall()

            print("\nEstructura final de la tabla 'items':")
            print(f"{'ID':<5} {'Columna':<25} {'Tipo':<15} {'Not Null':<10} {'Default'}")
            print("-" * 70)
            for col in columns_info:
                col_id, name, type_, notnull, default, pk = col
                notnull_str = "YES" if notnull else "NO"
                default_str = str(default) if default else "-"
                print(f"{col_id:<5} {name:<25} {type_:<15} {notnull_str:<10} {default_str}")
        else:
            print("ERROR - Algunas columnas no se agregaron correctamente")
            for col_name, exists in final_columns.items():
                if not exists:
                    print(f"   FALTA: {col_name}")
            return False

        # Cerrar conexión
        conn.close()

        # Estadísticas finales
        print("\n" + "=" * 70)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\nEstadisticas:")
        print(f"   - Columnas agregadas: {len(columns_to_add)}")
        print(f"   - Tamanio final BD: {db_path.stat().st_size / 1024:.2f} KB")
        print(f"\nProximos pasos:")
        print("   1. Actualizar modelo Item en src/models/item.py")
        print("   2. Actualizar DBManager en src/database/db_manager.py")
        print("   3. Crear FileManager en src/core/file_manager.py")
        print("=" * 70)

        return True

    except sqlite3.Error as e:
        logger.error(f"Error SQLite: {e}")
        print(f"\nERROR - Error de base de datos: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"\nERROR - Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False


def show_help():
    """Muestra ayuda de uso del script"""
    help_text = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  Migration Script: Add File Metadata to Items Table              ║
    ╚═══════════════════════════════════════════════════════════════════╝

    USO:
        python migrate_add_file_metadata.py [opciones]

    OPCIONES:
        -h, --help          Mostrar esta ayuda
        --db-path PATH      Especificar ruta a la base de datos
                           (Por defecto: ../../widget_sidebar.db)

    DESCRIPCIÓN:
        Este script agrega 5 campos nuevos a la tabla 'items' para
        soportar la gestión avanzada de archivos con tipo PATH:

        • file_size          - Tamaño en bytes (INTEGER)
        • file_type          - Categoría (VARCHAR 50)
        • file_extension     - Extensión con punto (VARCHAR 10)
        • original_filename  - Nombre original (VARCHAR 255)
        • file_hash          - SHA256 hash (VARCHAR 64)

    EJEMPLOS:
        # Ejecutar migración con BD por defecto
        python migrate_add_file_metadata.py

        # Especificar ruta a BD
        python migrate_add_file_metadata.py --db-path C:\\path\\to\\db.db

    NOTA:
        Es recomendable crear un backup de la base de datos antes
        de ejecutar esta migración.
    """
    print(help_text)


if __name__ == "__main__":
    """
    Ejecutar migración cuando se ejecuta directamente
    """
    # Parsear argumentos
    db_path = None

    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            show_help()
            sys.exit(0)

        if sys.argv[1] == '--db-path' and len(sys.argv) > 2:
            db_path = sys.argv[2]

    # Ejecutar migración
    try:
        success = migrate_add_file_metadata(db_path)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nWARN - Migracion cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR - La migracion fallo: {e}")
        sys.exit(1)
