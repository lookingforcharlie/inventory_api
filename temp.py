import psycopg2

# Define your database connection parameters
db_params = {
    "host": "localhost",
    "database": "your_database_name",
    "user": "your_username",
    "password": "your_password",
}


def create_db_connection():
    try:
        # Establish a database connection
        connection = psycopg2.connect(**db_params)
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"Error creating database connection: {error}")
        return None


def close_db_connection(connection):
    try:
        if connection:
            connection.close()
            print("Database connection closed.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error closing database connection: {error}")


def insert_hardware_item(name, price, count, category):
    try:
        # Create a database connection
        connection = create_db_connection()

        if connection:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Define the SQL query with placeholders for the values
            sql = """
                INSERT INTO hardware_inventory (name, price, count, category)
                VALUES (%s, %s, %s, %s)
            """

            # Execute the query with the provided values
            cursor.execute(sql, (name, price, count, category))

            # Commit the transaction
            connection.commit()

            # Close the cursor and the database connection
            cursor.close()
            close_db_connection(connection)

            print("Item inserted successfully.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting item: {error}")


# Example usage
insert_hardware_item("Screwdriver", 4.99, 50, "tools")
insert_hardware_item("Paintbrush", 6.49, 30, "tools")
