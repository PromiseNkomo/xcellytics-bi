from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
from pydantic import BaseModel
import pytz
import io
import pandas as pd


def parse_purchase_date(value):

    try:

        if value and str(value).strip():

            return pd.to_datetime(value)

    except:

        pass

    return now()

DATABASE_URL = "sqlite:///./sales.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def now():
    return datetime.now(
        pytz.timezone("Africa/Johannesburg")
    )


# ================= MODELS =================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True,)

    company_id = Column(Integer)

    name = Column(String)

    price = Column(Float)

    target = Column(Float, default=0)

    # IMPORTANT:
    # Distinguish POS products from manual products
    is_bulk = Column(Boolean, default=False)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)

    company_id = Column(Integer)

    product_id = Column(Integer)

    quantity = Column(Float)

    total_price = Column(Float)

    date = Column(DateTime, default=now)

    # ================= PHASE B =================

    created_date = Column(
        DateTime,
        default=now
    )

    last_modified_date = Column(
        DateTime,
        default=now
    )

    purchase_date = Column(
        DateTime,
        default=now
    )

    # IMPORTANT:
    # Distinguish POS sales from manual sales
    is_bulk = Column(Boolean, default=False)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)

    company_id = Column(Integer)

    amount = Column(Float)

    description = Column(String)

    type = Column(String)

    date = Column(DateTime, default=now)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    username = Column(String)
    password = Column(String)
    role = Column(String)




Base.metadata.create_all(bind=engine)

class CompanyCreate(BaseModel):
    company_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ================= APP =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= DATABASE =================

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


MANAGER_PASSWORD = "1234"


# ================= PRODUCTS =================

@app.get("/products/")
def get_products(db: Session = Depends(get_db)):

    # IMPORTANT:
    # ONLY manual products appear here
    products = db.query(Product).filter(
        Product.is_bulk == False
    ).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price or 0,
            "target": p.target or 0
        }
        for p in products
    ]


@app.post("/products/")
def create_product(
    p: dict,
    db: Session = Depends(get_db)
):

    if p.get("password") != MANAGER_PASSWORD:

        return {
            "error": "Unauthorized"
        }

    obj = Product(
        name=p.get("name"),
        price=safe(p.get("price")),
        target=safe(p.get("target")),
        is_bulk=False
    )

    db.add(obj)

    db.commit()

    db.refresh(obj)

    return {
        "ok": True
    }


@app.put("/products/{id}")
def update_product(
    id: int,
    p: dict,
    db: Session = Depends(get_db)
):

    if p.get("password") != MANAGER_PASSWORD:

        return {
            "error": "Unauthorized"
        }

    product = db.query(Product).filter(
        Product.id == id
    ).first()

    if not product:

        return {
            "error": "Product not found"
        }

    product.name = p.get("name")

    product.price = safe(
        p.get("price")
    )

    product.target = safe(
        p.get("target")
    )

    db.commit()

    return {
        "ok": True
    }


@app.delete("/products/{id}")
def delete_product(
    id: int,
    password: str,
    db: Session = Depends(get_db)
):

    if password != MANAGER_PASSWORD:

        return {
            "error": "Unauthorized"
        }

    obj = db.query(Product).filter(
        Product.id == id
    ).first()

    if obj:

        db.delete(obj)

        db.commit()

    return {
        "ok": True
    }


# ================= SALES =================

@app.get("/sales/")
def get_sales(db: Session = Depends(get_db)):

    # IMPORTANT:
    # ONLY manual sales appear here
    sales = db.query(Sale).filter(
        Sale.is_bulk == False
    ).order_by(
        Sale.date.desc()
    ).all()

    return [
        {
                "id": s.id,
                "product_id": s.product_id,
                "quantity": s.quantity or 0,
                "total_price": s.total_price or 0,
                "date": str(s.date),

                "created_date":
                str(s.created_date),

                "last_modified_date":
                str(s.last_modified_date),

                "purchase_date":
                str(s.purchase_date)
        }
        for s in sales
    ]


@app.post("/sales/")
def create_sale(
    s: dict,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == int(
            s.get("product_id")
        )
    ).first()

    if not product:

        return {
            "error": "Product not found"
        }

    qty = safe(
        s.get("quantity")
    )

    total = qty * (
        product.price or 0
    )

    purchase_date = parse_purchase_date(
        s.get("purchase_date")
    )

    sale = Sale(
        product_id=product.id,
        quantity=qty,
        total_price=total,

        date=now(),

        created_date=now(),

        last_modified_date=now(),

        purchase_date=purchase_date,

        is_bulk=False
    )

    db.add(sale)

    db.commit()

    return {
        "ok": True
    }


