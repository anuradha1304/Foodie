-- data.sql (Seed data)
-- Passwords are 'Password123' (BCrypt hashed)
INSERT INTO users (full_name, email, password_hash, phone, role, enabled, created_at) VALUES 
('Alice Customer', 'customer@foodapp.com', '$2a$10$P1NARuYDdJAPffbTgUVQkewu3xq38cpe0e2PBDl9Lw2S.buu5S8FO', '9876543210', 'CUSTOMER', true, NOW()),
('Bob Admin', 'admin1@foodapp.com', '$2a$10$P1NARuYDdJAPffbTgUVQkewu3xq38cpe0e2PBDl9Lw2S.buu5S8FO', '9876543211', 'RESTAURANT_ADMIN', true, NOW()),
('Charlie Admin', 'admin2@foodapp.com', '$2a$10$P1NARuYDdJAPffbTgUVQkewu3xq38cpe0e2PBDl9Lw2S.buu5S8FO', '9876543212', 'RESTAURANT_ADMIN', true, NOW())
ON DUPLICATE KEY UPDATE enabled = true;

INSERT INTO restaurants (name, description, cuisine_type, address, phone, image_url, is_open, owner_id, created_at) VALUES 
('Punjab Grill', 'Authentic North Indian food', 'North Indian', '123 Curry Lane', '1112223334', '/images/r1.jpg', true, 2, NOW()),
('La Piazza', 'Delicious Italian pizzas and pastas', 'Italian', '456 Pasta Ave', '5556667778', '/images/r2.jpg', true, 3, NOW())
ON DUPLICATE KEY UPDATE is_open = true;

-- Items for Restaurant 1 (North Indian, restaurant_id = 1)
INSERT INTO menu_items (restaurant_id, name, description, category, price, image_url, is_available, is_deleted, version, created_at, updated_at) VALUES 
(1, 'Paneer Tikka', 'Spicy grilled paneer', 'Starters', 249.00, '/images/p1.jpg', true, false, 0, NOW(), NOW()),
(1, 'Samosa', 'Crispy potato pastry', 'Starters', 49.00, '/images/p2.jpg', false, false, 0, NOW(), NOW()),
(1, 'Butter Chicken', 'Creamy chicken curry', 'Main Course', 349.00, '/images/p3.jpg', true, false, 0, NOW(), NOW()),
(1, 'Dal Makhani', 'Slow cooked black lentils', 'Main Course', 229.00, '/images/p4.jpg', true, false, 0, NOW(), NOW()),
(1, 'Garlic Naan', 'Tandoori bread with garlic', 'Breads', 69.00, '/images/p5.jpg', true, false, 0, NOW(), NOW()),
(1, 'Tandoori Roti', 'Whole wheat tandoori bread', 'Breads', 29.00, '/images/p6.jpg', true, false, 0, NOW(), NOW()),
(1, 'Gulab Jamun', 'Sweet milk dumplings', 'Desserts', 99.00, '/images/p7.jpg', true, false, 0, NOW(), NOW());

-- Items for Restaurant 2 (Italian, restaurant_id = 2)
INSERT INTO menu_items (restaurant_id, name, description, category, price, image_url, is_available, is_deleted, version, created_at, updated_at) VALUES 
(2, 'Bruschetta', 'Toasted bread with tomatoes', 'Starters', 199.00, '/images/i1.jpg', true, false, 0, NOW(), NOW()),
(2, 'Garlic Bread', 'Toasted bread with garlic butter', 'Starters', 149.00, '/images/i2.jpg', true, false, 0, NOW(), NOW()),
(2, 'Margherita Pizza', 'Classic cheese and tomato pizza', 'Pizzas', 399.00, '/images/i3.jpg', true, false, 0, NOW(), NOW()),
(2, 'Pepperoni Pizza', 'Spicy pepperoni pizza', 'Pizzas', 499.00, '/images/i4.jpg', false, false, 0, NOW(), NOW()),
(2, 'Penne Arrabbiata', 'Spicy tomato pasta', 'Pastas', 299.00, '/images/i5.jpg', true, false, 0, NOW(), NOW()),
(2, 'Fettuccine Alfredo', 'Creamy cheese pasta', 'Pastas', 349.00, '/images/i6.jpg', true, false, 0, NOW(), NOW()),
(2, 'Tiramisu', 'Coffee flavored Italian dessert', 'Desserts', 249.00, '/images/i7.jpg', true, false, 0, NOW(), NOW());
