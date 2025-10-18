# database/init_db.py
import mysql.connector
from config import Config
import os

def init_database():
    """Initialize the database with required tables"""
    
    # First, create database if it doesn't exist
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
        print(f"Database {Config.MYSQL_DATABASE} created or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    cursor.close()
    conn.close()
    
    # Now create tables
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
        
    statements = schema.split(';')
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
                print(f"Executed: {statement[:50]}...")
            except Exception as e:
                print(f"Error executing statement: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialization completed!")

if __name__ == '__main__':
    init_database()