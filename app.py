from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flashing messages


# Database connection parameters (use environment variables for security)
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "34.101.181.164"),  # Change to your DB host
            database=os.getenv("DB_NAME", "db-magang"),  # Change to your DB name
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "magang"),  # Your PostgreSQL username
            password=os.getenv("DB_PASSWORD", "magangm1d1")  # Your PostgreSQL password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


# Fetch coffee menu items matching a search query
@app.route("/search", methods=["GET"])
def search_items():
    query = request.args.get("query", "")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM public.jadi_kopi_item_ex WHERE name ILIKE %s", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()

    results = [item[0] for item in items]
    return jsonify(results)


# Fetch all coffee items for the form
def get_coffee_menu():
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name, avatar FROM public.jadi_kopi_item_ex")
    items = cursor.fetchall()
    conn.close()
    return items


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        coffee_item = request.form.get("coffee_item")
        sugar = request.form.get("sugar")
        ice = request.form.get("ice")

        # Basic validation
        if not customer_name or not coffee_item:
            flash("Customer name and coffee item are required.", "error")
            return redirect(url_for("index"))

        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate receipt
        receipt = f"""
        ------ Coffee Receipt ------
        Customer: {customer_name}
        Order: {coffee_item}
        Sugar: {sugar}
        Ice: {ice}
        Time: {order_time}
        ----------------------------
        """
        print(receipt)  # Print receipt to the console

        flash("Order submitted successfully!", "success")
        return redirect(url_for("index"))

    # Fetch coffee menu from the database
    coffee_menu = get_coffee_menu()
    return render_template("index.html", coffee_menu=coffee_menu)


if __name__ == "__main__":
    app.run(debug=True)
