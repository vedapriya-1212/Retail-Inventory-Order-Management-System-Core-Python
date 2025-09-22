from src.dao import customer_dao, product_dao
from src.config import get_supabase
from datetime import datetime

def _sb():
    return get_supabase()

def create_order(customer_id: int, items: list[dict]) -> dict:
    # Check customer exists
    customer = customer_dao.get_customer_by_id(customer_id)
    if not customer:
        raise ValueError(f"Customer with id {customer_id} does not exist.")

    # Check product stock and calculate total
    total_amount = 0
    product_updates = []
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        if not prod:
            raise ValueError(f"Product id {item['prod_id']} does not exist.")
        if prod["stock"] < item["quantity"]:
            raise ValueError(f"Not enough stock for product {prod['name']} (id {prod['prod_id']}).")
        total_amount += prod["price"] * item["quantity"]
        product_updates.append((prod["prod_id"], prod["stock"] - item["quantity"]))

    # Insert order
    order_payload = {
        "cust_id": customer_id,
        "total_amount": total_amount,
        "status": "PLACED"
    }
    order_resp = _sb().table("orders").insert(order_payload).execute()
    order_id = order_resp.data[0]["order_id"]

    # Insert order items and update product stock
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        _sb().table("order_items").insert({
            "order_id": order_id,
            "prod_id": item["prod_id"],
            "quantity": item["quantity"],
            "price": prod["price"]
        }).execute()
    for prod_id, new_stock in product_updates:
        _sb().table("products").update({"stock": new_stock}).eq("prod_id", prod_id).execute()

    # Insert pending payment
    _sb().table("payments").insert({
        "order_id": order_id,
        "amount": total_amount,
        "status": "PENDING"
    }).execute()

    return get_order_details(order_id)

def process_payment(order_id: int, method: str) -> dict:
    # Mark payment as PAID
    payment = _sb().table("payments").select("*").eq("order_id", order_id).limit(1).execute()
    if not payment.data:
        raise ValueError("Payment record not found for this order.")
    _sb().table("payments").update({
        "status": "PAID",
        "method": method,
        "paid_at": datetime.now().isoformat()
    }).eq("order_id", order_id).execute()
    # Mark order as COMPLETED
    _sb().table("orders").update({"status": "COMPLETED"}).eq("order_id", order_id).execute()
    return get_order_details(order_id)

def get_order_details(order_id: int) -> dict:
    # Fetch order
    order = _sb().table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    if not order.data:
        raise ValueError("Order not found.")
    order = order.data[0]
    # Fetch customer
    customer = customer_dao.get_customer_by_id(order["cust_id"])
    # Fetch order items
    items = _sb().table("order_items").select("*").eq("order_id", order_id).execute().data
    # Fetch product details for each item
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        item["product_info"] = prod
    # Fetch payment
    payment = _sb().table("payments").select("*").eq("order_id", order_id).limit(1).execute()
    payment = payment.data[0] if payment.data else None
    return {
        "order": order,
        "customer": customer,
        "items": items,
        "payment": payment
    }

def get_orders_by_customer(customer_id: int) -> list:
    orders = _sb().table("orders").select("*").eq("cust_id", customer_id).order("order_id", desc=False).execute()
    return orders.data or []

def cancel_order(order_id: int) -> dict:
    # Fetch order
    order = _sb().table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    if not order.data:
        raise ValueError("Order not found.")
    order = order.data[0]
    if order["status"] != "PLACED":
        raise ValueError("Only orders with status 'PLACED' can be cancelled.")

    # Restore stock
    items = _sb().table("order_items").select("*").eq("order_id", order_id).execute().data
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        new_stock = prod["stock"] + item["quantity"]
        _sb().table("products").update({"stock": new_stock}).eq("prod_id", prod["prod_id"]).execute()

    # Update order status
    _sb().table("orders").update({"status": "CANCELLED"}).eq("order_id", order_id).execute()
    # Mark payment as REFUNDED
    _sb().table("payments").update({"status": "REFUNDED"}).eq("order_id", order_id).execute()
    return get_order_details(order_id)

def complete_order(order_id: int) -> dict:
    # Fetch order
    order = _sb().table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    if not order.data:
        raise ValueError("Order not found.")
    order = order.data[0]
    if order["status"] != "PLACED":
        raise ValueError("Only orders with status 'PLACED' can be completed.")

    _sb().table("orders").update({"status": "COMPLETED"}).eq("order_id", order_id).execute()
    return get_order_details(order_id)