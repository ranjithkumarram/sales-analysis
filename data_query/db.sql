-- Tech Store Sales Database Schema
-- Created by: Ranjith kumar Ramasamy
-- Purpose: Education Purpose

CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  order_id VARCHAR(50),
  product VARCHAR(100),
  quantity_ordered INT,
  price_each DECIMAL(10,2),
  order_date TIMESTAMP,
  purchase_address TEXT,
  order_city VARCHAR(100),
  order_state VARCHAR(50)
);

-- Insert sample data or use COPY for CSV import
