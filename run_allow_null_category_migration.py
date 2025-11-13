"""
Script to run the allow_null_category_id migration for pinned_panels
"""
from src.database.db_manager import DBManager
from src.database.migrations.allow_null_category_id_pinned_panels import upgrade

if __name__ == "__main__":
    print("="*60)
    print("Iniciando migracion: Permitir category_id NULL")
    print("="*60)

    # Create DBManager instance
    db = DBManager("widget_sidebar.db")

    # Run migration
    try:
        conn = db.connect()
        upgrade(conn)
        conn.commit()
        print("\n" + "="*60)
        print("MIGRACION COMPLETADA!")
        print("="*60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
