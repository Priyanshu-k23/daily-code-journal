<!-- daily-code-journal: topic_id=oop-encapsulation -->
# Protect invariants with encapsulation

**Date (IST):** 2026-11-28  
**Category:** Object-Oriented Programming  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

Expose a controlled method instead of changing state from arbitrary callers. Validation at the boundary preserves invariants such as nonnegative balances.

## Practical example

```python
class Wallet:
    def __init__(self, balance=0):
        self._balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    @property
    def balance(self):
        return self._balance

wallet = Wallet(10)
wallet.deposit(5)
print(wallet.balance)
```

## Expected output or usage

```text
15
```

## Time and space complexity

Deposit: O(1) time and O(1) additional space.

## Key learning points

- Encapsulation centralizes data validation.
- Underscore attributes are a convention, not strict access control.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
