query_strings = {
    "check_version": """
    SELECT version()
    """,
    "create_type": """
      CREATE TYPE category_type AS ENUM ('tools', 'consumables');
      """,
    "create_inventory_table": """
      CREATE TABLE IF NOT EXISTS hardware_inventory (
        hardware_id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        price DECIMAL(10, 2), 
        count SMALLINT, 
        category category_type
    );
    """,
    "insert_batch": """
      INSERT INTO hardware_inventory (name, price, count, category) VALUES
        ('Hammer', 9.99, 20, 'tools'),
        ('Pliers', 5.99, 20, 'tools'),
        ('Nails', 1.99, 100, 'consumables');
    """,
    "select_items": """
      SELECT * FROM hardware_inventory LIMIT 2;
    """,
    "select_id_by_name": """
      SELECT hardware_id FROM hardware_inventory WHERE name='Nails';      
    """,
}
