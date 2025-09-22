from src.config import get_supabase
from datetime import datetime, timedelta
from collections import Counter

def _sb():
    return get_supabase()

def top_5_selling_products():
    resp = _sb().table("order_items").select("prod_id, quantity").execute()
    counter = Counter()
    for item in resp.data:
        counter[item["prod_id"]] += item["quantity"]
    # Optionally join with product names
    return counter.most_common(5)

def total_revenue_last_month():
    from_date = (datetime.now() - timedelta(days=30)).date().isoformat()
    resp = _sb().table("payments").select("amount, paid_at, status").eq("status", "PAID").gte("paid_at", from_date).execute()
    total = sum([float(p["amount"]) for p in resp.data])
    return total

def total_orders_by_customer():
    resp = _sb().table("orders").select("cust_id").execute()
    counter = Counter()
    for order in resp.data:
        counter[order["cust_id"]] += 1
    return dict(counter)

def customers_with_more_than_2_orders():
    resp = _sb().table("orders").select("cust_id").execute()
    counter = Counter()
    for order in resp.data:
        counter[order["cust_id"]] += 1
    return [cust_id for cust_id, count in counter.items() if count > 2]