from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Establish the database connection using environment variables
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    sslmode="require"
)

# **1. Financial Data Retrieval & Update**
@app.route('/records/by-year', methods=['GET', 'POST'])
def financial_records():
    if request.method == 'GET':
        try:
            cur = conn.cursor()
            cur.execute("""SELECT 
                                fr."Year", 
                                inc.revenue, inc.cost_of_goods_sold, inc.gross_profit, 
                                inc.total_expenses, inc.earnings_before_tax, inc.taxes, inc.net_profit,
                                bal.cash, bal.debt, bal.equity_capital, 
                                bal.retained_earnings, bal.total_shareholders_equity,
                                cf.net_earnings, cf.cash_from_operations, 
                                cf.investment_in_property_and_equipment, cf.cash_from_investing, 
                                cf.net_cash_change, cf.opening_cash_balance, cf.closing_cash_balance
                            FROM financial_records fr
                            LEFT JOIN incomeStatement inc ON fr."Year" = inc."Year"
                            LEFT JOIN balanceSheet bal ON fr."Year" = bal."Year"
                            LEFT JOIN cashFlowStatement cf ON fr."Year" = cf."Year"
                            ORDER BY fr."Year" ASC;""")
            rows = cur.fetchall()
            cur.close()

            records_list = []
            for row in rows:
                records_list.append({
                    "Year": row[0],
                    "Revenue": row[1],
                    "CostOfGoodsSold": row[2],
                    "GrossProfit": row[3],
                    "TotalExpenses": row[4],
                    "EarningsBeforeTax": row[5],
                    "Taxes": row[6],
                    "NetProfit": row[7],
                    "Cash": row[8],
                    "Debt": row[9],
                    "EquityCapital": row[10],
                    "RetainedEarnings": row[11],
                    "TotalShareholdersEquity": row[12],
                    "NetEarnings": row[13],
                    "CashFromOperations": row[14],
                    "InvestmentInPropertyAndEquipment": row[15],
                    "CashFromInvesting": row[16],
                    "NetCashChange": row[17],
                    "OpeningCashBalance": row[18],
                    "ClosingCashBalance": row[19]
                })
            return jsonify(records_list)
        except Exception as e:
            print("Error in /records/by-year:", e)
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        # Update the financial data
        data = request.get_json()
        year = data.get('Year')
        revenue = data.get('Revenue')
        cost_of_goods_sold = data.get('CostOfGoodsSold')
        gross_profit = data.get('GrossProfit')
        total_expenses = data.get('TotalExpenses')
        earnings_before_tax = data.get('EarningsBeforeTax')
        taxes = data.get('Taxes')
        net_profit = data.get('NetProfit')
        cash = data.get('Cash')
        debt = data.get('Debt')
        equity_capital = data.get('EquityCapital')
        retained_earnings = data.get('RetainedEarnings')
        total_shareholders_equity = data.get('TotalShareholdersEquity')
        net_earnings = data.get('NetEarnings')
        cash_from_operations = data.get('CashFromOperations')
        investment_in_property_and_equipment = data.get('InvestmentInPropertyAndEquipment')
        cash_from_investing = data.get('CashFromInvesting')
        net_cash_change = data.get('NetCashChange')
        opening_cash_balance = data.get('OpeningCashBalance')
        closing_cash_balance = data.get('ClosingCashBalance')

        try:
            cur = conn.cursor()
            cur.execute("""UPDATE financial_records SET
                    revenue = %s, cost_of_goods_sold = %s, gross_profit = %s, total_expenses = %s, 
                    earnings_before_tax = %s, taxes = %s, net_profit = %s,
                    cash = %s, debt = %s, equity_capital = %s, retained_earnings = %s,
                    total_shareholders_equity = %s, net_earnings = %s, cash_from_operations = %s,
                    investment_in_property_and_equipment = %s, cash_from_investing = %s, 
                    net_cash_change = %s, opening_cash_balance = %s, closing_cash_balance = %s
                WHERE "Year" = %s
            """, (revenue, cost_of_goods_sold, gross_profit, total_expenses, earnings_before_tax,
                  taxes, net_profit, cash, debt, equity_capital, retained_earnings, 
                  total_shareholders_equity, net_earnings, cash_from_operations, 
                  investment_in_property_and_equipment, cash_from_investing, net_cash_change,
                  opening_cash_balance, closing_cash_balance, year))
            conn.commit()
            cur.close()
            return jsonify({"message": "Financial record updated successfully"}), 200
        except Exception as e:
            conn.rollback()
            print("Error updating financial record:", e)
            return jsonify({"error": str(e)}), 500


# **2. Retrieve and Update Products Data (Real-time Updates on Purchase)**
@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'GET':
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM product;")
            rows = cur.fetchall()
            cur.close()

            products = []
            for row in rows:
                products.append({
                    "productid": row[0],
                    "productname": row[1],
                    "price": row[2],
                    "quantity": row[3]
                })
            return jsonify(products)
        except Exception as e:
            print("Error in /products (GET):", e)
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        # Add a new product
        data = request.get_json()
        product_name = data.get('productname')
        price = data.get('price')
        quantity = data.get('quantity')

        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO product (productname, price, quantity) VALUES (%s, %s, %s);",
                        (product_name, price, quantity))
            conn.commit()
            cur.close()
            return jsonify({"message": "Product added successfully"}), 201
        except Exception as e:
            conn.rollback()
            print("Error in /products (POST):", e)
            return jsonify({"error": str(e)}), 500


# **3. Sales Data Retrieval & Insertion from Receipt Page**
@app.route('/sales', methods=['GET', 'POST'])
def manage_sales():
    if request.method == 'GET':
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sales;")
            rows = cur.fetchall()
            cur.close()

            sales_data = []
            for row in rows:
                sales_data.append({
                    "saleid": row[0],
                    "customerid": row[1],
                    "employeeid": row[2],
                    "productid": row[3],
                    "sales_date": row[4]
                })
            return jsonify(sales_data)
        except Exception as e:
            print("Error in /sales (GET):", e)
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        # Insert a sale record and decrement the product quantity
        data = request.get_json()
        customer_id = data.get('customerid')
        employee_id = data.get('employeeid')
        product_id = data.get('productid')
        sales_date = data.get('sales_date')
        quantity_sold = data.get('quantity')  # The quantity sold in the sale

        try:
            cur = conn.cursor()

            # Step 1: Check the current product quantity
            cur.execute("SELECT quantity FROM product WHERE productid = %s;", (product_id,))
            current_quantity = cur.fetchone()

            if current_quantity is None:
                cur.close()
                return jsonify({"error": "Product not found"}), 404

            current_quantity = current_quantity[0]

            # Step 2: Check if enough quantity is available
            if current_quantity < quantity_sold:
                cur.close()
                return jsonify({"error": "Not enough stock available"}), 400

            # Step 3: Insert the sale into the sales table
            cur.execute("""INSERT INTO sales (customerid, employeeid, productid, sales_date) 
                           VALUES (%s, %s, %s, %s);""", 
                           (customer_id, employee_id, product_id, sales_date))
            
            # Step 4: Decrease the product quantity in the product table
            new_quantity = current_quantity - quantity_sold
            cur.execute("UPDATE product SET quantity = %s WHERE productid = %s;", (new_quantity, product_id))

            conn.commit()
            cur.close()
            return jsonify({"message": "Sale recorded successfully, product quantity updated"}), 201
        except Exception as e:
            conn.rollback()
            print("Error inserting sale and updating product quantity:", e)
            return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
