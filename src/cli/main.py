import argparse
import json
from src.services import product_service, order_service, report_service
from src.dao import product_dao, customer_dao

def cmd_product_add(args):
    try:
        p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
        print("Created product:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_product_list(args):
    ps = product_dao.list_products(limit=100)
    print(json.dumps(ps, indent=2, default=str))

def cmd_customer_add(args):
    try:
        c = customer_dao.create_customer(args.name, args.email, args.phone, args.city)
        print("Created customer:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_update(args):
    if not args.phone and not args.city:
        print("Error: At least one of --phone or --city must be provided.")
        return
    customer = customer_dao.get_customer_by_email(args.email)
    if not customer:
        print(f"Error: No customer found with email '{args.email}'.")
        return
    try:
        updated = customer_dao.update_customer(customer["cust_id"], args.phone, args.city)
        print("Updated customer:")
        print(json.dumps(updated, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_delete(args):
    customer = customer_dao.get_customer_by_email(args.email)
    if not customer:
        print(f"Error: No customer found with email '{args.email}'.")
        return
    try:
        deleted = customer_dao.delete_customer(customer["cust_id"])
        print("Deleted customer:")
        print(json.dumps(deleted, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_list(args):
    results = customer_dao.list_customers(limit=100)
    print(json.dumps(results, indent=2, default=str))

def cmd_customer_search(args):
    results = customer_dao.search_customers(email=args.email, city=args.city)
    print(json.dumps(results, indent=2, default=str))

def cmd_order_create(args):
    items = []
    for item in args.item:
        try:
            pid, qty = item.split(":")
            items.append({"prod_id": int(pid), "quantity": int(qty)})
        except Exception:
            print("Invalid item format:", item)
            return
    try:
        ord = order_service.create_order(args.customer, items)
        print("Order created:")
        print(json.dumps(ord, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_show(args):
    try:
        o = order_service.get_order_details(args.order)
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_cancel(args):
    try:
        o = order_service.cancel_order(args.order)
        print("Order cancelled (updated):")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
def cmd_order_list(args):
    orders = order_service.get_orders_by_customer(args.customer)
    print(json.dumps(orders, indent=2, default=str))

def cmd_order_complete(args):
    try:
        o = order_service.complete_order(args.order)
        print("Order marked as completed:")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_pay(args):
    try:
        o = order_service.process_payment(args.order, args.method)
        print("Payment processed and order completed:")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_top5(args):
    res = report_service.top_5_selling_products()
    print(json.dumps(res, indent=2, default=str))

def cmd_report_revenue(args):
    res = report_service.total_revenue_last_month()
    print("Total revenue in last month:", res)

def cmd_report_orders_by_customer(args):
    res = report_service.total_orders_by_customer()
    print(json.dumps(res, indent=2, default=str))

def cmd_report_big_customers(args):
    res = report_service.customers_with_more_than_2_orders()
    print(json.dumps(res, indent=2, default=str))

def build_parser():
    parser = argparse.ArgumentParser(prog="retail-cli")
    sub = parser.add_subparsers(dest="cmd")

    # product add/list
    p_prod = sub.add_parser("product", help="product commands")
    pprod_sub = p_prod.add_subparsers(dest="action")
    addp = pprod_sub.add_parser("add")
    addp.add_argument("--name", required=True)
    addp.add_argument("--sku", required=True)
    addp.add_argument("--price", type=float, required=True)
    addp.add_argument("--stock", type=int, default=0)
    addp.add_argument("--category", default=None)
    addp.set_defaults(func=cmd_product_add)

    listp = pprod_sub.add_parser("list")
    listp.set_defaults(func=cmd_product_list)

    # customer commands
    pcust = sub.add_parser("customer", help="customer commands")
    pcust_sub = pcust.add_subparsers(dest="action")

    addc = pcust_sub.add_parser("add")
    addc.add_argument("--name", required=True)
    addc.add_argument("--email", required=True)
    addc.add_argument("--phone", required=True)
    addc.add_argument("--city", default=None)
    addc.set_defaults(func=cmd_customer_add)

    updatec = pcust_sub.add_parser("update")
    updatec.add_argument("--email", required=True)
    updatec.add_argument("--phone", required=False)
    updatec.add_argument("--city", required=False)
    updatec.set_defaults(func=cmd_customer_update)

    delc = pcust_sub.add_parser("delete")
    delc.add_argument("--email", required=True)
    delc.set_defaults(func=cmd_customer_delete)

    listc = pcust_sub.add_parser("list")
    listc.set_defaults(func=cmd_customer_list)

    searchc = pcust_sub.add_parser("search")
    searchc.add_argument("--email", required=False)
    searchc.add_argument("--city", required=False)
    searchc.set_defaults(func=cmd_customer_search)

    # order
    porder = sub.add_parser("order", help="order commands")
    porder_sub = porder.add_subparsers(dest="action")

    createo = porder_sub.add_parser("create")
    createo.add_argument("--customer", type=int, required=True)
    createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
    createo.set_defaults(func=cmd_order_create)

    showo = porder_sub.add_parser("show")
    showo.add_argument("--order", type=int, required=True)
    showo.set_defaults(func=cmd_order_show)

    cano = porder_sub.add_parser("cancel")
    cano.add_argument("--order", type=int, required=True)
    cano.set_defaults(func=cmd_order_cancel)

    listc = porder_sub.add_parser("list")
    listc.add_argument("--customer", type=int, required=True)
    listc.set_defaults(func=cmd_order_list)

    completeo = porder_sub.add_parser("complete")
    completeo.add_argument("--order", type=int, required=True)
    completeo.set_defaults(func=cmd_order_complete)

    pay = porder_sub.add_parser("pay")
    pay.add_argument("--order", type=int, required=True)
    pay.add_argument("--method", required=True, choices=["Cash", "Card", "UPI"])
    pay.set_defaults(func=cmd_order_pay)

    preport = sub.add_parser("report", help="reporting commands")
    preport_sub = preport.add_subparsers(dest="action")

    top5 = preport_sub.add_parser("top5")
    top5.set_defaults(func=cmd_report_top5)

    revenue = preport_sub.add_parser("revenue")
    revenue.set_defaults(func=cmd_report_revenue)

    orders = preport_sub.add_parser("orders_by_customer")
    orders.set_defaults(func=cmd_report_orders_by_customer)

    bigcust = preport_sub.add_parser("big_customers")
    bigcust.set_defaults(func=cmd_report_big_customers)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()