@app.put("/sales/{id}")
def update_sale(
    id: int,
    s: dict,
    db: Session = Depends(get_db)
):

    sale = db.query(Sale).filter(
        Sale.id == id
    ).first()

    if not sale:

        return {
            "error": "Sale not found"
        }

    product = db.query(Product).filter(
        Product.id == int(
            s.get("product_id")
        )
    ).first()

    if not product:

        return {
            "error": "Product not found"
        }

    qty = safe(
        s.get("quantity")
    )

    sale.product_id = product.id

    sale.quantity = qty

    sale.total_price = qty * (
    product.price or 0
    )

    if s.get("purchase_date"):

        sale.purchase_date = (
            parse_purchase_date(
                s.get("purchase_date")
            )
        )

    sale.last_modified_date = now()

    db.commit()

    return {
        "ok": True
    }


@app.delete("/sales/{id}")
def delete_sale(
    id: int,
    db: Session = Depends(get_db)
):

    obj = db.query(Sale).filter(
        Sale.id == id
    ).first()

    if obj:

        db.delete(obj)

        db.commit()

    return {
        "ok": True
    }


# ================= EXPENSES =================

@app.get("/expenses/")
def get_expenses(
    db: Session = Depends(get_db)
):

    expenses = db.query(Expense).order_by(
        Expense.date.desc()
    ).all()

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
def create_expense(
    e: dict,
    db: Session = Depends(get_db)
):

    if e.get("type") == "confidential":

        if e.get("password") != MANAGER_PASSWORD:

            return {
                "error": "Unauthorized"
            }

    obj = Expense(
        amount=safe(
            e.get("amount")
        ),
        description=e.get("description"),
        type=e.get(
            "type",
            "general"
        ),
        date=now()
    )

    db.add(obj)

    db.commit()

    return {
        "ok": True
    }


@app.delete("/expenses/{id}")
def delete_expense(
    id: int,
    db: Session = Depends(get_db)
):

    obj = db.query(Expense).filter(
        Expense.id == id
    ).first()

    if obj:

        db.delete(obj)

        db.commit()

    return {
        "ok": True
    }

# ================= Registration API =============

