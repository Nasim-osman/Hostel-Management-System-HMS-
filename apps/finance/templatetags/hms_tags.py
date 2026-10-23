from django import template

register = template.Library()


@register.filter(name='bd_format')
def bd_format(amount):
    """
    Formats a numeric value using South Asian / Bangladeshi numbering grouping (Lakh, Crore).
    Example:
        120345 -> 1,20,345
        20345  -> 20,345
        1000000 -> 10,00,000
    """
    if amount is None or amount == '':
        return '0'
    try:
        s = str(int(round(float(amount))))
    except (ValueError, TypeError):
        return str(amount)

    is_negative = s.startswith('-')
    if is_negative:
        s = s[1:]

    if len(s) <= 3:
        res = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        res = ','.join(groups) + ',' + last_three

    return f"-{res}" if is_negative else res


@register.filter(name='taka')
def taka(amount):
    """
    Formats amount as Bangladeshi Taka: ৳ 1,20,345
    """
    return f"৳ {bd_format(amount)}"
