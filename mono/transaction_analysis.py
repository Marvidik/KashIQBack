from collections import defaultdict
import re

def extract_name_from_narration(narration):
    parts = narration.split('/')
    for part in parts:
        part = part.strip()
        # Assume names are typically two or more words with alphabets
        if len(part.split()) >= 2 and all(p.isalpha() for p in part.split()):
            return part.upper()
    return None


def top_transactions(transactions, count):
    credit_data = defaultdict(lambda: {"total": 0, "times": 0})
    debit_data = defaultdict(lambda: {"total": 0, "times": 0})

    for tx in transactions:
        name = extract_name_from_narration(tx.narration or tx.narration)
        if not name:
            continue
        data = credit_data if tx.type == "credit" else debit_data
        data[name]["total"] += tx.amount
        data[name]["times"] += 1

    top_creditors = sorted(credit_data.items(), key=lambda x: x[1]["total"], reverse=True)[:count]
    top_debtors = sorted(debit_data.items(), key=lambda x: x[1]["total"], reverse=True)[:count]

    return {
        "creditors": [{"name": name, **data} for name, data in top_creditors],
        "debtors": [{"name": name, **data} for name, data in top_debtors],
    }

def calculate_total_credits_and_debits(transactions):
    total_credits = 0
    total_debits = 0
    credit_count = 0
    debit_count = 0

    for tx in transactions:
        if tx.type == "credit":
            total_credits += tx.amount
            credit_count += 1
        elif tx.type == "debit":
            total_debits += tx.amount
            debit_count += 1

    return {
        "total_credits": round(total_credits, 2),
        "credit_transactions": credit_count,
        "total_debits": round(total_debits, 2),
        "debit_transactions": debit_count
    }


def get_monthly_breakdown(transactions):
    result = defaultdict(lambda: {"credit": 0, "debit": 0})

    for tx in transactions:
        if not tx.date:
            continue
        month_key = tx.date.strftime("%Y-%m")
        if tx.type.lower() == "credit":
            result[month_key]["credit"] += tx.amount
        elif tx.type.lower() == "debit":
            result[month_key]["debit"] += tx.amount

    return dict(result)


def get_category_summary(transactions):
    category_summary = defaultdict(float)

    for tx in transactions:
        if tx.type == 'debit':  # Only consider expenses
            category = tx.category if tx.category else 'Uncategorized'
            category_summary[category] += tx.amount

    return dict(category_summary)


def get_top_spending_categories(transactions, top_n=5):
    summary = get_category_summary(transactions)
    sorted_summary = sorted(summary.items(), key=lambda x: x[1], reverse=True)
    return sorted_summary[:top_n]


def detect_recurring_payments(transactions):
    recurring = []

    grouped = defaultdict(list)
    for tx in transactions:
        if tx.type == 'debit':  # Only expenses
            key = (tx.narration.strip().lower(), round(tx.amount, 2))
            grouped[key].append(tx.date)

    for (narration, amount), dates in grouped.items():
        if len(dates) < 2:
            continue

        dates.sort()
        intervals = [
            (dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)
        ]

        if all(25 <= interval <= 35 for interval in intervals):
            recurring.append({
                "narration": narration.title(),
                "amount": amount,
                "interval_days": intervals[0],
                "occurrences": len(dates),
                "last_paid": dates[-1].strftime('%Y-%m-%d')
            })

    return recurring