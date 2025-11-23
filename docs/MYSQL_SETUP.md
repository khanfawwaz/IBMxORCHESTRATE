# MySQL Setup Guide

## Overview
This guide shows how to configure the Warehouse Forecasting System to use **MySQL** or **MariaDB** instead of SQLite.

## Why MySQL?

**MySQL/MariaDB is recommended for:**
- Production deployments
- High concurrent user loads
- Large datasets (10M+ records)
- Multi-server architectures
- Advanced querying and indexing

**SQLite is fine for:**
- Development and testing
- Single-user applications
- Datasets under 5M records
- Simple deployments

---

## Prerequisites

### Option 1: Install MySQL
```bash
# Windows (using Chocolatey)
choco install mysql

# Or download from: https://dev.mysql.com/downloads/installer/

# Start MySQL service
net start MySQL
```

### Option 2: Install MariaDB (MySQL-compatible)
```bash
# Windows (using Chocolatey)
choco install mariadb

# Or download from: https://mariadb.org/download/

# Start MariaDB service
net start MariaDB
```

### Option 3: Use Docker
```bash
docker run -d \
  --name warehouse-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=warehouse_db \
  -e MYSQL_USER=warehouse_user \
  -e MYSQL_PASSWORD=warehouse_pass \
  -p 3306:3306 \
  mysql:8.0
```

---

## Step 1: Create Database

### Using MySQL Command Line
```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE warehouse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user
CREATE USER 'warehouse_user'@'localhost' IDENTIFIED BY 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON warehouse_db.* TO 'warehouse_user'@'localhost';
FLUSH PRIVILEGES;

# Exit
EXIT;
```

### Using MySQL Workbench
1. Open MySQL Workbench
2. Connect to your MySQL server
3. Click **Create Schema** icon
4. Name: `warehouse_db`
5. Charset: `utf8mb4`
6. Collation: `utf8mb4_unicode_ci`
7. Click **Apply**

---

## Step 2: Install Python MySQL Driver

The system supports two MySQL drivers:

### Option A: PyMySQL (Pure Python - Easier)
```bash
pip install pymysql
```

**Use this connection string in .env:**
```bash
DATABASE_URL="mysql+pymysql://warehouse_user:your_password@localhost:3306/warehouse_db"
```

### Option B: mysqlclient (C-based - Faster)
```bash
# Requires MySQL development libraries
pip install mysqlclient
```

**Use this connection string in .env:**
```bash
DATABASE_URL="mysql+mysqldb://warehouse_user:your_password@localhost:3306/warehouse_db"
```

**Recommended:** Start with PyMySQL for ease of installation, switch to mysqlclient for production performance.

---

## Step 3: Configure .env File

Edit `d:\Projects\WarehouseFUll\.env`:

```bash
# Database Configuration
# Comment out SQLite line:
# DATABASE_URL="sqlite:///./data/databases/warehouse.db"

# Uncomment and configure MySQL:
DATABASE_URL="mysql+pymysql://warehouse_user:your_password@localhost:3306/warehouse_db"

# Optional: MySQL-specific settings
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_USER="warehouse_user"
MYSQL_PASSWORD="your_password"
MYSQL_DATABASE="warehouse_db"
MYSQL_CHARSET="utf8mb4"
```

**Security Note:** Replace `your_password` with a strong password!

---

## Step 4: Initialize Database

Run the setup script to create tables and seed data:

```bash
cd d:\Projects\WarehouseFUll
python setup.py
```

This will:
1. ✅ Connect to MySQL
2. ✅ Create all tables
3. ✅ Generate 2.9M sales records
4. ✅ Load data into MySQL
5. ✅ Train ML models

**Expected time:** 10-15 minutes

---

## Step 5: Verify MySQL Connection

### Test Script
```python
# test_mysql.py
from backend.shared.database import get_db, Product, SalesHistory

# Test connection
with get_db() as db:
    product_count = db.query(Product).count()
    sales_count = db.query(SalesHistory).count()
    
    print(f"✅ Connected to MySQL!")
    print(f"Products: {product_count:,}")
    print(f"Sales Records: {sales_count:,}")
```

Run:
```bash
python test_mysql.py
```

---

## MySQL Configuration Tips

### 1. Optimize for Large Datasets

Add to MySQL config file (`my.ini` or `my.cnf`):

```ini
[mysqld]
# Increase buffer pool (use 70% of available RAM)
innodb_buffer_pool_size = 4G

# Increase max connections
max_connections = 200

# Optimize for InnoDB
innodb_flush_log_at_trx_commit = 2
innodb_log_buffer_size = 16M

# Query cache (MySQL 5.7 and earlier)
query_cache_type = 1
query_cache_size = 256M

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

### 2. Create Indexes for Performance

```sql
-- Add indexes for common queries
USE warehouse_db;

-- Sales history indexes
CREATE INDEX idx_sales_sku ON sales_history(sku);
CREATE INDEX idx_sales_location ON sales_history(location);
CREATE INDEX idx_sales_timestamp ON sales_history(timestamp);
CREATE INDEX idx_sales_sku_location ON sales_history(sku, location);

-- Supply chain indexes
CREATE INDEX idx_supply_sku ON supply_chain(sku);

-- Social trends indexes
CREATE INDEX idx_trends_sku ON social_trends(sku);
CREATE INDEX idx_trends_date ON social_trends(date);
```

### 3. Monitor Performance

```sql
-- Check table sizes
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'warehouse_db'
ORDER BY (data_length + index_length) DESC;

