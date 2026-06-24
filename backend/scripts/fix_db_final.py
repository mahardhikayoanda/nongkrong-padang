import psycopg2
from urllib.parse import urlparse

DATABASE_URL = "postgresql://nongkrong_user:nongkrong_pass@localhost:5432/nongkrong_db"

def manual_migrate():
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    try:
        print(f"Connecting to {hostname}:{port} / {database} as {username}...")
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("Checking users table...")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users';")
        columns = [row[0] for row in cur.fetchall()]
        print(f"Current columns: {columns}")

        if 'jenis_kelamin' not in columns:
            print("Adding column 'jenis_kelamin'...")
            cur.execute("ALTER TABLE users ADD COLUMN jenis_kelamin VARCHAR(20);")
            print("Successfully added column.")
        else:
            print("Column 'jenis_kelamin' already exists.")

        cur.close()
        conn.close()
        print("Migration task finished.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    manual_migrate()
