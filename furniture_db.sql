-- ============================================
-- FURNITURE STORE - COMPLETE DATABASE SCHEMA
-- Compatible with Flutter Frontend & Python Backend
-- Includes: User Shopping + Admin Management
-- ============================================

CREATE DATABASE IF NOT EXISTS furniture_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE furniture_db;

Drop database furniture_db;


-- ============================================
-- CORE TABLES - USER & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    address VARCHAR(255),
    img VARCHAR(500),
    birth_date VARCHAR(50),
    gender VARCHAR(20),
    date_enter DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    role ENUM('user', 'admin') DEFAULT 'user',
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_role (role)
) ENGINE=InnoDB;
-- ============================================
-- PRODUCT CATALOG
-- ============================================

CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    img VARCHAR(500),
    status ENUM('active', 'inactive') DEFAULT 'active',
    INDEX idx_name (name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE category_items (
    id VARCHAR(50) PRIMARY KEY,
    category_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    img VARCHAR(500),
    status ENUM('active', 'inactive') DEFAULT 'active',
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img VARCHAR(500),
    title VARCHAR(255),
    description TEXT,
    status ENUM('active', 'inactive', 'out_of_stock') DEFAULT 'active',
    category_id VARCHAR(50),
    material JSON,
    size JSON,
    root_price FLOAT DEFAULT 0,
    current_price FLOAT DEFAULT 0,
    review_avg FLOAT DEFAULT 0,
    sell_count FLOAT DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category_items(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_timestamp (timestamp),
    INDEX idx_price (current_price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE product_items (
    id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    color JSON,
    img JSON,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SHOPPING FEATURES
-- ============================================

CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_item_id VARCHAR(50),
    quantity INT DEFAULT 1,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255),
    img VARCHAR(500),
    color JSON,
    price FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (product_item_id) REFERENCES product_items(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255),
    img VARCHAR(500),
    price FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id),
    INDEX idx_user (user_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- ORDERS & CHECKOUT
-- ============================================

CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100),
    address TEXT NOT NULL,
    note TEXT,
    date_order DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL,
    status_payment ENUM('unpaid', 'paid', 'refunded') DEFAULT 'unpaid',
    sub_total FLOAT NOT NULL,
    vat FLOAT DEFAULT 0,
    delivery_fee FLOAT DEFAULT 0,
    total_order FLOAT NOT NULL,
    status_order ENUM('pending', 'confirmed', 'shipping', 'delivered', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    img VARCHAR(500),
    color JSON,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- ============================================
-- REVIEWS & RATINGS
-- ============================================

CREATE TABLE reviews (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    rating FLOAT NOT NULL CHECK (rating >= 0 AND rating <= 5),
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_user (user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- NOTIFICATIONS
-- ============================================

CREATE TABLE notifications (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('order', 'promotion', 'system') DEFAULT 'order',
    reference_id VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_timestamp (timestamp),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- MARKETING & UI
-- ============================================

CREATE TABLE banners (
    id VARCHAR(50) PRIMARY KEY,
    img VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    link VARCHAR(500),
    date_start DATE,
    date_end DATE,
    status ENUM('active', 'inactive') DEFAULT 'active',
    display_order INT DEFAULT 0,
    product JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE countries (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10),
    city JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE filters (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100),
    price JSON,
    color JSON,
    material JSON,
    feature JSON,
    popular_search JSON,
    price_range JSON,
    series JSON,
    sort_by JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INVENTORY MANAGEMENT (ADMIN)
-- ============================================

CREATE TABLE suppliers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    contact_person VARCHAR(100),
    tax_code VARCHAR(50),
    bank_account VARCHAR(100),
    bank_name VARCHAR(100),
    note VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE inventory (
    id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    quantity_on_hand INT DEFAULT 0,
    quantity_reserved INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    reorder_quantity INT DEFAULT 50,
    last_restock_date DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_quantity (quantity_on_hand)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE inventory_transactions (
    id VARCHAR(50) PRIMARY KEY,
    inventory_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50),
    transaction_type ENUM('import_stock', 'export_stock', 'adjustment', 'return_stock') NOT NULL,
    quantity INT NOT NULL,
    unit_cost FLOAT,
    total_cost FLOAT,
    reference_number VARCHAR(100),
    note VARCHAR(500),
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_inventory (inventory_id),
    INDEX idx_product (product_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_type (transaction_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SAMPLE DATA - USERS
-- ============================================

DELETE FROM users;


INSERT INTO users VALUES
('USR_ADMIN01','admin@furniture.com','0123456789','123456','Admin Manager',NULL,NULL,NULL,NULL,NOW(),'active','admin'),
('USR_ADMIN02','xyanua@gmail.com','0986252525','986252525','xyanua',NULL,NULL,NULL,'male',NOW(),'active','admin'),
('USR_USER01','user@test.com','0987654321','123456','Test User','123 Test Street',NULL,'1990-01-01','male',NOW(),'active','user'),
('USR_USER02','nguyen@gmail.com','0901234567','123456','Nguyễn Văn A','456 Đường Lê Lợi',NULL,'1985-05-15','male',NOW(),'active','user');
-- ============================================
-- SAMPLE DATA - CATEGORIES
-- ============================================

INSERT INTO categories VALUES 
('CAT_001', 'Bedroom Furniture  ', 'https://via.placeholder.com/300', 'active'),
('CAT_002', 'Entryway & Storage', 'https://via.placeholder.com/300', 'active'),
('CAT_003', 'Gaming Furniture', 'https://via.placeholder.com/300', 'active'),
('CAT_004', 'Bathroom Furniture', 'https://via.placeholder.com/300', 'active');

INSERT INTO category_items VALUES 
('CATI_001', 'CAT_001', 'Sofas', 'https://via.placeholder.com/200', 'active'),
('CATI_002', 'CAT_001', 'Coffee Tables', 'https://via.placeholder.com/200', 'active'),
('CATI_003', 'CAT_001', 'TV Stands', 'https://via.placeholder.com/200', 'active'),
('CATI_004', 'CAT_002', 'Beds', 'https://via.placeholder.com/200', 'active'),
('CATI_005', 'CAT_002', 'Wardrobes', 'https://via.placeholder.com/200', 'active'),
('CATI_006', 'CAT_003', 'Desks', 'https://via.placeholder.com/200', 'active'),
('CATI_007', 'CAT_003', 'Office Chairs', 'https://via.placeholder.com/200', 'active'),
('CATI_008', 'CAT_004', 'Dining Tables', 'https://via.placeholder.com/200', 'active'),
('CATI_009', 'CAT_004', 'Dining Chairs', 'https://via.placeholder.com/200', 'active');

-- ============================================
-- SAMPLE DATA - SUPPLIERS
-- ============================================

INSERT INTO suppliers VALUES 
('SUP_001', 'Công ty Gỗ Việt Nam', 'contact@goviet.com', '0901234567', 
 '123 Đường Gỗ, Quận 1, TP.HCM', 'Nguyễn Văn A', '0123456789', 
 '1234567890', 'Vietcombank', 'Nhà cung cấp gỗ chất lượng cao', NOW(), NOW()),
 
('SUP_002', 'Công ty Nội Thất Xanh', 'info@noithatxanh.com', '0907654321',
 '456 Đường Nội Thất, Quận 2, TP.HCM', 'Trần Thị B', '0987654321', 
 '9876543210', 'Techcombank', 'Chuyên cung cấp phụ kiện nội thất', NOW(), NOW()),
 
('SUP_003', 'Công ty Sắt Thép Đại Phát', 'sales@satthep.com', '0912345678',
 '789 Đường Công Nghiệp, Bình Dương', 'Lê Văn C', '0369852147',
 '3698521470', 'ACB Bank', 'Cung cấp khung sắt, kim loại', NOW(), NOW());

-- ============================================
-- SAMPLE DATA - PRODUCTS
-- ============================================

INSERT INTO products VALUES 
('PRD_001', 'Modern Fabric Sofa', 'https://via.placeholder.com/400', 
 'Comfortable 3-Seater Sofa', 
 'A beautiful modern sofa perfect for any living room. Made with high-quality fabric and solid wood frame.',
 'active', 'CATI_001',
 '{"type": "Fabric", "origin": "Vietnam", "quality": "Premium"}',
 '{"width": "200cm", "height": "85cm", "depth": "90cm", "weight": "65kg"}',
 5500000, 4500000, 4.5, 150, NOW()),
 
('PRD_002', 'Wooden Coffee Table', 'https://via.placeholder.com/400',
 'Rustic Oak Coffee Table',
 'Handcrafted wooden coffee table with storage drawer. Perfect for modern or traditional homes.',
 'active', 'CATI_002',
 '{"type": "Oak Wood", "origin": "Vietnam", "finish": "Natural"}',
 '{"width": "120cm", "height": "45cm", "depth": "60cm", "weight": "25kg"}',
 2800000, 2200000, 4.7, 200, NOW()),
 
('PRD_003', 'Executive Office Desk', 'https://via.placeholder.com/400',
 'Premium Ergonomic Work Desk',
 'Spacious desk with cable management system. Ideal for home office or corporate workspace.',
 'active', 'CATI_006',
 '{"type": "MDF Wood", "origin": "Vietnam", "coating": "Laminated"}',
 '{"width": "140cm", "height": "75cm", "depth": "70cm", "weight": "35kg"}',
 3500000, 2800000, 4.8, 180, NOW()),
 
('PRD_004', 'Ergonomic Office Chair', 'https://via.placeholder.com/400',
 'Premium Leather Executive Chair',
 'Comfortable chair with lumbar support and adjustable height. Perfect for long working hours.',
 'active', 'CATI_007',
 '{"type": "PU Leather", "origin": "Imported", "cushion": "Memory Foam"}',
 '{"width": "65cm", "height": "120cm", "depth": "65cm", "weight": "18kg"}',
 2500000, 1800000, 4.7, 250, NOW()),
 
('PRD_005', 'King Size Bed Frame', 'https://via.placeholder.com/400',
 'Luxury Wooden Bed Frame',
 'Elegant bed frame with headboard storage. Made from solid wood with modern design.',
 'active', 'CATI_004',
 '{"type": "Solid Wood", "origin": "Vietnam", "finish": "Walnut"}',
 '{"width": "200cm", "height": "120cm", "length": "220cm", "weight": "80kg"}',
 8500000, 7200000, 4.6, 95, NOW()),
 
('PRD_006', 'Dining Table Set', 'https://via.placeholder.com/400',
 '6-Seater Dining Table',
 'Modern dining table with 6 chairs. Perfect for family dinners and gatherings.',
 'active', 'CATI_008',
 '{"type": "Tempered Glass Top", "frame": "Metal", "origin": "Vietnam"}',
 '{"width": "160cm", "height": "75cm", "length": "90cm", "weight": "55kg"}',
 6500000, 5500000, 4.5, 120, NOW());

-- ============================================
-- SAMPLE DATA - PRODUCT ITEMS (Color Variants)
-- ============================================

INSERT INTO product_items VALUES 
('PRDI_001', 'PRD_001', '{"name": "Gray", "code": "#808080"}', 
 '["https://via.placeholder.com/400", "https://via.placeholder.com/400/808080"]'),
 
('PRDI_002', 'PRD_001', '{"name": "Beige", "code": "#F5F5DC"}',
 '["https://via.placeholder.com/400", "https://via.placeholder.com/400/F5F5DC"]'),
 
('PRDI_003', 'PRD_002', '{"name": "Natural Oak", "code": "#D2691E"}',
 '["https://via.placeholder.com/400", "https://via.placeholder.com/400/D2691E"]'),
 
('PRDI_004', 'PRD_003', '{"name": "Walnut Brown", "code": "#8B4513"}',
 '["https://via.placeholder.com/400"]'),
 
('PRDI_005', 'PRD_004', '{"name": "Black Leather", "code": "#000000"}',
 '["https://via.placeholder.com/400"]'),
 
('PRDI_006', 'PRD_005', '{"name": "Dark Walnut", "code": "#654321"}',
 '["https://via.placeholder.com/400"]'),
 
('PRDI_007', 'PRD_006', '{"name": "White & Silver", "code": "#F5F5F5"}',
 '["https://via.placeholder.com/400"]');

-- ============================================
-- SAMPLE DATA - INVENTORY
-- ============================================

INSERT INTO inventory VALUES 
('INV_001', 'PRD_001', 50, 5, 15, 30, NOW(), NOW()),
('INV_002', 'PRD_002', 80, 8, 20, 40, NOW(), NOW()),
('INV_003', 'PRD_003', 45, 3, 10, 25, NOW(), NOW()),
('INV_004', 'PRD_004', 120, 15, 25, 50, NOW(), NOW()),
('INV_005', 'PRD_005', 30, 2, 8, 20, NOW(), NOW()),
('INV_006', 'PRD_006', 60, 6, 12, 30, NOW(), NOW());

-- ============================================
-- SAMPLE DATA - NOTIFICATIONS
-- ============================================

INSERT INTO notifications (id, user_id, title, message, type, reference_id, is_read, timestamp) VALUES
('NOTIF_001', 'USR_USER01', 'Chào mừng đến với cửa hàng!', 'Cảm ơn bạn đã đăng ký tài khoản. Chúc bạn có trải nghiệm mua sắm tuyệt vời!', 'system', NULL, FALSE, NOW()),
('NOTIF_002', 'USR_USER01', 'Khuyến mãi đặc biệt', 'Giảm giá 20% cho tất cả sản phẩm nội thất phòng khách. Mã: LIVING20', 'promotion', NULL, FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY)),
('NOTIF_003', 'USR_USER02', 'Chào mừng đến với cửa hàng!', 'Cảm ơn bạn đã đăng ký tài khoản. Chúc bạn có trải nghiệm mua sắm tuyệt vời!', 'system', NULL, TRUE, DATE_SUB(NOW(), INTERVAL 2 DAY));

-- ============================================
-- SAMPLE DATA - BANNERS
-- ============================================

INSERT INTO banners VALUES 
('BAN_001', 'https://via.placeholder.com/1200x400', 
 'Summer Sale 2025', 'Up to 30% off on selected living room furniture', 
 '/products?category=CAT_001', '2025-06-01', '2025-06-30', 
 'active', 1, '["PRD_001", "PRD_002"]', NOW()),
 
('BAN_002', 'https://via.placeholder.com/1200x400',
 'New Arrivals', 'Check out our latest furniture collection',
 '/products/special/new-arrivals', '2025-01-01', '2025-12-31',
 'active', 2, '["PRD_003", "PRD_004", "PRD_005"]', NOW()),
 
('BAN_003', 'https://via.placeholder.com/1200x400',
 'Office Furniture Sale', 'Complete your workspace with our premium desks and chairs',
 '/products?category=CAT_003', '2025-03-01', '2025-03-31',
 'active', 3, '["PRD_003", "PRD_004"]', NOW());

-- ============================================
-- SAMPLE DATA - COUNTRIES
-- ============================================

INSERT INTO countries VALUES 
('CTR_001', 'Vietnam', 'VN', 
 '["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho", "Hai Phong", "Nha Trang"]'),
 
('CTR_002', 'Thailand', 'TH',
 '["Bangkok", "Chiang Mai", "Phuket", "Pattaya"]'),
 
('CTR_003', 'Singapore', 'SG',
 '["Singapore"]');

-- ============================================
-- SAMPLE DATA - FILTERS
-- ============================================

INSERT INTO filters VALUES (
    'default',
    NULL,
    '["Under $100", "$100-$500", "$500-$1000", "$1000-$3000", "Over $3000"]',
    '{"Gray": "#808080", "Brown": "#8B4513", "White": "#FFFFFF", "Black": "#000000", "Beige": "#F5F5DC", "Walnut": "#654321"}',
    '["Wood", "Metal", "Fabric", "Leather", "Glass", "MDF", "Rattan"]',
    '["Adjustable", "Storage", "Foldable", "Waterproof", "Eco-friendly", "Ergonomic", "Modern Design"]',
    '["Modern", "Vintage", "Minimalist", "Luxury", "Scandinavian", "Industrial", "Contemporary"]',
    '{"min": 0, "max": 20000000}',
    '["Classic", "Modern", "Contemporary", "Traditional", "Industrial", "Scandinavian"]',
    '["Price: Low to High", "Price: High to Low", "Name A-Z", "Newest First", "Best Review", "Best Seller"]'
);

-- ============================================
-- SAMPLE DATA - REVIEWS
-- ============================================

INSERT INTO reviews VALUES 
('REV_001', 'USR_USER01', 'PRD_001', 4.5, 
 'Very comfortable sofa! Good quality fabric and sturdy construction.', NOW()),
 
('REV_002', 'USR_USER02', 'PRD_001', 5.0,
 'Excellent product! Worth every penny. Highly recommended!', NOW()),
 
('REV_003', 'USR_USER01', 'PRD_002', 4.5,
 'Beautiful coffee table. The wood quality is great and it has nice storage space.', NOW()),
 
('REV_004', 'USR_USER02', 'PRD_004', 5.0,
 'Best office chair I ever bought! Very comfortable for long hours.', NOW());

-- ============================================
-- TRIGGERS - AUTO UPDATE REVIEW AVERAGE
-- ============================================

-- =============================================
-- Update Database with Assets Paths for Flutter
-- =============================================


-- Update Banners with assets paths
UPDATE banners SET img = 'assets/banners/banner1.jpg' WHERE id = 'BAN_001';
UPDATE banners SET img = 'assets/banners/banner2.jpg' WHERE id = 'BAN_002';
UPDATE banners SET img = 'assets/banners/banner3.jpg' WHERE id = 'BAN_003';

-- Update Categories with assets paths
UPDATE categories SET img = 'assets/categorys/Bedroom_Furniture.png' WHERE id = 'CAT_001';
UPDATE categories SET img = 'assets/categorys/Entryway_Furniture_&_Storage.png' WHERE id = 'CAT_002';
UPDATE categories SET img = 'assets/categorys/Gaming_Furniture.png' WHERE id = 'CAT_003';
UPDATE categories SET img = 'assets/categorys/Bathroom_Furniture.png' WHERE id = 'CAT_004';
UPDATE categories SET img = 'assets/categorys/BathroomFurniture/Bathroom_cabinets.png' WHERE id = 'CAT_005';
UPDATE categories SET img = 'assets/categorys/EntrywayFurniture&Storage/Banches.png' WHERE id = 'CAT_006';
UPDATE categories SET img = 'assets/categorys/KidsFurniture/Kids_armchair.png' WHERE id = 'CAT_007';
UPDATE categories SET img = 'assets/categorys/GamingFurniture/Gaming_chairs.png' WHERE id = 'CAT_008';
UPDATE categories SET img = 'assets/categorys/PatioFurniture/Patio_sets.png' WHERE id = 'CAT_009';

-- Update Category Items with assets paths
-- Living Room
UPDATE category_items SET img = 'assets/categorys/LivingRoomFurniture/Coffee_tables.png' WHERE id = 'CATI_001';
UPDATE category_items SET img = 'assets/categorys/LivingRoomFurniture/Coffee_tables.png' WHERE id = 'CATI_002';
UPDATE category_items SET img = 'assets/categorys/LivingRoomFurniture/Armchairs_accent_chairs.png' WHERE id = 'CATI_003';

-- Bedroom
UPDATE category_items SET img = 'assets/categorys/BedroomFurniture/Beds.png' WHERE id = 'CATI_004';
UPDATE category_items SET img = 'assets/categorys/BedroomFurniture/Armoires_&_warddrobes.png' WHERE id = 'CATI_005';

-- Office
UPDATE category_items SET img = 'assets/categorys/OfficeFurniture/Gaming_desks.png' WHERE id = 'CATI_006' AND name = 'Desks';
UPDATE category_items SET img = 'assets/categorys/GamingFurniture/Gaming_chairs.png' WHERE id = 'CATI_007';

-- Kitchen & Dining
UPDATE category_items SET img = 'assets/categorys/Kitchen&DiningFurniture/Kitchen_islands.png' WHERE id = 'CATI_008';
UPDATE category_items SET img = 'assets/categorys/Kitchen&DiningFurniture/Kitchen_cabinets.png' WHERE id = 'CATI_009';

SELECT id, name, img FROM categories LIMIT 2;

SELECT id, img FROM products LIMIT 5;

-- Update Products with assets paths
-- Bạn cần đặt ảnh vào: assets/products/PRO01/, assets/products/PRO02/, etc.
-- Ví dụ với các sản phẩm hiện có:

UPDATE products SET img = 'assets/products/PRO01/PRO01-1.png' WHERE id = 'PRD_001';
UPDATE products SET img = 'assets/products/PRO02/PRO02-1.png' WHERE id = 'PRD_002';
UPDATE products SET img = 'assets/products/PRO03/PRO03-1.png' WHERE id = 'PRD_003';  -- Dùng -1.png thay vì MAIN
UPDATE products SET img = 'assets/products/PRO04/PRO04-1.png' WHERE id = 'PRD_004';  -- Dùng -1.png thay vì MAIN
UPDATE products SET img = 'assets/products/PRO05/PRO05-1.png' WHERE id = 'PRD_005';  -- Dùng -1.png thay vì MAIN
UPDATE products SET img = 'assets/products/PRO06/PRO06-1.png' WHERE id = 'PRD_006';
UPDATE products SET img = 'assets/products/PRO07/PRO07-1.png' WHERE id = 'PRD_007';  -- Nếu có
UPDATE products SET img = 'assets/products/PRO08/PRO08-1.png' WHERE id = 'PRD_008';  -- Nếu có
UPDATE products SET img = 'assets/products/PRO09/PRO09-1.png' WHERE id = 'PRD_009';  -- Nếu có

-- Update Product Items with assets paths
UPDATE product_items SET img = '["assets/products/PRO01/PRO01-1.png", "assets/products/PRO01/PRO01-2.png"]' WHERE id = 'PRDI_001';
UPDATE product_items SET img = '["assets/products/PRO01/PRO01-3.png", "assets/products/PRO01/PRO01-4.png"]' WHERE id = 'PRDI_002';
UPDATE product_items SET img = '["assets/products/PRO02/PRO02-1.png", "assets/products/PRO02/PRO02-2.png"]' WHERE id = 'PRDI_003';
UPDATE product_items SET img = '["assets/products/PRO03/PRO03-1.png"]' WHERE id = 'PRDI_004';
UPDATE product_items SET img = '["assets/products/PRO04/PRO04-1.png"]' WHERE id = 'PRDI_005';
UPDATE product_items SET img = '["assets/products/PRO05/PRO05-1.png"]' WHERE id = 'PRDI_006';
UPDATE product_items SET img = '["assets/products/PRO06/PRO06-1.png"]' WHERE id = 'PRDI_007';

-- Update User avatar paths (nếu có)
-- UPDATE users SET img = 'assets/icons/user.png' WHERE img IS NULL OR img = '';

-- Verify updates
SELECT 'Banners' as Table_Name, id, img FROM banners
UNION ALL
SELECT 'Categories', id, img FROM categories
UNION ALL
SELECT 'Category Items', id, img FROM category_items
UNION ALL
SELECT 'Products', id, img FROM products;







DELIMITER $$

CREATE TRIGGER update_product_review_avg AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE products 
    SET review_avg = (
        SELECT AVG(rating) 
        FROM reviews 
        WHERE product_id = NEW.product_id
    )
    WHERE id = NEW.product_id;
END$$

CREATE TRIGGER update_product_review_avg_update AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    UPDATE products 
    SET review_avg = (
        SELECT AVG(rating) 
        FROM reviews 
        WHERE product_id = NEW.product_id
    )
    WHERE id = NEW.product_id;
END$$

CREATE TRIGGER update_product_review_avg_delete AFTER DELETE ON reviews
FOR EACH ROW
BEGIN
    UPDATE products 
    SET review_avg = COALESCE((
        SELECT AVG(rating) 
        FROM reviews 
        WHERE product_id = OLD.product_id
    ), 0)
    WHERE id = OLD.product_id;
END$$

DELIMITER ;

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 'Database Created Successfully!' as status;
SELECT '';
SELECT 'TABLE COUNTS:' as info;

SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'category_items', COUNT(*) FROM category_items
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'product_items', COUNT(*) FROM product_items
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'banners', COUNT(*) FROM banners
UNION ALL SELECT 'countries', COUNT(*) FROM countries
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL SELECT 'notifications', COUNT(*) FROM notifications;

SELECT '';
SELECT 'LOGIN CREDENTIALS:' as info;
SELECT '─────────────────────────────────' as separator;
SELECT 'Admin' as role, '0123456789' as email, 'admin123' as password
UNION ALL
SELECT 'User', '0987654321', 'user1234'
UNION ALL
SELECT 'User', '0901234567', 'user1234';

SELECT '';
SELECT 'All done! Database is ready to use.' as message;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
SET FOREIGN_KEY_CHECKS = 1;


SHOW TABLES;
DESCRIBE orders;
DESCRIBE order_items;