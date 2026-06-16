#!/usr/bin/env python3
import json
import pymysql

# Load database config
with open('db_config.json', 'r') as f:
    db_config = json.load(f)

try:
    # Connect to database
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    cursor = connection.cursor()
    
    # Get all tables
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    print("✅ Database Connection Successful!\n")
    print("Tables in database 'gateway1':")
    print("=" * 50)
    
    for table_info in tables:
        table_name = table_info['Tables_in_gateway1']
        
        # Get column count
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()
        
        print(f"\n📋 {table_name} ({len(columns)} columns)")
        print("-" * 50)
        
        for col in columns:
            col_type = col['Type']
            null_val = col['Null']
            key_val = col['Key']
            extra = col['Extra']
            
            col_info = f"  • {col['Field']}: {col_type}"
            if key_val:
                col_info += f" [{key_val}]"
            if null_val == 'NO':
                col_info += " [NOT NULL]"
            if extra:
                col_info += f" {extra}"
            
            print(col_info)
    
    print("\n" + "=" * 50)
    print(f"\n✅ Total tables: {len(tables)}")
    
    # Verify specific tables exist
    table_names = [t['Tables_in_gateway1'] for t in tables]
    required_tables = ['network_config', 'entity_owner', 'security_server', 'security_service']
    
    print(f"\n✅ Required tables check:")
    for req_table in required_tables:
        status = "✓" if req_table in table_names else "✗"
        print(f"  {status} {req_table}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Database Connection Failed!")
    print(f"Error: {str(e)}")
