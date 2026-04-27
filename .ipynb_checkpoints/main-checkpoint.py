from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
import pytz
import csv
import io

DATABASE_URL = "sqlite:///./sales.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def now():
    return datetime.now(pytz.timezone("Africa/Johannesburg"))

# ---------------- MODELS ----------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    target = Column(Float, default=0)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    quantity = Column(Float)
    total_price = Column(Float)
    date = Column(DateTime, default=now)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    description = Column(String)
    type = Column(String)
    date = Column(DateTime, default=now)

Base.metadata.create_all(bind=engine)

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def safe(v):
    try:
        return float(v)
    except:
        return 0.0

# ---------------- PRODUCTS ----------------
@app.get("/products/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {"id": p.id, "name": p.name, "price": p.price or 0, "target": p.target or 0}
        for p in products
    ]

@app.post("/products/")
def create_product(p: dict, db: Session = Depends(get_db)):
    obj = Product(
        name=p.get("name"),
        price=safe(p.get("price")),
        target=safe(p.get("target"))
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"ok": True}

# ---------------- SALES ----------------
@app.get("/sales/")
def get_sales(db: Session = Depends(get_db)):
    sales = db.query(Sale).all()
    return [
        {
            "id": s.id,
            "product_id": s.product_id,
            "quantity": s.quantity or 0,
            "total_price": s.total_price or 0,
            "date": str(s.date)
        }
        for s in sales
    ]

@app.post("/sales/")
def create_sale(s: dict, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == s.get("product_id")).first()

    if not product:
        return {"error": "Product not found"}

    qty = safe(s.get("quantity"))
    total = qty * (product.price or 0)

    sale = Sale(
        product_id=product.id,
        quantity=qty,
        total_price=total,
        date=now()
    )

    db.add(sale)
    db.commit()
    return {"ok": True}

# ---------------- EXPENSES ----------------
@app.get("/expenses/")
def get_expenses(db: Session = Depends(get_db)):
    expenses = db.query(Expense).all()
    return [
        {
            "id": e.id,
            "amount": e.amount or 0,
            "description": e.description or "",
            "type": e.type or "general",
            "date": str(e.date)
        }
        for e in expenses
    ]

@app.post("/expenses/")
def create_expense(e: dict, db: Session = Depends(get_db)):
    obj = Expense(
        amount=safe(e.get("amount")),
        description=e.get("description"),
        type=e.get("type", "general"),
        date=now()
    )
    db.add(obj)
    db.commit()
    return {"ok": True}

# ---------------- ANALYTICS (FIXED) ----------------
@app.get("/analytics/")
def analytics(db: Session = Depends(get_db)):

    sales = db.query(Sale).all()
    expenses = db.query(Expense).all()
    products = db.query(Product).all()

    # SAFE totals
    revenue = sum(float(s.total_price or 0) for s in sales)
    expense_total = sum(float(e.amount or 0) for e in expenses)
    profit = revenue - expense_total

    # PRODUCT PERFORMANCE
    product_map = {}

    for s in sales:
        product_map[s.product_id] = product_map.get(s.product_id, 0) + float(s.total_price or 0)

    performance = []

    for p in products:
        actual = product_map.get(p.id, 0)
        target = float(p.target or 0)

        percent = (actual / target * 100) if target > 0 else 0

        status = "green" if percent >= 100 else "yellow" if percent >= 70 else "red"

        performance.append({
            "name": p.name,
            "actual": round(actual, 2),
            "target": round(target, 2),
            "percent": round(percent, 2),
            "status": status
        })

    # ALWAYS RETURN VALID DATA
    return {
        "totals": {
            "revenue": round(revenue, 2),
            "expenses": round(expense_total, 2),
            "profit": round(profit, 2)
        },
        "performance": performance
    }