from typing import Optional, List, Dict
from src.config import get_supabase

def _sb():
    return get_supabase()

def create_customer(name: str, email: str, phone: str, city: str | None = None) -> Optional[Dict]:
    """
    Create a new customer. Email must be unique.
    """
    existing = get_customer_by_email(email)
    if existing:
        raise ValueError(f"Customer with email '{email}' already exists.")

    payload = {"name": name, "email": email, "phone": phone}
    if city:
        payload["city"] = city

    _sb().table("customers").insert(payload).execute()
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_id(cust_id: int) -> Optional[Dict]:
    resp = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_email(email: str) -> Optional[Dict]:
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_customer(cust_id: int, phone: str | None = None, city: str | None = None) -> Optional[Dict]:
    """
    Update a customer's phone or city.
    """
    fields = {}
    if phone:
        fields["phone"] = phone
    if city:
        fields["city"] = city

    if not fields:
        raise ValueError("No fields to update.")

    _sb().table("customers").update(fields).eq("cust_id", cust_id).execute()
    resp = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def delete_customer(cust_id: int) -> Optional[Dict]:
    """
    Delete a customer only if they have no orders.
    """
    orders_resp = _sb().table("orders").select("order_id").eq("customer", cust_id).limit(1).execute()
    if orders_resp.data:
        raise ValueError("Cannot delete customer: existing orders found.")

    resp_before = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    row = resp_before.data[0] if resp_before.data else None

    _sb().table("customers").delete().eq("cust_id", cust_id).execute()
    return row

def list_customers(limit: int = 100) -> List[Dict]:
    resp = _sb().table("customers").select("*").order("cust_id", desc=False).limit(limit).execute()
    return resp.data or []

def search_customers(email: str | None = None, city: str | None = None) -> List[Dict]:
    """
    Search customers by email or city.
    """
    q = _sb().table("customers").select("*")
    if email:
        q = q.eq("email", email)
    if city:
        q = q.eq("city", city)
    resp = q.execute()
    return resp.data or []