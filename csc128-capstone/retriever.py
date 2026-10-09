def general_faq():
    try:
        with open("bakery_faq.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "FAQ information is currently unavailable."

FAQ_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "general_faq",
        "description": "Retrieve store hours, location, and allergen policies.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}