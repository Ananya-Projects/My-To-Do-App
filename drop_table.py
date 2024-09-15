import sqlite3

# Replace this with the correct path to your SQLite DB
db_path = 'C:/Users/DELL/Desktop/CODE/mytodo_app/instance/tasks.db'


conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the alembic_version table
cursor.execute('DROP TABLE IF EXISTS alembic_version;')
conn.commit()

print("Dropped alembic_version table.")
conn.close()
