"""
Database Utilities
SQLAlchemy models and database connection management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Base class for models
Base = declarative_base()

# Database path
DB_DIR = Path(__file__).parent.parent.parent / "data" / "databases"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "warehouse.db"

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")


# ============================================================================
# SQLAlchemy Models
# ============================================================================

class Product(Base):
    """Product table"""
    __tablename__ = "products"
    
    sku = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    subcategory = Column(String)
    brand = Column(String)
    base_price = Column(Float)
    unit = Column(String)
    perishable = Column(Boolean, default=False)
    seasonality_factor = Column(Float, default=0.0)


class SalesHistory(Base):
    """Sales history table"""
    __tablename__ = "sales_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
    product_name = Column(String)
    category = Column(String, index=True)
    location = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float)
    revenue = Column(Float)


class SupplyChain(Base):
    """Supply chain table"""
    __tablename__ = "supply_chain"
    
    sku = Column(String, primary_key=True)
    product_name = Column(String)
    supplier = Column(String)
    lead_time_days = Column(Integer)
    current_stock = Column(Integer)
    reorder_point = Column(Integer)
    supplier_reliability = Column(Float)
    unit_cost = Column(Float)
    minimum_order_quantity = Column(Integer)


class SocialTrend(Base):
    """Social trends table"""
    __tablename__ = "social_trends"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
    product_name = Column(String)
    platform = Column(String, index=True)
    engagement_score = Column(Float)
    reliability_score = Column(Float)
    mentions = Column(Integer)
    sentiment = Column(String)


class ForecastCache(Base):
    """Forecast cache table"""
    __tablename__ = "forecast_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    forecast_days = Column(Integer)
    total_predicted_demand = Column(Float)
    trend = Column(String)
    confidence = Column(Float)
    forecast_data = Column(Text)  # JSON string
    created_at = Column(DateTime, nullable=False, index=True)
    expires_at = Column(DateTime)


class AnalysisHistory(Base):
    """Analysis history table"""
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    company_id = Column(String, index=True)
    request_data = Column(Text)  # JSON string
    response_data = Column(Text)  # JSON string
    overall_confidence = Column(Float)
    recommendation = Column(String)
    created_at = Column(DateTime, nullable=False, index=True)
    execution_time = Column(Float)


# ============================================================================
# Database Engine and Session
# ============================================================================

def get_engine():
    """Get database engine with appropriate configuration"""
    if "sqlite" in DATABASE_URL:
        # SQLite-specific configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
    elif "mysql" in DATABASE_URL:
        # MySQL-specific configuration
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,
            connect_args={
                "charset": "utf8mb4",
                "use_unicode": True
            }
        )
    else:
        # PostgreSQL or other databases
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    
    return engine


# Create engine
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at {DB_PATH if 'sqlite' in DATABASE_URL else DATABASE_URL}")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session context manager
    
    Usage:
        with get_db() as db:
            products = db.query(Product).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for FastAPI dependency injection)
    
    Usage:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db_session)):
            return db.query(Product).all()
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let FastAPI handle it


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_csv_to_db(csv_path: Path, table_name: str) -> int:
    """
    Load CSV data into database table
    
    Args:
        csv_path: Path to CSV file
        table_name: Name of table to load into
        
    Returns:
        Number of records loaded
    """
    import pandas as pd
    from datetime import datetime
    
    if not csv_path.exists():
        print(f"⚠ CSV file not found: {csv_path}")
        return 0
    
    df = pd.read_csv(csv_path)
    
    # Convert datetime columns
    datetime_columns = ['timestamp', 'date', 'created_at', 'expires_at']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Load to database
    with get_db() as db:
        # Clear existing data (optional)
        if table_name == "products":
            db.query(Product).delete()
        elif table_name == "sales_history":
            db.query(SalesHistory).delete()
        elif table_name == "supply_chain":
            db.query(SupplyChain).delete()
        elif table_name == "social_trends":
            db.query(SocialTrend).delete()
        
        db.commit()
    
    # Use pandas to_sql for efficient bulk insert
    df.to_sql(
        table_name,
        engine,
        if_exists='append',
        index=False,
        chunksize=1000
    )
    
    print(f"✓ Loaded {len(df):,} records into {table_name}")
    return len(df)


def seed_database():
    """Seed database with generated data"""
    from pathlib import Path
    
    data_dir = Path(__file__).parent.parent.parent / "data" / "warehouse"
    
    print("Seeding database...")
    
    # Load products
    products_path = data_dir / "products.csv"
    if products_path.exists():
        load_csv_to_db(products_path, "products")
    
    # Load sales history
    sales_path = data_dir / "sales_history.csv"
    if sales_path.exists():
        load_csv_to_db(sales_path, "sales_history")
    
    # Load supply chain
    supply_path = data_dir / "supply_chain.csv"
    if supply_path.exists():
        load_csv_to_db(supply_path, "supply_chain")
    
    # Load social trends
    trends_path = data_dir / "social_trends.csv"
    if trends_path.exists():
        load_csv_to_db(trends_path, "social_trends")
    
    print("✓ Database seeding complete")


# ============================================================================
# Query Helpers
# ============================================================================

def get_product_by_sku(db: Session, sku: str) -> Product:
    """Get product by SKU"""
    return db.query(Product).filter(Product.sku == sku).first()


def get_sales_history(
    db: Session,
    sku: str = None,
    location: str = None,
    limit: int = 1000
) -> list:
    """Get sales history with optional filters"""
    query = db.query(SalesHistory)
    
    if sku:
        query = query.filter(SalesHistory.sku == sku)
    if location:
        query = query.filter(SalesHistory.location == location)
    
    return query.order_by(SalesHistory.timestamp.desc()).limit(limit).all()


def get_supply_chain_info(db: Session, sku: str) -> SupplyChain:
    """Get supply chain information for SKU"""
    return db.query(SupplyChain).filter(SupplyChain.sku == sku).first()


def get_social_trends(
    db: Session,
    sku: str = None,
    platform: str = None,
    days: int = 30
) -> list:
    """Get recent social trends"""
    from datetime import datetime, timedelta
    
    query = db.query(SocialTrend)
    
    if sku:
        query = query.filter(SocialTrend.sku == sku)
    if platform:
        query = query.filter(SocialTrend.platform == platform)
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    query = query.filter(SocialTrend.date >= cutoff_date)
    
    return query.order_by(SocialTrend.date.desc()).all()


if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Seed with data
    seed_database()
