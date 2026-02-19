# Type annotation stubs that our tests can use

from dataclasses import dataclass

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

class CashRegister:
    ...

# Creates and returns a CashRegister instance with the desired starting inventory
def make_register(starting_inventory: CashGroup) -> CashRegister:
    ...

# Gets the current inventory from the register given
def get_register_inventory(register: CashRegister) -> CashGroup:
    ...

# Triggered if there are negatives in the cost, payment, or register inventory
class InputNotAllowed(Exception):
    ...

# Acts as the "cashier"
# Takes payment and returns the amount to be given as change to the customer
# This will modify the register inventory if appropriate
# If the payment, cost, or starting register inventory have any negatives, raise InputNotAllowed
# If the customer payment is insufficient or exact change is not possible, void the transaction
# If the transaction is voided, return the payment as the "change"
def check_out_customer(cost: float, payment: CashGroup, register: CashRegister) -> CashGroup:
    ...

