from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
import random
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 30

# Create the main app
app = FastAPI(title="Pharmacy API")
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

# User Models
class UserBase(BaseModel):
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    addresses: List[Dict[str, Any]] = []
    wishlist: List[str] = []

class UserCreate(BaseModel):
    phone: str
    name: str

class LoginRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

class LoginResponse(BaseModel):
    token: str
    user: User
    message: str

# Medicine Models
class Substitute(BaseModel):
    id: str
    name: str
    price: float

class Medicine(BaseModel):
    id: str
    name: str
    salt_composition: str
    category: str
    price: float
    discount: float = 0
    final_price: float
    stock_quantity: int
    description: str
    usage: str
    manufacturer: str
    requires_prescription: bool = False
    image: Optional[str] = None  # base64
    substitutes: List[Substitute] = []
    rating: float = 4.5
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MedicineCreate(BaseModel):
    name: str
    salt_composition: str
    category: str
    price: float
    discount: float = 0
    stock_quantity: int
    description: str
    usage: str
    manufacturer: str
    requires_prescription: bool = False
    image: Optional[str] = None
    substitutes: List[Substitute] = []

# Cart Models
class CartItem(BaseModel):
    medicine_id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None

class Cart(BaseModel):
    user_id: str
    items: List[CartItem] = []
    total: float = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AddToCartRequest(BaseModel):
    medicine_id: str
    quantity: int = 1

# Order Models
class OrderItem(BaseModel):
    medicine_id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None

class Address(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    phone: str

class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    subtotal: float
    delivery_charges: float
    discount: float = 0
    total: float
    payment_method: str
    payment_status: str = "pending"
    delivery_address: Address
    status: str = "placed"  # placed, confirmed, packed, out_for_delivery, delivered, cancelled
    prescription_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    delivery_address: Address
    payment_method: str = "COD"
    coupon_code: Optional[str] = None

# Prescription Models
class Prescription(BaseModel):
    id: str
    user_id: str
    image: str  # base64
    status: str = "pending"  # pending, verified, rejected
    notes: Optional[str] = None
    verified_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PrescriptionUpload(BaseModel):
    image: str
    notes: Optional[str] = None

# Admin Models
class AdminLogin(BaseModel):
    username: str
    password: str

class OrderStatusUpdate(BaseModel):
    status: str

class DashboardStats(BaseModel):
    total_orders: int
    total_revenue: float
    pending_orders: int
    total_users: int
    low_stock_medicines: int
    pending_prescriptions: int

# ==================== AUTHENTICATION ====================

def create_jwt_token(user_id: str) -> str:
    """Create JWT token for user"""
    expiration = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT token and return user_id"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace('Bearer ', '')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Mock OTP storage (in production, use Redis)
otp_storage = {}

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/send-otp")
async def send_otp(request: LoginRequest):
    """Send OTP to phone (mock implementation)"""
    otp = generate_otp()
    otp_storage[request.phone] = otp
    
    # In production, send OTP via SMS service
    logging.info(f"OTP for {request.phone}: {otp}")
    
    return {
        "success": True,
        "message": "OTP sent successfully",
        "otp": otp  # Remove this in production!
    }

@api_router.post("/auth/verify-otp", response_model=LoginResponse)
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP and login/register user"""
    stored_otp = otp_storage.get(request.phone)
    
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Remove used OTP
    del otp_storage[request.phone]
    
    # Check if user exists
    user_doc = await db.users.find_one({"phone": request.phone})
    
    if not user_doc:
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "phone": request.phone,
            "name": "",
            "email": "",
            "addresses": [],
            "wishlist": [],
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        user_doc = new_user
    
    user = User(**user_doc)
    token = create_jwt_token(user.id)
    
    return LoginResponse(
        token=token,
        user=user,
        message="Login successful"
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """Get current user information"""
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_doc)

@api_router.put("/auth/profile")
async def update_profile(user_data: Dict[str, Any], user_id: str = Depends(get_current_user)):
    """Update user profile"""
    await db.users.update_one(
        {"id": user_id},
        {"$set": user_data}
    )
    return {"success": True, "message": "Profile updated"}

# ==================== MEDICINE ENDPOINTS ====================

@api_router.get("/medicines", response_model=List[Medicine])
async def get_medicines(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get medicines with search and filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"salt_composition": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    medicines = await db.medicines.find(query).skip(skip).limit(limit).to_list(limit)
    return [Medicine(**med) for med in medicines]

@api_router.get("/medicines/{medicine_id}", response_model=Medicine)
async def get_medicine(medicine_id: str):
    """Get medicine details"""
    medicine = await db.medicines.find_one({"id": medicine_id})
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return Medicine(**medicine)

@api_router.get("/categories")
async def get_categories():
    """Get all categories"""
    categories = await db.medicines.distinct("category")
    return {"categories": categories}

# ==================== CART ENDPOINTS ====================

@api_router.get("/cart", response_model=Cart)
async def get_cart(user_id: str = Depends(get_current_user)):
    """Get user's cart"""
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": [], "total": 0}
        await db.carts.insert_one(cart)
    return Cart(**cart)

@api_router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest, user_id: str = Depends(get_current_user)):
    """Add item to cart"""
    # Get medicine
    medicine = await db.medicines.find_one({"id": request.medicine_id})
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": [], "total": 0}
    
    # Check if item exists in cart
    items = cart.get("items", [])
    found = False
    for item in items:
        if item["medicine_id"] == request.medicine_id:
            item["quantity"] += request.quantity
            found = True
            break
    
    if not found:
        items.append({
            "medicine_id": request.medicine_id,
            "name": medicine["name"],
            "price": medicine.get("final_price", medicine["price"]),
            "quantity": request.quantity,
            "image": medicine.get("image")
        })
    
    # Calculate total
    total = sum(item["price"] * item["quantity"] for item in items)
    
    # Update cart
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "total": total, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    
    return {"success": True, "message": "Item added to cart"}

