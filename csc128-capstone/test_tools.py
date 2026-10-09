import json
from tools import check_stock, place_order

def test_check_stock():
    assert "10" in check_stock("Croissant")

def test_place_order():
    result = place_order("John", "Croissant", 2)
    assert "Successfully reserved" in result

if __name__ == "__main__":
    test_check_stock()
    test_place_order()
    print("Deterministic tests passed.")