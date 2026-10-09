INVENTORY = {
    "Croissant": 10,
    "Sourdough Loaf": 5,
    "Blueberry Muffin": 8
}

ORDERS = []

def check_stock(item_name):
    item = item_name.title()
    if item in INVENTORY:
        return f"We have {INVENTORY[item]} {item}(s) in stock."
    return f"We do not carry {item} or it is out of stock."

def place_order(customer_name, item_name, quantity):
    item = item_name.title()
    if item not in INVENTORY:
        return f"{item} is not available."
    if INVENTORY[item] < quantity:
        return f"Only {INVENTORY[item]} {item}(s) left."
    
    INVENTORY[item] -= quantity
    ORDERS.append({"name": customer_name, "item": item, "qty": quantity})
    return f"Successfully reserved {quantity} {item}(s) for {customer_name}."

def cancel_order(customer_name, item_name, quantity):
    item = item_name.title()
    for order in ORDERS:
        if order["name"] == customer_name and order["item"] == item and order["qty"] == quantity:
            ORDERS.remove(order)
            INVENTORY[item] += quantity
            return f"Cancelled order for {quantity} {item}(s) under {customer_name}."
    return f"No matching order found for {customer_name}."

AVAILABLE_TOOLS = {
    "check_stock": check_stock,
    "place_order": place_order,
    "cancel_order": cancel_order
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check the daily inventory for a specific baked good.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string"}
                },
                "required": ["item_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Deduct items from inventory and save a pickup order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string"},
                    "item_name": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["customer_name", "item_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Delete an existing order and return items to inventory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string"},
                    "item_name": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["customer_name", "item_name", "quantity"]
            }
        }
    }
]