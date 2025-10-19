def one_to_19(n):
    return ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"][n]


def tens(n):
    return ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"][n]


def two_digits(n):
    if n < 20:
        return one_to_19(n)
    else:
        t = n // 10
        r = n % 10
        return tens(t) + (" " + one_to_19(r) if r else "")


def three_digits(n):
    h = n // 100
    r = n % 100
    if h and r:
        return one_to_19(h) + " Hundred " + two_digits(r)
    elif h:
        return one_to_19(h) + " Hundred"
    elif r:
        return two_digits(r)
    else:
        return ""


def convert_to_words(n):
    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    hundred = n

    parts = []
    if crore:
        parts.append(three_digits(crore) + " Crore")
    if lakh:
        parts.append(three_digits(lakh) + " Lakh")
    if thousand:
        parts.append(three_digits(thousand) + " Thousand")
    if hundred:
        parts.append(three_digits(hundred))
    return " ".join(parts) if parts else "Zero"


def amount_to_words(amount: str | int | float) -> str:
    if isinstance(amount, str):
        amount = float(amount)

    integer_part = int(amount)
    decimal_part = round((amount - integer_part) * 100)

    words = convert_to_words(integer_part) + " Taka"
    if decimal_part:
        words += " and " + convert_to_words(decimal_part) + " Paisa"
    words += " Only"

    return words
