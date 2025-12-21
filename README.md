# Furniture Store Backend API

Backend API cho ứng dụng Furniture Store được xây dựng với FastAPI + MySQL + SQLAlchemy.

## Công nghệ sử dụng

- **FastAPI**: Modern, fast web framework cho Python
- **MySQL**: Relational database với MySQL Workbench
- **SQLAlchemy**: Python SQL toolkit và ORM
- **JWT**: Authentication với JSON Web Tokens
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Yêu cầu hệ thống

- Python 3.8+
- MySQL Server 8.0+
- MySQL Workbench (khuyến nghị)

## Cài đặt

### 1. Clone repository và tạo virtual environment

```bash
cd furniture_be
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình MySQL Database

**Sử dụng MySQL Workbench:**

1. Mở MySQL Workbench
2. Kết nối tới MySQL Server
3. Tạo database mới:

```sql
CREATE DATABASE furniture_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Cấu hình môi trường

Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/furniture_db
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
HOST=0.0.0.0
PORT=8000
```

**Lưu ý:** Thay `your_password` bằng password MySQL của bạn.

### 5. Khởi tạo database

```bash
python init_db.py
```

Script này sẽ:
- Tạo tất cả các bảng trong database
- Seed dữ liệu mẫu (categories, products, users)
- Tạo 2 tài khoản test

**Tài khoản test:**
- Admin: `admin@furniture.com` / `admin12
- User: `user@test.com` / `user123`3`

### 6. Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

## API Documentation

Sau khi chạy server, truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký user mới
- `POST /auth/login` - Đăng nhập

### Users
- `GET /users/me` - Lấy thông tin user hiện tại
- `PUT /users/me` - Cập nhật thông tin user
- `GET /users/me/reviews` - Lấy reviews của user

### Products
- `GET /products` - Danh sách sản phẩm (có filter, sort, pagination)
- `GET /products/{id}` - Chi tiết sản phẩm
- `GET /products/special/new-arrivals` - Sản phẩm mới
- `GET /products/special/top-seller` - Bán chạy nhất
- `GET /products/special/best-review` - Review tốt nhất
- `GET /products/special/discount` - Sản phẩm giảm giá
- `GET /products/{id}/reviews` - Reviews của sản phẩm
- `POST /products/{id}/reviews` - Tạo review
- `PATCH /reviews/{id}` - Cập nhật review
- `DELETE /reviews/{id}` - Xóa review

### Categories
- `GET /categories` - Danh sách categories

### Banners
- `GET /banners` - Danh sách banners

### Cart
- `GET /cart` - Lấy giỏ hàng
- `POST /cart` - Thêm vào giỏ
- `PATCH /cart/{id}` - Cập nhật số lượng
- `DELETE /cart/{id}` - Xóa khỏi giỏ

### Favorites
- `GET /favorites` - Danh sách yêu thích
- `POST /favorites` - Thêm yêu thích
- `DELETE /favorites/{id}` - Xóa yêu thích

### Orders
- `GET /orders` - Lịch sử đơn hàng
- `POST /orders` - Tạo đơn hàng mới

### Countries
- `GET /countries` - Danh sách quốc gia và thành phố

## Database Schema

### Tables
- `users` - Người dùng
- `products` - Sản phẩm
- `product_items` - Biến thể sản phẩm (màu sắc)
- `categories` - Danh mục
- `category_items` - Mục con của danh mục
- `banners` - Banner quảng cáo
- `cart_items` - Giỏ hàng
- `favorites` - Danh sách yêu thích
- `orders` - Đơn hàng
- `order_items` - Chi tiết đơn hàng
- `reviews` - Đánh giá sản phẩm
- `countries` - Quốc gia và thành phố

## Xem database trong MySQL Workbench

1. Mở MySQL Workbench
2. Kết nối tới server
3. Chọn schema `furniture_db`
4. Xem tables và data

## Development

### Thêm model mới

1. Tạo model trong `app/models/`
2. Tạo schema trong `app/schemas/`
3. Tạo router trong `app/routers/`
4. Include router trong `app/main.py`
5. Chạy lại `init_db.py` hoặc sử dụng Alembic migrations

### Testing API

Sử dụng Swagger UI tại `/docs` hoặc tools như:
- Postman
- Thunder Client (VS Code extension)
- curl

## Troubleshooting

### Lỗi kết nối database

```
Can't connect to MySQL server
```

**Giải pháp:**
- Kiểm tra MySQL server đang chạy
- Kiểm tra username/password trong `.env`
- Kiểm tra port MySQL (mặc định 3306)

### Lỗi import module

```
ModuleNotFoundError
```

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### Lỗi JWT token

```
Invalid authentication credentials
```

**Giải pháp:**
- Đăng nhập lại để lấy token mới
- Kiểm tra SECRET_KEY trong `.env`

## License

MIT License