@api_router.put("/cart/update/{medicine_id}")
async def update_cart_item(medicine_id: str, quantity: int, user_id: str = Depends(get_current_user)):
    """Update cart item quantity"""
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = cart.get("items", [])
    
    if quantity <= 0:
        # Remove item
        items = [item for item in items if item["medicine_id"] != medicine_id]
    else:
        # Update quantity
        for item in items:
            if item["medicine_id"] == medicine_id:
                item["quantity"] = quantity
                break
    
    total = sum(item["price"] * item["quantity"] for item in items)
    
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "total": total, "updated_at": datetime.utcnow()}}
    )
    
    return {"success": True, "message": "Cart updated"}

@api_router.delete("/cart/clear")
async def clear_cart(user_id: str = Depends(get_current_user)):
    """Clear cart"""
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": [], "total": 0, "updated_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Cart cleared"}

# ==================== ORDER ENDPOINTS ====================

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, user_id: str = Depends(get_current_user)):
    """Create new order from cart"""
    # Get cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate order totals
    subtotal = cart["total"]
    delivery_charges = 0 if subtotal > 500 else 50
    discount = 0
    total = subtotal + delivery_charges - discount
    
    # Create order
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": user_id,
        "items": cart["items"],
        "subtotal": subtotal,
        "delivery_charges": delivery_charges,
        "discount": discount,
        "total": total,
        "payment_method": order_data.payment_method,
        "payment_status": "pending" if order_data.payment_method == "COD" else "paid",
        "delivery_address": order_data.delivery_address.dict(),
        "status": "placed",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(order)
    
    # Clear cart
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": [], "total": 0}}
    )
    
    return Order(**order)

