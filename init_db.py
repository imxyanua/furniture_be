#!/usr/bin/env python3
"""
Initialize database with tables and sample data
Run: python init_db.py
"""
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.product import Product, ProductItem
from app.models.category import Category, CategoryItem
from app.models.banner import Banner
from app.models.cart import CartItem
from app.models.favorite import Favorite
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.models.country import Country
from app.models.filter import Filter
from app.models.supplier import Supplier
from app.models.inventory import Inventory, InventoryTransaction
from app.utils.security import get_password_hash
from app.utils.helpers import generate_id
from datetime import datetime


def init_database(drop_existing=False):
    if drop_existing:
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped successfully!")
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            print("Database already has data. Skipping seed data.")
            return
        
        print("Seeding initial data...")
        
        # Create admin user
        admin = User(
            id="USR_ADMIN01",
            email="admin@furniture.com",
            phone="0123456789",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            status="active"
        )
        db.add(admin)
        
        # Create test user
        test_user = User(
            id="USR_TEST01",
            email="user@test.com",
            phone="0987654321",
            password_hash=get_password_hash("user123"),
            full_name="Test User",
            role="user",
            status="active"
        )
        db.add(test_user)
        
        # Create categories
        living_room = Category(
            id="CAT01",
            name="Living Room Furniture",
            img="/assets/categorys/Living Room Furniture/category.jpg",
            status="active"
        )
        db.add(living_room)
        
        bedroom = Category(
            id="CAT02",
            name="Bedroom Furniture",
            img="/assets/categorys/Bedroom Furniture/category.jpg",
            status="active"
        )
        db.add(bedroom)
        
        # Create category items
        sofa_item = CategoryItem(
            id="CATITEM01",
            category_id="CAT01",
            name="Sofas",
            img="/assets/categorys/Living Room Furniture/sofa.jpg",
            status="active"
        )
        db.add(sofa_item)
        
        bed_item = CategoryItem(
            id="CATITEM02",
            category_id="CAT02",
            name="Beds",
            img="/assets/categorys/Bedroom Furniture/bed.jpg",
            status="active"
        )
        db.add(bed_item)
        
        # Create sample products
        product1 = Product(
            id="PRO01",
            name="Modern Sofa",
            img="/assets/products/PRO01/main.jpg",
            title="Comfortable Modern Sofa",
            description="A beautiful and comfortable sofa for your living room",
            status="active",
            category_id="CATITEM01",
            material={"type": "Fabric", "quality": "Premium"},
            size={"width": "200cm", "height": "85cm", "depth": "90cm"},
            root_price=1500.0,
            current_price=1299.0,
            review_avg=4.5,
            sell_count=150
        )
        db.add(product1)
        
        product2 = Product(
            id="PRO02",
            name="King Size Bed",
            img="/assets/products/PRO02/main.jpg",
            title="Luxury King Size Bed",
            description="Premium quality king size bed with storage",
            status="active",
            category_id="CATITEM02",
            material={"type": "Wood", "quality": "Oak"},
            size={"width": "180cm", "length": "200cm"},
            root_price=2000.0,
            current_price=1799.0,
            review_avg=4.8,
            sell_count=95
        )
        db.add(product2)
        
        # Create product items (color variants)
        product1_item1 = ProductItem(
            id="PROITEM01",
            product_id="PRO01",
            color={"name": "Gray", "code": "#808080"},
            img=["/assets/products/PRO01/gray1.jpg", "/assets/products/PRO01/gray2.jpg"]
        )
        db.add(product1_item1)
        
        product2_item1 = ProductItem(
            id="PROITEM02",
            product_id="PRO02",
            color={"name": "Brown", "code": "#8B4513"},
            img=["/assets/products/PRO02/brown1.jpg", "/assets/products/PRO02/brown2.jpg"]
        )
        db.add(product2_item1)
        
        # Create banner
        banner1 = Banner(
            id="BAN01",
            date_start="2024-01-01",
            date_end="2024-12-31",
            img="/assets/banners/banner1.jpg",
            status="active",
            products=["PRO01", "PRO02"]
        )
        db.add(banner1)
        
        # Create countries
        vietnam = Country(
            id="VN",
            name="Vietnam",
            cities=["Ha Noi", "Ho Chi Minh", "Da Nang", "Can Tho", "Hai Phong"]
        )
        db.add(vietnam)
        
        usa = Country(
            id="US",
            name="United States",
            cities=["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        )
        db.add(usa)
        
        # Create default filter
        default_filter = Filter(
            id="default",
            category=None,
            price=["Under $100", "$100-$500", "$500-$1000", "Over $1000"],
            color={"Gray": "#808080", "Brown": "#8B4513", "White": "#FFFFFF", "Black": "#000000", "Beige": "#F5F5DC"},
            material=["Wood", "Metal", "Fabric", "Leather", "Glass"],
            feature=["Adjustable", "Storage", "Foldable", "Waterproof", "Eco-friendly"],
            popular_search=["Modern", "Vintage", "Minimalist", "Luxury", "Scandinavian"],
            price_range={"min": 0, "max": 10000},
            series=["Classic", "Modern", "Contemporary", "Traditional", "Industrial"],
            sort_by=["Price: Low to High", "Price: High to Low", "Name", "Newest", "Best Review"]
        )
        db.add(default_filter)
        
        # Create suppliers
        print("Creating suppliers...")
        supplier1 = Supplier(
            id="SUP_001",
            name="Công ty Gỗ Việt Nam",
            email="contact@goviet.com",
            phone="0901234567",
            address="123 Đường Gỗ, Quận 1",
            contact_person="Nguyễn Văn A",
            tax_code="0123456789",
            bank_account="1234567890",
            bank_name="Vietcombank",
            note="Nhà cung cấp gỗ chất lượng cao"
        )
        
        supplier2 = Supplier(
            id="SUP_002",
            name="Công ty Nội Thất Xanh",
            email="info@noithatxanh.com",
            phone="0907654321",
            address="456 Đường Nội Thất, Quận 2",
            contact_person="Trần Thị B",
            tax_code="0987654321",
            bank_account="9876543210",
            bank_name="Techcombank",
            note="Chuyên cung cấp phụ kiện nội thất"
        )
        
        db.add_all([supplier1, supplier2])
        db.flush()
        
        # Create inventory for products
        print("Creating inventory...")
        products = db.query(Product).all()
        for product in products:
            inventory = Inventory(
                id=generate_id("INV"),
                product_id=product.id,
                quantity_on_hand=100,
                quantity_reserved=0,
                reorder_level=20,
                reorder_quantity=50,
                last_restock_date=datetime.utcnow()
            )
            db.add(inventory)
        
        db.commit()
        print("Initial data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    drop_existing = "--drop" in sys.argv
    if drop_existing:
        confirm = input("⚠️  This will DROP all existing tables and data. Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    init_database(drop_existing=drop_existing)
    print("\nDatabase initialization completed!")
    print("\nTest credentials:")
    print("Admin - Email: admin@furniture.com, Password: admin123")
    print("User - Email: user@test.com, Password: user123")
