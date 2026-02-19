import pytest
from decimal import Decimal
import copy
from cash_register import CashGroup, CashRegister, InputNotAllowed, make_register, get_register_inventory, check_out_customer

#####################################
# General utility functions
#####################################

def vector_from_cash_group(c: CashGroup) -> list[int]:
    vector = [c.hundred, c.twenty, c.ten, c.five, c.one, c.quarter, c.dime, c.nickel, c.penny]
    return vector

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

# Calculate the value, in cents
def cash_group_value_cents(c: CashGroup) -> int:
    scalars = [100*i for i in (100, 20, 10, 5, 1)] + [25, 10, 5, 1]
    as_vector = vector_from_cash_group(c)
    total = sum([k*j for k, j in zip(scalars, as_vector)])
    return total

def dollars_to_cents(dollars: float) -> int:
    as_decimal = Decimal(str(dollars))
    cents = 100 * as_decimal
    return int(cents)

# I think this is giving the desired behavior, but need to check
def cash_groups_are_equal(a: CashGroup, b: CashGroup) -> bool:
    return a == b

#####################################
# Functions for testing
#####################################

# Copy it so we can compare to the original later
# I prefer creating a new instance of a CashGroup to set as a register value over mutating an existing one,
# but I decided to let the AI get credit for this approach anyway
def make_register_from_copy(starting_inventory: CashGroup):
    cash_copy = copy.copy(starting_inventory)
    return make_register(cash_copy)



#####################################
# Generic testing inputs
# Should probably be fixtures???
# Can param these later
#####################################

def generic_inventory() -> CashGroup:
    cash = CashGroup(hundred=0, twenty=5, ten=5, five=10, one=10)
    return cash

def generic_register() -> CashRegister:
    cash = generic_inventory()
    my_register = make_register_from_copy(starting_inventory=cash)
    return my_register

def generic_payment() -> CashGroup:
    payment = CashGroup(twenty=1)
    return payment

# Total value is non-neg but contains neg coeff(s)
def partially_negative_cash_group() -> CashGroup:
    cash = CashGroup(twenty=3, five=-1)
    return cash

# Total value is neg AND contains neg coeff(s)
def all_negative_cash_group() -> CashGroup:
    cash = CashGroup(twenty= -2, five=1)
    return cash

def generic_cost() -> float:
    return 15

#####################################
# ACTUAL TESTS
#####################################

# Test Set 1
# testing the get and make register functions
# get_register_inventory(make_register(x)) = x
def test_make_register():
    desired_starting_inventory = generic_inventory()
    my_register = make_register_from_copy(starting_inventory=desired_starting_inventory)
    assert cash_groups_are_equal(get_register_inventory(register=my_register), desired_starting_inventory)

# Test Set 2
# invalid input cases should raise the corresponding exception
def test_negative_cost():
    my_register = generic_register()
    my_payment = generic_payment()
    my_cost = -1 * generic_cost()
    with pytest.raises(InputNotAllowed):
        check_out_customer(cost=my_cost, payment=my_payment, register=my_register)

def test_negative_payment_1():
    my_register = generic_register()
    my_payment = all_negative_cash_group()
    my_cost = generic_cost()
    with pytest.raises(InputNotAllowed):
        check_out_customer(cost=my_cost, payment=my_payment, register=my_register)

def test_negative_payment_2():
    my_register = generic_register()
    my_payment = partially_negative_cash_group()
    my_cost = generic_cost()
    with pytest.raises(InputNotAllowed):
        check_out_customer(cost=my_cost, payment=my_payment, register=my_register)

# TODO check these
# Could also prohibit make_register from being set with a negative
# But this should raise SOME exception
def test_negative_inventory_1():
    my_payment = generic_payment()
    my_cost = generic_cost()
    with pytest.raises(InputNotAllowed):
        check_out_customer(cost=my_cost, payment=my_payment, register=make_register_from_copy(all_negative_cash_group()))

def test_negative_inventory_2():
    my_payment = generic_payment()
    my_cost = generic_cost()
    with pytest.raises(InputNotAllowed):
        check_out_customer(cost=my_cost, payment=my_payment, register=make_register_from_copy(partially_negative_cash_group()))

