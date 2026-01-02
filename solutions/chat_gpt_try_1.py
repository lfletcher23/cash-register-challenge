# Produced by ChatGPT

from dataclasses import dataclass
from typing import Dict

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


# Unrestricted
class CashRegister:
    def __init__(self, inventory: CashGroup):
        self.inventory = inventory


# Creates and returns a CashRegister instance with the desired starting inventory
def make_register(starting_inventory: CashGroup) -> CashRegister:
    _validate_no_negatives(starting_inventory)
    return CashRegister(starting_inventory)


# Gets the current inventory from the register given
def get_register_inventory(register: CashRegister) -> CashGroup:
    return register.inventory


# Triggered if there are negatives in the cost, payment, or register inventory
class InputNotAllowed(Exception):
    pass


def _validate_no_negatives(cash: CashGroup):
    for value in vars(cash).values():
        if value < 0:
            raise InputNotAllowed()


def _cashgroup_to_cents(cash: CashGroup) -> int:
    return (
        cash.hundred * 10000 +
        cash.twenty * 2000 +
        cash.ten * 1000 +
        cash.five * 500 +
        cash.one * 100 +
        cash.quarter * 25 +
        cash.dime * 10 +
        cash.nickel * 5 +
        cash.penny * 1
    )


def _empty_cashgroup() -> CashGroup:
    return CashGroup()


def _denomination_map() -> Dict[str, int]:
    return {
        "hundred": 10000,
        "twenty": 2000,
        "ten": 1000,
        "five": 500,
        "one": 100,
        "quarter": 25,
        "dime": 10,
        "nickel": 5,
        "penny": 1,
    }


# Acts as the "cashier"
def check_out_customer(cost: float, payment: CashGroup, register: CashRegister) -> CashGroup:
    if cost < 0:
        raise InputNotAllowed()

    _validate_no_negatives(payment)
    _validate_no_negatives(register.inventory)

    cost_cents = round(cost * 100)
    payment_cents = _cashgroup_to_cents(payment)

    # Insufficient payment → void
    if payment_cents < cost_cents:
        return payment

    change_needed = payment_cents - cost_cents

    # Temporarily add payment to register
    for k in vars(payment):
        setattr(register.inventory, k, getattr(register.inventory, k) + getattr(payment, k))

    change = _empty_cashgroup()
    denom_map = _denomination_map()

    for denom, value in denom_map.items():
        available = getattr(register.inventory, denom)
        needed = change_needed // value
        to_use = min(available, needed)

        if to_use > 0:
            setattr(change, denom, to_use)
            setattr(register.inventory, denom, available - to_use)
            change_needed -= to_use * value

    # Exact change not possible → void transaction
    if change_needed != 0:
        # Roll back register inventory
        for k in vars(payment):
            setattr(register.inventory, k, getattr(register.inventory, k) - getattr(payment, k))
        return payment

    return change