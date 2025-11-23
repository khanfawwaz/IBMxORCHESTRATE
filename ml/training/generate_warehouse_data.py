"""
Generate Synthetic Warehouse/Supermarket Data for ML Training
Creates realistic datasets for:
- Products (500 items across categories)
- Sales history (2.9M records over 2 years)
- Social trends (90 days)
- Supply chain data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
from pathlib import Path
from tqdm import tqdm

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "warehouse"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Product categories for a supermarket warehouse
CATEGORIES = {
    "Fresh Produce": {
        "subcategories": ["Fruits", "Vegetables", "Herbs"],
        "price_range": (1, 15),
        "seasonality": 0.3,
        "perishable": True
    },
    "Dairy & Eggs": {
        "subcategories": ["Milk", "Cheese", "Yogurt", "Eggs"],
        "price_range": (2, 20),
        "seasonality": 0.1,
        "perishable": True
    },
    "Meat & Seafood": {
        "subcategories": ["Beef", "Chicken", "Pork", "Fish"],
        "price_range": (5, 50),
        "seasonality": 0.2,
        "perishable": True
    },
    "Bakery": {
        "subcategories": ["Bread", "Pastries", "Cakes"],
        "price_range": (2, 25),
        "seasonality": 0.15,
        "perishable": True
    },
    "Frozen Foods": {
        "subcategories": ["Frozen Meals", "Ice Cream", "Frozen Vegetables"],
        "price_range": (3, 30),
        "seasonality": 0.25,
        "perishable": False
    },
    "Beverages": {
        "subcategories": ["Soft Drinks", "Juice", "Water", "Coffee", "Tea"],
        "price_range": (1, 20),
        "seasonality": 0.2,
        "perishable": False
    },
    "Snacks & Candy": {
        "subcategories": ["Chips", "Cookies", "Candy", "Nuts"],
        "price_range": (2, 15),
        "seasonality": 0.1,
        "perishable": False
    },
    "Pantry Staples": {
        "subcategories": ["Pasta", "Rice", "Canned Goods", "Oils", "Spices"],
        "price_range": (1, 25),
        "seasonality": 0.05,
        "perishable": False
    },
    "Household": {
        "subcategories": ["Cleaning", "Paper Products", "Laundry"],
        "price_range": (3, 30),
        "seasonality": 0.05,
        "perishable": False
    },
    "Personal Care": {
        "subcategories": ["Toiletries", "Cosmetics", "Hair Care"],
        "price_range": (2, 40),
        "seasonality": 0.1,
        "perishable": False
    }
}

BRANDS = [
    "FreshChoice", "ValueMart", "PremiumSelect", "NaturesBest", "DailyEssentials",
    "GourmetPick", "HealthyHarvest", "QuickBite", "HomeComfort", "PureLife",
    "GoldenFields", "OceanCatch", "MountainFresh", "SunnyGrove", "GreenValley"
]

LOCATIONS = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte"
]

SUPPLIERS = [
    "GlobalFoods Inc", "FreshSupply Co", "MegaDistributors", "RegionalWholesale",
    "DirectFarm Partners", "OceanHarvest Ltd", "CitySuppliers", "NationalFoods Corp",
    "LocalProduce Network", "PremiumImports LLC"
]


def generate_products(num_products: int = 500) -> pd.DataFrame:
    """Generate product catalog"""
    print(f"Generating {num_products} products...")
    
    products = []
    sku_counter = 1
    
    for category, cat_info in CATEGORIES.items():
        # Distribute products across categories
        num_in_category = int(num_products * (1 / len(CATEGORIES)))
        
        for _ in range(num_in_category):
            subcategory = random.choice(cat_info["subcategories"])
            brand = random.choice(BRANDS)
            
            # Generate product name
            adjective = random.choice([
                "Premium", "Organic", "Fresh", "Classic", "Deluxe",
                "Natural", "Artisan", "Gourmet", "Traditional", "Special"
            ])
            
            product_name = f"{adjective} {subcategory}"
            
            # Generate price
            min_price, max_price = cat_info["price_range"]
            base_price = round(random.uniform(min_price, max_price), 2)
            
            # Generate SKU
            category_code = ''.join([word[0] for word in category.split()])
            sku = f"WH-{category_code}-{sku_counter:04d}"
            sku_counter += 1
            
            products.append({
                "sku": sku,
                "name": product_name,
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "base_price": base_price,
                "unit": random.choice(["each", "lb", "oz", "pack", "box"]),
                "perishable": cat_info["perishable"],
                "seasonality_factor": cat_info["seasonality"]
            })
    
    df = pd.DataFrame(products)
    output_path = OUTPUT_DIR / "products.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df)} products to {output_path}")
    
    return df


def generate_sales_history(
    products_df: pd.DataFrame,
    days: int = 730,  # 2 years
    records_per_day: int = 4000
) -> pd.DataFrame:
    """Generate historical sales data with realistic patterns"""
    print(f"Generating sales history for {days} days...")
    
    start_date = datetime.now() - timedelta(days=days)
    sales_records = []
    
    # Pre-calculate product popularity scores
    product_popularity = {
        row['sku']: random.uniform(0.1, 1.0)
        for _, row in products_df.iterrows()
    }
    
    for day in tqdm(range(days), desc="Generating sales"):
        current_date = start_date + timedelta(days=day)
        
        # Day of week effect (weekends have more sales)
        dow_multiplier = 1.3 if current_date.weekday() >= 5 else 1.0
        
        # Seasonal effect
        month = current_date.month
        seasonal_multiplier = 1.0
        if month in [11, 12]:  # Holiday season
            seasonal_multiplier = 1.5
        elif month in [6, 7, 8]:  # Summer
            seasonal_multiplier = 1.2
        
        # Number of transactions for this day
        daily_transactions = int(
            records_per_day * dow_multiplier * seasonal_multiplier
        )
        
        for _ in range(daily_transactions):
            # Select random product (weighted by popularity)
            product = products_df.sample(
                n=1,
                weights=products_df['sku'].map(product_popularity)
            ).iloc[0]
            
            # Quantity (with some products selling more)
            if product['perishable']:
                quantity = np.random.poisson(2) + 1
            else:
                quantity = np.random.poisson(3) + 1
            
            # Price with some variation
            price_variation = random.uniform(0.95, 1.05)
            unit_price = round(product['base_price'] * price_variation, 2)
            revenue = round(unit_price * quantity, 2)
            
            # Location
            location = random.choice(LOCATIONS)
            
            # Add timestamp with random hour
            timestamp = current_date + timedelta(
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            
            sales_records.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "sku": product['sku'],
                "product_name": product['name'],
                "category": product['category'],
                "location": location,
                "quantity": quantity,
                "unit_price": unit_price,
                "revenue": revenue
            })
    
    df = pd.DataFrame(sales_records)
    output_path = OUTPUT_DIR / "sales_history.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df)} sales records to {output_path}")
    
    return df


def generate_social_trends(
    products_df: pd.DataFrame,
    days: int = 90
) -> pd.DataFrame:
    """Generate social media trend data"""
    print(f"Generating social trends for {days} days...")
    
    start_date = datetime.now() - timedelta(days=days)
    trends = []
    
    # Select trending products (20% of products)
    trending_products = products_df.sample(n=int(len(products_df) * 0.2))
    
    platforms = ["google_trends", "reddit", "youtube", "twitter", "instagram"]
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        for _, product in trending_products.iterrows():
            # Not all products trend every day
            if random.random() > 0.3:
                continue
            
            for platform in platforms:
                # Not all platforms have data
                if random.random() > 0.4:
                    continue
                
                # Engagement score (0-1)
                base_engagement = random.uniform(0.1, 0.9)
                
                # Add trend (some products become more popular over time)
                trend_factor = 1.0 + (day / days) * random.uniform(-0.5, 0.5)
                engagement = min(1.0, base_engagement * trend_factor)
                
                # Reliability score
                reliability = random.uniform(0.6, 1.0)
                
                trends.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "sku": product['sku'],
                    "product_name": product['name'],
                    "platform": platform,
                    "engagement_score": round(engagement, 3),
                    "reliability_score": round(reliability, 3),
                    "mentions": int(engagement * random.randint(100, 10000)),
                    "sentiment": random.choice(["positive", "neutral", "negative"])
                })
    
    df = pd.DataFrame(trends)
    output_path = OUTPUT_DIR / "social_trends.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df)} social trend records to {output_path}")
    
    return df


def generate_supply_chain(products_df: pd.DataFrame) -> pd.DataFrame:
    """Generate supply chain data"""
    print("Generating supply chain data...")
    
    supply_data = []
    
    for _, product in products_df.iterrows():
        supplier = random.choice(SUPPLIERS)
        
        # Lead time depends on product type
        if product['perishable']:
            lead_time = random.randint(1, 7)  # 1-7 days
        else:
            lead_time = random.randint(7, 30)  # 1-4 weeks
        
        # Current stock level
        stock_level = random.randint(50, 1000)
        
        # Reorder point
        reorder_point = int(stock_level * 0.3)
        
        # Supplier reliability
        reliability = random.uniform(0.7, 1.0)
        
        supply_data.append({
            "sku": product['sku'],
            "product_name": product['name'],
            "supplier": supplier,
            "lead_time_days": lead_time,
            "current_stock": stock_level,
            "reorder_point": reorder_point,
            "supplier_reliability": round(reliability, 2),
            "unit_cost": round(product['base_price'] * 0.6, 2),  # 40% markup
            "minimum_order_quantity": random.choice([10, 25, 50, 100])
        })
    
    df = pd.DataFrame(supply_data)
    output_path = OUTPUT_DIR / "supply_chain.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df)} supply chain records to {output_path}")
    
    return df


def generate_all_data():
    """Generate all datasets"""
    print("=" * 60)
    print("WAREHOUSE DATA GENERATION")
    print("=" * 60)
    
    # Generate products
    products_df = generate_products(num_products=500)
    
    # Generate sales history
    sales_df = generate_sales_history(products_df, days=730, records_per_day=4000)
    
    # Generate social trends
    trends_df = generate_social_trends(products_df, days=90)
    
    # Generate supply chain data
    supply_df = generate_supply_chain(products_df)
    
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files in: {OUTPUT_DIR}")
    print(f"  - products.csv: {len(products_df):,} products")
    print(f"  - sales_history.csv: {len(sales_df):,} sales records")
    print(f"  - social_trends.csv: {len(trends_df):,} trend records")
    print(f"  - supply_chain.csv: {len(supply_df):,} supply records")
    print(f"\nTotal data size: ~{(len(sales_df) * 100 / 1_000_000):.1f} MB")
    
    return products_df, sales_df, trends_df, supply_df


if __name__ == "__main__":
    generate_all_data()