# Test Set 3
# Transactions should be voided if payment is insufficient or change is impossible
# If a transaction is voided, then the amount returned to customer = payment
# And the register end balance should be the same as the register start balance

# Function to check if voided correctly
def voided_correctly(payment: CashGroup, register_start: CashGroup, register_end: CashGroup, change: CashGroup) -> bool:
    payment_returned = payment == change
    register_unchanged = register_start == register_end
    voided_correctly = payment_returned and register_unchanged
    return voided_correctly

def test_insufficient_payment():
    register_start = generic_inventory()
    my_register = make_register_from_copy(register_start)
    my_payment = CashGroup(five=2)
    my_cost = 20
    returned_to_customer = check_out_customer(cost=my_cost, payment=my_payment, register=my_register)
    register_end = get_register_inventory(my_register)

    assert voided_correctly(payment=my_payment, register_start=register_start, register_end=register_end, change=returned_to_customer)

def test_change_not_possible():
    register_start = CashGroup(twenty=1, one=3)
    my_register = make_register_from_copy(register_start)
    my_payment = CashGroup(twenty=1)
    my_cost = 10
    returned_to_customer = check_out_customer(cost=my_cost, payment=my_payment, register=my_register)
    register_end = get_register_inventory(my_register)

    assert voided_correctly(payment=my_payment, register_start=register_start, register_end=register_end, change=returned_to_customer)


# Test Set 4
# If the transaction was processed, check that it was done correctly, meaning:
# - amount collected was correct (payment - change)
# - register balance accurately reflects transactions
# - change given was valid/possible

# Helper function for #4
def change_verified(cost: float, payment: CashGroup, register_start: CashGroup, register_end: CashGroup, change: CashGroup) -> bool:

    # Starts as false until confirmed
    change_verified = False

    # Check for unexpected negatives
    valid_problem = is_non_negative(payment) and is_non_negative(register_start) and cost >= 0
    non_negative_outputs = is_non_negative(register_end) and is_non_negative(change)

    if valid_problem and non_negative_outputs:

        # Check that we collected the correct amount overall
        net_collected_in_cents = cash_group_value_cents(register_end) - cash_group_value_cents(register_start)
        cost_in_cents = dollars_to_cents(cost)
        correct_amount_collected = net_collected_in_cents == cost_in_cents

        # Now we basically walk through the transaction to check each component
        if correct_amount_collected:

            # Amount in the register after payment is taken but before change is given
            # Can assume it's non-neg since it's the sum of two non-negs
            register_intermediate = add_cash_groups(register_start, payment)

            # Calculate the expected register end state and check it
            calculated_register_end = subtract_cash_groups(register_intermediate, change)
            register_end_matches = calculated_register_end == register_end

            if register_end_matches:
                change_verified = True
            else:
                print("Transaction values are inconsistent")

        else:
            print("Incorrect amount collected")

    else:
        print("Invalid inputs or outputs")

    return change_verified

def test_acceptable_transaction_1():
    register_start = CashGroup(hundred=0, twenty=5, ten=8, five=12, one=25, quarter=10, dime=10, nickel=10, penny=20)
    register = make_register_from_copy(register_start)
    cost = 13
    payment = CashGroup(twenty=1)
    change = check_out_customer(cost, payment, register)
    register_end = get_register_inventory(register)
    assert change_verified(cost, payment, register_start, register_end, change)

# Test Set 5
# Edge cases to check on
# Floating point issues
# "Extra" payment where change would otherwise not be possible should be allowed

# Able to give customer change out of their own payment, if needed
def test_redundant_overpayment():
    register_start = CashGroup(twenty=10, five=0)
    register = make_register_from_copy(register_start)
    cost = 15
    payment = CashGroup(five=4)
    returned_to_customer = check_out_customer(cost=cost, payment=payment, register=register)
    register_end = get_register_inventory(register)

    expected_change = CashGroup(five=1)
    expected_register_end = CashGroup(twenty=10, five=3)

    assert returned_to_customer == expected_change and register_end == expected_register_end