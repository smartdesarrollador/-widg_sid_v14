"""
Migration Script: Add Files Configuration Settings
Fecha: 2025-11-08
Fase 2 - Plan de Implementación PATH Avanzado

Este script agrega configuraciones para la gestión de archivos a la tabla 'settings'.

Settings agregados:
- files_base_path: Ruta base para almacenamiento de archivos
- files_folders_config: JSON con mapeo de tipos de archivos a carpetas
- files_auto_create_folders: Boolean para crear carpetas automáticamente
"""

import sqlite3
import json
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
    script_dir = Path(__file__).parent
    db_path = script_dir.parent.parent / "widget_sidebar.db"
    return db_path


def get_default_folders_config() -> dict:
    """
    Obtiene la configuración por defecto de carpetas

    Returns:
        dict: Diccionario con mapeo de tipos a carpetas
    """
    return {
        "VIDEOS": "VIDEOS",
        "IMAGENES": "IMAGENES",
        "PDFS": "PDFS",
        "WORDS": "WORDS",
        "EXCELS": "EXCELS",
        "TEXT": "TEXT",
        "OTROS": "OTROS"
    }


def setting_exists(cursor: sqlite3.Cursor, key: str) -> bool:
    """
    Verifica si un setting ya existe

    Args:
        cursor: Cursor de la base de datos
        key: Clave del setting

    Returns:
        bool: True si existe, False si no
    """
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
    count = cursor.fetchone()[0]
    return count > 0


def migrate_add_files_settings(db_path: str = None) -> bool:
    """
    Ejecuta la migración para agregar settings de configuración de archivos

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
    print("MIGRACION: Agregar Configuracion de Archivos a Settings")
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

        # Verificar settings existentes
        print("\n[2/4] Verificando settings actuales...")

        settings_to_add = {
            'files_base_path': '',
            'files_folders_config': json.dumps(get_default_folders_config()),
            'files_auto_create_folders': 'true'
        }

        existing_settings = {}
        for key in settings_to_add.keys():
            exists = setting_exists(cursor, key)
            existing_settings[key] = exists
            status = "[OK] Ya existe" if exists else "[  ] Por agregar"
            print(f"   - {key}: {status}")

        # Determinar qué settings agregar
        settings_to_insert = {
            k: v for k, v in settings_to_add.items()
            if not existing_settings[k]
        }

        if not settings_to_insert:
            print("\nOK - Todos los settings ya existen. No se requiere migracion.")
            conn.close()
            return True

        print(f"\nSe agregaran {len(settings_to_insert)} settings nuevos")

        # Agregar settings
        print("\n[3/4] Insertando settings...")

        for key, value in settings_to_insert.items():
            try:
                cursor.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
                print(f"   OK - Setting agregado: {key}")

                # Mostrar preview del valor
                if len(value) > 50:
                    preview = value[:47] + "..."
                else:
                    preview = value
                print(f"        Valor: {preview}")

                logger.info(f"Setting added: {key}")
            except sqlite3.IntegrityError as e:
                print(f"   WARN - Setting ya existe: {key}")
            except Exception as e:
                print(f"   ERROR - No se pudo agregar {key}: {e}")
                raise

        # Commit cambios
        conn.commit()
        print("\nOK - Cambios guardados en la base de datos")

        # Verificar que los settings se agregaron
        print("\n[4/4] Verificando migracion...")
        final_settings = {}
        for key in settings_to_add.keys():
            final_settings[key] = setting_exists(cursor, key)

        all_exist = all(final_settings.values())

        if all_exist:
            print("OK - Todos los settings fueron agregados exitosamente")

            # Mostrar settings finales
            print("\nSettings de configuracion de archivos:")
            print(f"{'Key':<30} Value")
            print("-" * 70)

            for key in settings_to_add.keys():
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                if result:
                    value = result[0]
                    if len(value) > 50:
                        display_value = value[:47] + "..."
                    else:
                        display_value = value
                    print(f"{key:<30} {display_value}")
        else:
            print("ERROR - Algunos settings no se agregaron correctamente")
            for key, exists in final_settings.items():
                if not exists:
                    print(f"   FALTA: {key}")
            return False

        # Cerrar conexión
        conn.close()

        # Estadísticas finales
        print("\n" + "=" * 70)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\nEstadisticas:")
        print(f"   - Settings agregados: {len(settings_to_insert)}")
        print(f"   - Tamanio final BD: {db_path.stat().st_size / 1024:.2f} KB")
        print(f"\nConfiguracion por defecto:")
        print(f"   - Ruta base: (vacia - usuario debe configurar)")
        print(f"   - Carpetas predefinidas: 7 tipos")
        print(f"   - Auto-crear carpetas: Activado")
        print(f"\nProximos pasos:")
        print("   1. Actualizar ConfigManager con metodos para files settings")
        print("   2. Crear pestaña 'Archivos' en SettingsWindow")
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
    ║  Migration Script: Add Files Configuration Settings              ║
    ╚═══════════════════════════════════════════════════════════════════╝

    USO:
        python migrate_add_files_settings.py [opciones]

    OPCIONES:
        -h, --help          Mostrar esta ayuda
        --db-path PATH      Especificar ruta a la base de datos
                           (Por defecto: ../../widget_sidebar.db)

    DESCRIPCIÓN:
        Este script agrega 3 settings nuevos para la gestión de archivos:

        • files_base_path          - Ruta base de almacenamiento
        • files_folders_config     - JSON con mapeo de carpetas
        • files_auto_create_folders - Boolean para auto-creación

    VALORES POR DEFECTO:
        files_base_path: "" (vacío)
        files_folders_config: {
            "VIDEOS": "VIDEOS",
            "IMAGENES": "IMAGENES",
            "PDFS": "PDFS",
            "WORDS": "WORDS",
            "EXCELS": "EXCELS",
            "TEXT": "TEXT",
            "OTROS": "OTROS"
        }
        files_auto_create_folders: true

    EJEMPLOS:
        # Ejecutar migración con BD por defecto
        python migrate_add_files_settings.py

        # Especificar ruta a BD
        python migrate_add_files_settings.py --db-path C:\\path\\to\\db.db
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
        success = migrate_add_files_settings(db_path)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nWARN - Migracion cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR - La migracion fallo: {e}")
        sys.exit(1)
