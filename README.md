# cash-register-challenge

I thought this was a fun practice problem because although it's pretty simple, there's a surprising amount of potential complexity. I also found that certain AI LLM models struggled with certain aspects of this problem, so I wanted to make sort of a standardized test to compare LLMs on.

For code that I personally wrote (as a human) to solve this, see `solutions/my_solution.py`

## Problem Requirements

### Structures and Classes

We need some sort of structure to represent a "pile" of cash, which has a combination of various denominations. I would like to force the AI to choose this itself, but I decided to choose this myself to facilitate testing. I went with a dataclass because you can set defaults and avoid having to type every single value every single time. Realistically at some point we're almost definitely going to want to see these as vectors instead, but I didn't want to limit things prematurely. I also didn't want to force a dependency on external packages (like numpy) if I didn't have to.

So I decided to call this dataclass a CashGroup and define it this way:
```
@dataclass
class CashGroup:
    hundred: int = 0
    twenty: int = 0
    ten: int = 0
    five: int = 0
    one: int = 0
    quarter: int = 0
    dime: int = 0
    nickel: int = 0
    penny: int = 0
```

I also wanted a class to represent a cash register. I didn't want to restrict the implementation of the class, so I'm only defining the name and leaving the rest as a stub. However I also need certain functionality for testing, so I'm also going to add stubs for creating a register and getting its inventory.
```
class CashRegister:
    ...

# Creates and returns a CashRegister instance with the desired starting inventory
def make_register(starting_inventory: CashGroup) -> CashRegister:
    ...

# Gets the current inventory from the register given
def get_register_inventory(register: CashRegister) -> CashGroup:
    ...
```

### Desired Behavior

Our primary function that the AI needs to write will be called `check_out_customer`. This should take the cost of the customer's purchase, the payment from the customer, and the cash register instance to use as arguments. This function will return a `CashGroup` instance representing the change returned to the customer and will modify the cash register inventory as appropriate.

#### Negative values
I'm deliberately avoiding the phrase "invalid" inputs because we *do* want to handle the situation where a customer tries to pay without having enough money. But it's unclear what it would mean for there to be negative values in a `CashGroup`, or for the cost to be negative.

Therefore, the function `check_out_customers` should raise an error if the cost, payment, or register inventory are negative. We'll define a specific exception to raise in these cases:

```
class InputNotAllowed(Exception):
    ...
```

#### Transactions unable to be completed
If a transaction is unable to be completed, it should be voided.

Transactions should be voided if the customer payment is not sufficient to cover the cost or exact change is impossible to return. If a transaction is voided, then the payment should be returned to the customer and the register inventory should not change.

If any of the inputs are not allowed, raise the exception and do NOT void the transaction.

#### Decimal places
We want the AI to figure out that it needs to be careful with the floats without being told, so we'll allow our cost input to be in the form of a float. If the cost contains more than two decimal places, it should be rounded to the nearest hundredth using typical rounding rules. For our tests, we're going to convert to integer values of cents in order to ensure our arithmetic is accurate.

## Final problem statement
See `cash_register.pyi` for the full stub functions.
