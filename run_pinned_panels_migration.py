"""
Script to run pinned_panels migration for global search support
"""
from src.database.db_manager import DBManager
from src.database.migrations.add_global_search_to_pinned_panels import upgrade

if __name__ == "__main__":
    print("="*60)
    print("Iniciando migracion de pinned_panels...")
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
