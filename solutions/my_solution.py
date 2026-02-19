# This is one attempt to solve the problem written by me, rather than AI

from dataclasses import dataclass
from decimal import Decimal
from math import floor

#####################################
# Starting point
#####################################

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

    def __init__(self, starting_inventory: CashGroup = CashGroup()):
        self.inventory = starting_inventory

# Creates and returns a CashRegister instance with the desired starting inventory
def make_register(starting_inventory: CashGroup) -> CashRegister:
    return CashRegister(starting_inventory)

# Gets the current inventory from the register given
def get_register_inventory(register: CashRegister) -> CashGroup:
    return register.inventory

# I prefer to reassign inventory to a new CashGroup over mutating the current cash group assigned
# I didn't specify this but I don't really want a CashGroup to be mutable itself
def set_register_inventory(register: CashRegister, cash: CashGroup):
    register.inventory = cash

# Triggered if there are negatives in the cost, payment, or register inventory
class InputNotAllowed(Exception):
    pass

#####################################
# Functions for manipulating our cash groups
#####################################

def vector_from_cash_group(c: CashGroup) -> list[int]:
    vector = [c.hundred, c.twenty, c.ten, c.five, c.one, c.quarter, c.dime, c.nickel, c.penny]
    return vector

# FLAG: There's probably a nicer way to write these add and subtract functions...
# But for now, just something that works
# Could convert to vectors first but then we need to deal with making sure everything is indexed properly
# One consideration is allowing flexibility to change the cash group definition vs enforcing it as previously defined

def add_cash_groups(a: CashGroup, b: CashGroup) -> CashGroup:
    vector_a = vector_from_cash_group(a)
    vector_b = vector_from_cash_group(b)
    vector_sum = [x + y for x, y in zip(vector_a, vector_b)]
    sum = CashGroup(*vector_sum)
    return sum

def subtract_cash_groups(a: CashGroup, b: CashGroup) -> CashGroup:
    vector_a = vector_from_cash_group(a)
    vector_b = vector_from_cash_group(b)
    vector_sum = [x - y for x, y in zip(vector_a, vector_b)]
    diff = CashGroup(*vector_sum)
    return diff

# Check if any of the values are negative
def is_non_negative(c: CashGroup) -> bool:
    as_vector = vector_from_cash_group(c)
    has_any_negatives = any(v < 0 for v in as_vector)
    non_negative = not has_any_negatives
    return non_negative

# This could just be a constant but I like having the expression
def cash_group_value_vector_cents() -> list[int]:
    scalars = [100*i for i in (100, 20, 10, 5, 1)] + [25, 10, 5, 1]
    return scalars

# Calculate the value, in cents
def cash_group_value_cents(c: CashGroup) -> int:
    scalars = cash_group_value_vector_cents()
    as_vector = vector_from_cash_group(c)
    total = sum([k*j for k, j in zip(scalars, as_vector)])
    return total


##################################################
# Functions for actually checking out our customer
##################################################

# I left the initial input as a float to test if the AI would identify the potential decimal issue
# But now want to convert it to a decimal and then scale it to an integer
# TODO Should this have some rounding happening? Or does the int conversion handle it?
def dollars_to_cents(dollars: float) -> int:
    as_decimal = Decimal(str(dollars))
    cents = 100 * as_decimal
    return int(cents)

# The returned CashGroup should never have any negative coeffs!
# Inventory vector should have no negative coeffs and we never subtract more than we have
def try_to_get_change(inventory: CashGroup, change_owed_cents: int) -> CashGroup:
    scalars = cash_group_value_vector_cents()
    inventory_vector = vector_from_cash_group(inventory)

    vector_length = len(scalars)

    # This is going to be the change we give, init as 0 for everything
    change_vector = [0 for j in range(vector_length)]

    # Tracks the amount of change still owed (init change owed - value of change vector)
    amount_left = change_owed_cents

    for j in range(vector_length):

        # Highest number of units of denomination with index j we might want
        max_use_of_j = floor(amount_left / scalars[j])

        # Limit by how many are actually available
        actual_use = min(max_use_of_j, inventory_vector[j])

        # Update these
        change_vector[j] = actual_use
        amount_left = amount_left - actual_use * scalars[j]

    # Convert that change vector back into a cash group
    change_as_cash_group = CashGroup(*change_vector)
    return change_as_cash_group

# Acts as the "cashier"
# Takes payment and returns the amount to be given as change to the customer
# This will modify the register inventory if appropriate
# If the payment, cost, or starting register inventory have any negatives, raise InputNotAllowed
# If the customer payment is insufficient or exact change is not possible, void the transaction
# If the transaction is voided, return the payment as the "change"
def check_out_customer(cost: float, payment: CashGroup, register: CashRegister) -> CashGroup:
    register_start = get_register_inventory(register)

    # Did the inputs make sense in the first place?
    non_neg_cost = cost >= 0
    non_neg_register_start = is_non_negative(register_start)
    non_neg_payment = is_non_negative(payment)
    inputs_allowed = non_neg_cost and non_neg_register_start and non_neg_payment

    # Only proceed if inputs are allowed, otherwise raise error
    if inputs_allowed:
        cost_in_cents = dollars_to_cents(cost)
        payment_value = cash_group_value_cents(payment)
        change_owed_in_cents = payment_value - cost_in_cents

        # This is what we'll be returning the the customer at the ened
        # We initiate it as nothing (zero change)
        amount_to_return = CashGroup()

        # Payment was insufficient so we return the entire amount paid
        if change_owed_in_cents < 0:
            print("Transaction voided, payment insufficient")
            amount_to_return = payment

        else:
            # Inventory we have to work with when we get our change
            intermediate_inventory = add_cash_groups(register_start, payment)

            # Attempt to get the change
            # FLAG: We could check if change is needed before attempting to get it
            change = try_to_get_change(intermediate_inventory, change_owed_in_cents)

            # Process transaction if we did the change correctly
            if change_owed_in_cents == cash_group_value_cents(change):

                # Determine amount left that should be in register and set it
                final_inventory = subtract_cash_groups(intermediate_inventory, change)
                set_register_inventory(register, final_inventory)
                amount_to_return = change

            # If change wasn't exact then we had a problem, void transaction
            else:
                print('Transaction voided, unable to get change')
                amount_to_return = payment

        return amount_to_return

    else:
        raise InputNotAllowed

