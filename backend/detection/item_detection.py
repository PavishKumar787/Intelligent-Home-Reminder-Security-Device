REQUIRED_ITEMS = ["phone", "wallet", "bag"]

def check_missing_items(detected_items):
    return [i for i in REQUIRED_ITEMS if i not in detected_items]
