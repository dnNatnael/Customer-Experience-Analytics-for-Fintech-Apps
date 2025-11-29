import psycopg2


def create_connection():
  try:
    connection = psycopg2.connect(
      host='localhost',
      database='bank_reviews',
      user='postgres',
      password='0000',
      port='5432',
    )
    print("Connected to the PostgreSQL database")
    return connection
  except Exception as e:
    print("Error:", e)
    return None   
if __name__ == "__main__":
  connection = create_connection()