@app.post("/register")
def register(company: CompanyCreate, db: Session = Depends(get_db)):

    existing = db.query(Company).filter(
        Company.email == company.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_company = Company(
        company_name=company.company_name,
        email=company.email,
        password=company.password
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    print("===== COMPANY CREATED =====")
    print(new_company.id)
    print(new_company.company_name)
    print(new_company.email)
    print(new_company.password)

    manager = User(
        company_id=new_company.id,
        username="Manager",
        password=company.password,
        role="manager"
    )

    db.add(manager)
    db.commit()
    print("Company Registered:", new_company.email)

    return {
        "message":"Company Created"
    }

# ===========LogIn API ===========

@app.post("/login")
def login(user: LoginRequest,
          db: Session = Depends(get_db)):
    
    print("Trying login...")
    print(user.email)
    print(user.password)
    
    company = db.query(Company).filter(
        Company.email == user.email,
        Company.password == user.password
    ).first()
    
    print(company)
    
    if not company:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )

    return {
        "company_id": company.id,
        "company_name": company.company_name,
        "role":"manager"
    }

# ================= BULK UPLOAD =================

@app.post("/bulk-upload/")
async def bulk_upload(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

        filename = file.filename.lower()

        content = await file.read()

        # ================= READ FILE =================

        if filename.endswith(".csv"):

            decoded = content.decode("utf-8")

            df = pd.read_csv(
                io.StringIO(decoded)
            )

        elif filename.endswith(".xlsx"):

            df = pd.read_excel(
                io.BytesIO(content)
            )

        else:

            return {
                "error":
                "Only CSV and XLSX files supported"
            }

        # ================= NORMALIZE COLUMNS =================

        df.columns = [
            c.lower().strip()
            for c in df.columns
        ]

        # ================= VALIDATION =================

        if "product" not in df.columns:

            return {
                "error":
                "Missing 'product' column"
            }

        if "quantity" not in df.columns:

            return {
                "error":
                "Missing 'quantity' column"
            }

        grouped = {}
        
        daily_revenue = {}

        uploaded_sales = []
        
        sales_created = 0

        skipped = 0

        auto_created_products = 0

        # ================= PROCESS ROWS =================

        for _, row in df.iterrows():

            product_name = str(
                row.get("product", "")
            ).strip()

            quantity = safe(
                row.get("quantity", 0)
            )

            uploaded_price = safe(
                row.get("price", 0)
            )

            uploaded_date = row.get("date")

            # ================= VALIDATE =================

            if not product_name:

                skipped += 1

                continue

            if quantity <= 0:

                skipped += 1

                continue

            # ================= FIND BULK PRODUCT =================

            product = db.query(Product).filter(
                Product.company_id == company_id,
                Product.name.ilike(product_name),
                Product.is_bulk == True
            ).first()

            # ================= AUTO CREATE =================

            if not product:

                product = Product(
                    company_id=company_id,
                    name=product_name,
                    price=uploaded_price,
                    target=0,
                    is_bulk=True
                )

                db.add(product)

                db.commit()

                db.refresh(product)

                auto_created_products += 1

            # ================= UPDATE PRICE =================

            if uploaded_price > 0:

                product.price = uploaded_price

                db.commit()

            # ================= FINAL PRICE =================

            final_price = (
                uploaded_price
                if uploaded_price > 0
                else (product.price or 0)
            )

            total = quantity * final_price

            # ================= DATE =================

            sale_date = now()

            try:

                if uploaded_date and str(
                    uploaded_date
                ).strip():

                    sale_date = pd.to_datetime(
                        uploaded_date
                    )

            except:

                sale_date = now()

            # ================= CREATE BULK SALE =================

            sale = Sale(
                company_id=company_id,
                product_id=product.id,
                quantity=quantity,
                total_price=total,

                date=sale_date,

                created_date=now(),

                last_modified_date=now(),

                purchase_date=sale_date,

                is_bulk=True
            )

            db.add(sale)

            grouped[product_name] = (
                grouped.get(product_name, 0)
                + total
            )

            day = str(sale_date.date())

            daily_revenue[day] = (
                daily_revenue.get(day, 0)
                + total
            )    
            uploaded_sales.append({
                "product": product_name,
                "quantity": quantity,
                "price": final_price,
                "revenue": total,
                "date": str(sale_date.date())
            })
            sales_created += 1

        db.commit()

        return {

            "ok": True,

            "filename": file.filename,

            "sales_created": sales_created,

            "products_auto_created":
            auto_created_products,

            "skipped_rows": skipped,

            "grouped": grouped,
            
            "daily_revenue": daily_revenue,

            "sales": uploaded_sales,
            
            "detected_columns":
            list(df.columns)
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ================= ANALYTICS =================

@app.get("/analytics/")
def analytics(
    company_id: int,
    db: Session = Depends(get_db)
):

    # IMPORTANT:
    # ONLY manual sales for main dashboard
    sales = db.query(Sale).filter(
        Sale.company_id == company_id,
        Sale.is_bulk == False
    ).all()

    expenses = db.query(Expense).filter(
        Expense.company_id == company_id
    ).all()

    products = db.query(Product).filter(
        Product.company_id == company_id,
        Product.is_bulk == False
    ).all()

    revenue = sum(
        float(s.total_price or 0)
        for s in sales
    )

    expense_total = sum(
        float(e.amount or 0)
        for e in expenses
    )

    profit = revenue - expense_total

    product_map = {}

    for s in sales:

        product_map[s.product_id] = (
            product_map.get(
                s.product_id,
                0
            )
            + float(s.total_price or 0)
        )

    performance = []

    for p in products:

        actual = product_map.get(
            p.id,
            0
        )

        target = float(
            p.target or 0
        )

        percent = (
            actual / target * 100
        ) if target > 0 else 0

        status = (
            "green"
            if percent >= 100
            else "yellow"
            if percent >= 70
            else "red"
        )

        performance.append({
            "name": p.name,
            "actual": round(actual, 2),
            "target": round(target, 2),
            "percent": round(percent, 2),
            "status": status
        })

    # ================= DAILY SALES =================

    daily_sales = {}

    for s in sales:

        day = str(
            s.date.date()
        )

        daily_sales[day] = (
            daily_sales.get(day, 0)
            + float(s.total_price or 0)
        )

    graph = []

    for k, v in daily_sales.items():

        graph.append({
            "date": k,
            "sales": round(v, 2)
        })

    return {

        "totals": {
            "revenue": round(revenue, 2),
            "expenses": round(expense_total, 2),
            "profit": round(profit, 2)
        },

        "performance": performance,

        "sales_count": len(sales),

        "expense_count": len(expenses),

        "product_count": len(products),

        "graph": graph
    }