
def identify_report_type(raw_text: str) -> str:
    """Identify report type A or B using weighted feature scoring."""

    print("OCR text received by classifier:")
    print(raw_text[:1000])
    check_a = 0
    check_b = 0

    # Features specific to report A
    features_a = {
        "מקום.ע": 3,
        "הפסקה": 2,
        "100%": 2,
        "125%": 2,
        "150%": 2,
        "שבת": 2,
        "שם החברה": 2
    }

    # Features specific to report B
    features_b = {
        "הערות": 3,
        "עבודה לחודש": 2,
    }

    for feature, points in features_a.items():
        if feature in raw_text:
            check_a += points
            print(f"A found: {feature} (+{points})")

    for feature, points in features_b.items():
        if feature in raw_text:
            check_b += points
            print(f"B found: {feature} (+{points})")

    print(f"CHECK A: {check_a}")
    print(f"CHECK B: {check_b}")

    # Require a meaningful score and a clear winner
    if check_a > check_b:
        return "A"

    if check_b > check_a:
        return "B"

    return "UNKNOWN"