@api_router.get("/orders", response_model=List[Order])
async def get_orders(user_id: str = Depends(get_current_user)):
    """Get user's orders"""
    orders = await db.orders.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [Order(**order) for order in orders]

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, user_id: str = Depends(get_current_user)):
    """Get order details"""
    order = await db.orders.find_one({"id": order_id, "user_id": user_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

# ==================== PRESCRIPTION ENDPOINTS ====================

@api_router.post("/prescriptions", response_model=Prescription)
async def upload_prescription(data: PrescriptionUpload, user_id: str = Depends(get_current_user)):
    """Upload prescription"""
    prescription = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "image": data.image,
        "status": "pending",
        "notes": data.notes,
        "created_at": datetime.utcnow()
    }
    
    await db.prescriptions.insert_one(prescription)
    return Prescription(**prescription)

@api_router.get("/prescriptions", response_model=List[Prescription])
async def get_prescriptions(user_id: str = Depends(get_current_user)):
    """Get user's prescriptions"""
    prescriptions = await db.prescriptions.find({"user_id": user_id}).to_list(100)
    return [Prescription(**p) for p in prescriptions]

# ==================== ADMIN ENDPOINTS ====================

@api_router.post("/admin/login")
async def admin_login(credentials: AdminLogin):
    """Admin login"""
    # Simple admin check (in production, use proper auth)
    if credentials.username == "admin" and credentials.password == "admin123":
        token = create_jwt_token("admin")
        return {"token": token, "success": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_orders = await db.orders.count_documents({})
    pending_orders = await db.orders.count_documents({"status": {"$in": ["placed", "confirmed"]}})
    total_users = await db.users.count_documents({})
    low_stock = await db.medicines.count_documents({"stock_quantity": {"$lt": 10}})
    pending_prescriptions = await db.prescriptions.count_documents({"status": "pending"})
    
    # Calculate revenue
    orders = await db.orders.find({"payment_status": {"$in": ["paid", "pending"]}}).to_list(10000)
    total_revenue = sum(order.get("total", 0) for order in orders)
    
    return DashboardStats(
        total_orders=total_orders,
        total_revenue=total_revenue,
        pending_orders=pending_orders,
        total_users=total_users,
        low_stock_medicines=low_stock,
        pending_prescriptions=pending_prescriptions
    )

@api_router.get("/admin/orders", response_model=List[Order])
async def get_all_orders(skip: int = 0, limit: int = 50):
    """Get all orders for admin"""
    orders = await db.orders.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [Order(**order) for order in orders]

@api_router.put("/admin/orders/{order_id}/status")
async def update_order_status(order_id: str, status_data: OrderStatusUpdate):
    """Update order status"""
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": status_data.status, "updated_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Order status updated"}

@api_router.post("/admin/medicines", response_model=Medicine)
async def create_medicine(medicine_data: MedicineCreate):
    """Create new medicine"""
    medicine_id = str(uuid.uuid4())
    final_price = medicine_data.price * (1 - medicine_data.discount / 100)
    
    medicine = {
        "id": medicine_id,
        **medicine_data.dict(),
        "final_price": final_price,
        "rating": 4.5,
        "created_at": datetime.utcnow()
    }
    
    await db.medicines.insert_one(medicine)
    return Medicine(**medicine)

@api_router.put("/admin/medicines/{medicine_id}")
async def update_medicine(medicine_id: str, medicine_data: Dict[str, Any]):
    """Update medicine"""
    if "price" in medicine_data or "discount" in medicine_data:
        medicine = await db.medicines.find_one({"id": medicine_id})
        price = medicine_data.get("price", medicine["price"])
        discount = medicine_data.get("discount", medicine["discount"])
        medicine_data["final_price"] = price * (1 - discount / 100)
    
    await db.medicines.update_one(
        {"id": medicine_id},
        {"$set": medicine_data}
    )
    return {"success": True, "message": "Medicine updated"}

@api_router.delete("/admin/medicines/{medicine_id}")
async def delete_medicine(medicine_id: str):
    """Delete medicine"""
    await db.medicines.delete_one({"id": medicine_id})
    return {"success": True, "message": "Medicine deleted"}

@api_router.get("/admin/prescriptions", response_model=List[Prescription])
async def get_all_prescriptions():
    """Get all prescriptions for admin"""
    prescriptions = await db.prescriptions.find({}).sort("created_at", -1).to_list(100)
    return [Prescription(**p) for p in prescriptions]

@api_router.put("/admin/prescriptions/{prescription_id}")
async def update_prescription(prescription_id: str, data: Dict[str, Any]):
    """Update prescription status"""
    await db.prescriptions.update_one(
        {"id": prescription_id},
        {"$set": data}
    )
    return {"success": True, "message": "Prescription updated"}

# ==================== SEED DATA ENDPOINT ====================

@api_router.post("/seed")
async def seed_database():
    """Seed database with sample medicines"""
    # Clear existing medicines
    await db.medicines.delete_many({})
    
    sample_medicines = [
        {
            "id": str(uuid.uuid4()),
            "name": "Paracetamol 500mg",
            "salt_composition": "Paracetamol",
            "category": "Tablets",
            "price": 20.0,
            "discount": 10,
            "final_price": 18.0,
            "stock_quantity": 500,
            "description": "Used to relieve mild to moderate pain and reduce fever",
            "usage": "Take 1-2 tablets every 4-6 hours as needed. Do not exceed 8 tablets in 24 hours.",
            "manufacturer": "PharmaCo",
            "requires_prescription": False,
            "rating": 4.5,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Calpol 500mg", "price": 22.0},
                {"id": str(uuid.uuid4()), "name": "Dolo 650mg", "price": 25.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dolo 650",
            "salt_composition": "Paracetamol",
            "category": "Tablets",
            "price": 30.0,
            "discount": 5,
            "final_price": 28.5,
            "stock_quantity": 300,
            "description": "Effective for fever and body pain",
            "usage": "Take 1 tablet every 6 hours",
            "manufacturer": "Micro Labs",
            "requires_prescription": False,
            "rating": 4.7,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Paracetamol 500mg", "price": 18.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Amoxicillin 500mg",
            "salt_composition": "Amoxicillin",
            "category": "Antibiotics",
            "price": 150.0,
            "discount": 15,
            "final_price": 127.5,
            "stock_quantity": 200,
            "description": "Antibiotic used to treat bacterial infections",
            "usage": "Take 1 capsule three times daily for 5-7 days",
            "manufacturer": "MedLife",
            "requires_prescription": True,
            "rating": 4.6,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Novamox 500mg", "price": 130.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cetirizine 10mg",
            "salt_composition": "Cetirizine Hydrochloride",
            "category": "Antihistamines",
            "price": 50.0,
            "discount": 20,
            "final_price": 40.0,
            "stock_quantity": 400,
            "description": "Used to relieve allergy symptoms",
            "usage": "Take 1 tablet once daily",
            "manufacturer": "HealthCare Ltd",
            "requires_prescription": False,
            "rating": 4.4,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Zyrtec 10mg", "price": 45.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Vitamin C 500mg",
            "salt_composition": "Ascorbic Acid",
            "category": "Supplements",
            "price": 80.0,
            "discount": 10,
            "final_price": 72.0,
            "stock_quantity": 350,
            "description": "Boosts immunity and overall health",
            "usage": "Take 1 tablet daily",
            "manufacturer": "NutriHealth",
            "requires_prescription": False,
            "rating": 4.8,
            "substitutes": [],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cough Syrup 100ml",
            "salt_composition": "Dextromethorphan",
            "category": "Syrups",
            "price": 120.0,
            "discount": 0,
            "final_price": 120.0,
            "stock_quantity": 150,
            "description": "Relief from cough and cold",
            "usage": "Take 10ml three times daily",
            "manufacturer": "ColdCare",
            "requires_prescription": False,
            "rating": 4.3,
            "substitutes": [],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ibuprofen 400mg",
            "salt_composition": "Ibuprofen",
            "category": "Tablets",
            "price": 45.0,
            "discount": 12,
            "final_price": 39.6,
            "stock_quantity": 280,
            "description": "Pain reliever and anti-inflammatory",
            "usage": "Take 1 tablet every 6-8 hours with food",
            "manufacturer": "PainFree Pharma",
            "requires_prescription": False,
            "rating": 4.5,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Brufen 400mg", "price": 42.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Omeprazole 20mg",
            "salt_composition": "Omeprazole",
            "category": "Tablets",
            "price": 95.0,
            "discount": 8,
            "final_price": 87.4,
            "stock_quantity": 220,
            "description": "Treats acid reflux and heartburn",
            "usage": "Take 1 capsule before breakfast",
            "manufacturer": "DigestWell",
            "requires_prescription": True,
            "rating": 4.6,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Omez 20mg", "price": 90.0}
            ],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Multivitamin Tablets",
            "salt_composition": "Mixed Vitamins & Minerals",
            "category": "Supplements",
            "price": 250.0,
            "discount": 15,
            "final_price": 212.5,
            "stock_quantity": 180,
            "description": "Complete daily nutrition support",
            "usage": "Take 1 tablet daily after meals",
            "manufacturer": "HealthPlus",
            "requires_prescription": False,
            "rating": 4.7,
            "substitutes": [],
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Metformin 500mg",
            "salt_composition": "Metformin Hydrochloride",
            "category": "Tablets",
            "price": 60.0,
            "discount": 10,
            "final_price": 54.0,
            "stock_quantity": 320,
            "description": "Controls blood sugar in diabetes",
            "usage": "Take 1 tablet twice daily with meals",
            "manufacturer": "DiabetCare",
            "requires_prescription": True,
            "rating": 4.5,
            "substitutes": [
                {"id": str(uuid.uuid4()), "name": "Glycomet 500mg", "price": 58.0}
            ],
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.medicines.insert_many(sample_medicines)
    
    return {
        "success": True,
        "message": f"Seeded {len(sample_medicines)} medicines"
    }

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
