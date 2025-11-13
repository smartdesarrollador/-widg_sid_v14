import sqlite3

conn = sqlite3.connect('widget_sidebar.db')
cursor = conn.cursor()

# Check panels 49 and 54
cursor.execute("""
    SELECT id, category_id, panel_type, custom_name, is_active
    FROM pinned_panels
    WHERE id IN (49, 54) OR category_id IS NULL
""")

print("Panels with category_id=NULL:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, category_id: {row[1]}, panel_type: {row[2]}, name: {row[3]}, active: {row[4]}")

conn.close()
