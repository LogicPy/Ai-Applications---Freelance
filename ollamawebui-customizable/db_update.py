import sqlite3

# Connect to the database
conn = sqlite3.connect('chats.db')
cursor = conn.cursor()

# Run SQL commands
try:
    # Check the schema of the chat_sessions table
    cursor.execute("PRAGMA table_info(chat_sessions);")
    schema = cursor.fetchall()
    print("Table Schema:", schema)

    # Delete from alembic_version table
    cursor.execute("DELETE FROM alembic_version;")
    print("Deleted migration history.")

    # Commit changes
    conn.commit()
except sqlite3.Error as e:
    print("Error:", e)
finally:
    conn.close()
    print("Database connection closed.")
