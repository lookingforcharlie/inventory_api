CREATE TYPE category_type AS ENUM ('tools', 'consumables');

CREATE TABLE hardware_inventory(
  hardware_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  price DECIMAL(10, 2), 
  count SMALLINT, 
  category category_type
)