-- Check query performance
SHOW PROCESSLIST;

-- Check slow queries
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
```

---

## Connection String Examples

### Local MySQL
```bash
# Standard connection
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/warehouse_db"

# With specific charset
DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/warehouse_db?charset=utf8mb4"

# With SSL
DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/warehouse_db?ssl=true"
```

### Remote MySQL
```bash
# Remote server
DATABASE_URL="mysql+pymysql://user:pass@192.168.1.100:3306/warehouse_db"

# Cloud MySQL (e.g., AWS RDS)
DATABASE_URL="mysql+pymysql://admin:pass@mydb.abc123.us-east-1.rds.amazonaws.com:3306/warehouse_db"

# Azure MySQL
DATABASE_URL="mysql+pymysql://user@server:pass@server.mysql.database.azure.com:3306/warehouse_db?ssl=true"
```

### Docker MySQL
```bash
# If using Docker Compose
DATABASE_URL="mysql+pymysql://warehouse_user:warehouse_pass@mysql:3306/warehouse_db"
```

---

## Docker Compose with MySQL

Update `docker-compose.yml` to include MySQL:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: warehouse_db
      MYSQL_USER: warehouse_user
      MYSQL_PASSWORD: warehouse_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - warehouse-network

  # Update orchestrator to use MySQL
  unified-orchestrator:
    build:
      context: .
      dockerfile: docker/Dockerfile.orchestrator
    ports:
      - "9000:9000"
    environment:
      - DATABASE_URL=mysql+pymysql://warehouse_user:warehouse_pass@mysql:3306/warehouse_db
    depends_on:
      - mysql
    networks:
      - warehouse-network

volumes:
  mysql_data:

networks:
  warehouse-network:
    driver: bridge
```

---

## Troubleshooting

### Error: "Can't connect to MySQL server"
```bash
# Check if MySQL is running
net start MySQL

# Or for MariaDB
net start MariaDB

# Check port is open
netstat -an | findstr 3306
```

### Error: "Access denied for user"
```sql
-- Reset user permissions
mysql -u root -p

GRANT ALL PRIVILEGES ON warehouse_db.* TO 'warehouse_user'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "No module named 'MySQLdb'"
```bash
# Install the driver
pip install pymysql

# Or
pip install mysqlclient
```

### Error: "Lost connection to MySQL server"
```bash
# Increase timeouts in .env
# Add to DATABASE_URL:
DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/warehouse_db?connect_timeout=60"
```

### Performance is slow
```sql
-- Check if indexes exist
SHOW INDEXES FROM sales_history;

-- Analyze tables
ANALYZE TABLE sales_history;
ANALYZE TABLE supply_chain;

-- Optimize tables
OPTIMIZE TABLE sales_history;
```

---

## Migration from SQLite to MySQL

### Export SQLite Data
```bash
# Install sqlite3 command line tool
# Export to SQL
sqlite3 data/databases/warehouse.db .dump > warehouse_backup.sql
```

### Import to MySQL
```bash
# Clean up SQLite-specific syntax
# Then import
mysql -u warehouse_user -p warehouse_db < warehouse_backup.sql
```

### Or Use Python Script
```python
# migrate_to_mysql.py
from backend.shared.database import get_db, Product, SalesHistory, SupplyChain
import os

# Backup SQLite connection
sqlite_url = "sqlite:///./data/databases/warehouse.db"
mysql_url = "mysql+pymysql://user:pass@localhost:3306/warehouse_db"

# Migration code here...
```

---

## Best Practices

### 1. Security
- ✅ Use strong passwords
- ✅ Create separate users for each application
- ✅ Enable SSL for remote connections
- ✅ Never commit passwords to Git

### 2. Performance
- ✅ Create indexes on frequently queried columns
- ✅ Use connection pooling (already configured)
- ✅ Monitor slow queries
- ✅ Regular OPTIMIZE TABLE

### 3. Backup
```bash
# Daily backup script
mysqldump -u warehouse_user -p warehouse_db > backup_$(date +%Y%m%d).sql

# Automated backup
# Add to Windows Task Scheduler or cron
```

### 4. Monitoring
- ✅ Monitor connection pool usage
- ✅ Track query performance
- ✅ Set up alerts for errors
- ✅ Regular health checks

---

## Comparison: SQLite vs MySQL

| Feature | SQLite | MySQL |
|---------|--------|-------|
| **Setup** | Zero config | Needs server |
| **Performance (writes)** | Good | Excellent |
| **Concurrent users** | Limited | Unlimited |
| **Max DB size** | 281 TB | Unlimited |
| **Transactions** | Yes | Yes |
| **Best for** | Development | Production |

---

## Summary

To use MySQL with this system:

1. ✅ Install MySQL/MariaDB
2. ✅ Create database and user
3. ✅ Install `pymysql` or `mysqlclient`
4. ✅ Update `.env` with MySQL connection string
5. ✅ Run `python setup.py`
6. ✅ Start services with `python start_services.py`

**That's it!** The system will now use MySQL for all database operations.

---

## Need Help?

- **MySQL Docs:** https://dev.mysql.com/doc/
- **MariaDB Docs:** https://mariadb.com/kb/
- **SQLAlchemy MySQL:** https://docs.sqlalchemy.org/en/20/dialects/mysql.html
- **PyMySQL:** https://github.com/PyMySQL/PyMySQL

**Happy forecasting with MySQL! 🚀**
