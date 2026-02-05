"""
Integration tests for BankAccount system.
Tests realistic scenarios with multiple operations and accounts.
"""

import pytest
from bank_account import BankAccount, InsufficientFundsError, InvalidAmountError


class TestBankingScenarios:
    """Test realistic banking scenarios with multiple operations."""
    
    def test_complete_banking_day_scenario(self):
        """Test a complete day of banking operations."""
        # Create accounts
        alice = BankAccount("Alice", 5000, interest_rate=0.05)
        bob = BankAccount("Bob", 3000, interest_rate=0.05)
        charlie = BankAccount("Charlie", 0, interest_rate=0.05)
        
        # Alice deposits her paycheck
        alice.deposit(2500)
        assert alice.balance == 7500
        
        # Alice pays rent to Bob
        alice.transfer(bob, 1500)
        assert alice.balance == 6000
        assert bob.balance == 4500
        
        # Bob withdraws cash
        bob.withdraw(500)
        assert bob.balance == 4000
        
        # Charlie receives money from both Alice and Bob
        alice.transfer(charlie, 200)
        bob.transfer(charlie, 300)
        assert charlie.balance == 500
        
        # Apply monthly interest to all accounts
        alice.apply_monthly_interest()
        bob.apply_monthly_interest()
        charlie.apply_monthly_interest()
        
        # Verify final balances are reasonable
        assert alice.balance > 5800  # Original 6000 + interest
        assert bob.balance > 3700    # Original 4000 + interest
        assert charlie.balance > 500  # Original 500 + interest
        
    def test_transaction_history_integration(self):
        """Test that transaction history accurately reflects all operations."""
        account = BankAccount("Alice", 1000, interest_rate=0.05)
        
        # Perform multiple operations
        account.deposit(500)
        account.withdraw(200)
        account.deposit(100)
        account.apply_monthly_interest()
        
        history = account.get_transaction_history()
        
        # Verify history contains all transactions in order
        assert len(history) == 5  # creation + 2 deposits + 1 withdrawal + 1 interest
        assert history[0]["type"] == "account_created"
        assert history[1]["type"] == "deposit"
        assert history[2]["type"] == "withdrawal"
        assert history[3]["type"] == "deposit"
        assert history[4]["type"] == "interest"
        
        # Verify final balance matches last transaction
        assert history[-1]["balance_after"] == account.balance
        
    def test_multi_account_transfer_chain(self):
        """Test a chain of transfers across multiple accounts."""
        # Create a chain of accounts
        account1 = BankAccount("Account1", 10000)
        account2 = BankAccount("Account2", 0)
        account3 = BankAccount("Account3", 0)
        account4 = BankAccount("Account4", 0)
        
        # Transfer through the chain
        account1.transfer(account2, 1000)
        account2.transfer(account3, 700)
        account3.transfer(account4, 500)
        
        # Verify final balances
        assert account1.balance == 9000
        assert account2.balance == 300
        assert account3.balance == 200
        assert account4.balance == 500
        
        # Verify total money is conserved
        total = account1.balance + account2.balance + account3.balance + account4.balance
        assert total == 10000
        
    def test_concurrent_operations_maintain_consistency(self):
        """Test that multiple operations maintain balance consistency."""
        account = BankAccount("Alice", 10000)
        
        # Perform many small operations
        for _ in range(10):
            account.deposit(100)
        
        for _ in range(5):
            account.withdraw(50)
        
        # Expected: 10000 + (10 * 100) - (5 * 50) = 10000 + 1000 - 250 = 10750
        assert account.balance == 10750
        
        # Verify transaction count
        history = account.get_transaction_history()
        assert len(history) == 16  # 1 creation + 10 deposits + 5 withdrawals
        
    def test_interest_accumulation_over_multiple_months(self):
        """Test interest calculation over multiple months."""
        account = BankAccount("Alice", 10000, interest_rate=0.12)  # 12% annual = 1% monthly
        
        # Apply interest for 12 months
        balances = [account.balance]
        for _ in range(12):
            account.apply_monthly_interest()
            balances.append(account.balance)
        
        # Verify balance increased each month
        for i in range(len(balances) - 1):
            assert balances[i + 1] > balances[i]
        
        # Verify final balance is approximately correct (compound interest)
        # 10000 * (1 + 0.12/12)^12 ≈ 11268.25
        expected = 10000 * ((1 + 0.12/12) ** 12)
        assert abs(account.balance - expected) < 1.0  # Allow small rounding difference
        
    def test_multiple_transfers_with_insufficient_funds(self):
        """Test behavior when multiple transfers lead to insufficient funds."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 0)
        account3 = BankAccount("Charlie", 0)
        
        # First transfer succeeds
        account1.transfer(account2, 600)
        assert account1.balance == 400
        
        # Second transfer succeeds
        account1.transfer(account3, 300)
        assert account1.balance == 100
        
        # Third transfer fails - insufficient funds
        with pytest.raises(InsufficientFundsError):
            account1.transfer(account2, 200)
        
        # Verify balances unchanged after failed transfer
        assert account1.balance == 100
        assert account2.balance == 600
        assert account3.balance == 300


class TestErrorRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_failed_operation_does_not_affect_balance(self):
        """Test that failed operations don't modify account balance."""
        account = BankAccount("Alice", 1000)
        
        # Attempt invalid withdrawal
        with pytest.raises(InvalidAmountError):
            account.withdraw(-100)
        
        assert account.balance == 1000  # Balance unchanged
        
        # Attempt withdrawal with insufficient funds
        with pytest.raises(InsufficientFundsError):
            account.withdraw(2000)
        
        assert account.balance == 1000  # Balance still unchanged
        
    def test_failed_transfer_does_not_affect_either_account(self):
        """Test that failed transfers don't modify either account."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        
        # Attempt transfer with insufficient funds
        with pytest.raises(InsufficientFundsError):
            account1.transfer(account2, 1500)
        
        # Both balances unchanged
        assert account1.balance == 1000
        assert account2.balance == 500
        
    def test_transaction_history_after_failed_operations(self):
        """Test that failed operations are not recorded in history."""
        account = BankAccount("Alice", 1000)
        initial_history_length = len(account.get_transaction_history())
        
        # Attempt failed operations
        with pytest.raises(InvalidAmountError):
            account.deposit(-100)
        
        with pytest.raises(InsufficientFundsError):
            account.withdraw(2000)
        
        # History should not have changed
        assert len(account.get_transaction_history()) == initial_history_length


class TestBusinessRules:
    """Test business logic and rules."""
    
    def test_savings_account_growth_scenario(self):
        """Test a savings account growing over time with deposits and interest."""
        savings = BankAccount("Alice Savings", 0, interest_rate=0.06)  # 6% annual
        
        # Monthly deposits for a year
        monthly_deposit = 500
        for month in range(12):
            savings.deposit(monthly_deposit)
            savings.apply_monthly_interest()
        
        # After 12 months: should have deposits + accumulated interest
        # This is more than just 12 * 500 = 6000 due to interest
        assert savings.balance > 6000
        assert savings.balance < 6500  # Reasonable upper bound
        
    def test_checking_account_typical_usage(self):
        """Test typical checking account usage pattern."""
        checking = BankAccount("Alice Checking", 2000)
        
        # Simulate bills and income
        checking.deposit(3000)      # Paycheck
        checking.withdraw(1200)     # Rent
        checking.withdraw(300)      # Utilities
        checking.withdraw(150)      # Phone
        checking.withdraw(500)      # Groceries
        checking.deposit(50)        # Refund
        
        # Verify final balance
        expected = 2000 + 3000 - 1200 - 300 - 150 - 500 + 50
        assert checking.balance == expected
        
    def test_balance_precision_with_many_operations(self):
        """Test that balance maintains precision after many decimal operations."""
        account = BankAccount("Alice", 1000.00)
        
        # Perform operations with decimal amounts
        for _ in range(100):
            account.deposit(0.01)
        
        for _ in range(50):
            account.withdraw(0.01)
        
        # Expected: 1000.00 + 1.00 - 0.50 = 1000.50
        assert account.balance == 1000.50
        
    def test_account_closure_scenario(self):
        """Test closing an account by withdrawing all funds."""
        account = BankAccount("Alice", 1000)
        
        # Add some transactions
        account.deposit(500)
        account.withdraw(200)
        
        # Close account - withdraw all
        final_balance = account.balance
        account.withdraw(final_balance)
        
        assert account.balance == 0
        
        # Should not be able to withdraw from empty account
        with pytest.raises(InsufficientFundsError):
            account.withdraw(1)


class TestPerformanceAndScale:
    """Test system behavior with large numbers of operations."""
    
    def test_large_number_of_transactions(self):
        """Test account can handle many transactions."""
        account = BankAccount("Alice", 10000)
        
        # Perform 1000 small transactions
        for i in range(500):
            account.deposit(10)
            account.withdraw(5)
        
        # Expected: 10000 + (500 * 10) - (500 * 5) = 10000 + 5000 - 2500 = 12500
        assert account.balance == 12500
        
        # Verify all transactions recorded
        history = account.get_transaction_history()
        assert len(history) == 1001  # 1 creation + 1000 operations
        
    def test_large_balance_operations(self):
        """Test operations with large balances."""
        account = BankAccount("Corporation", 1000000000)  # 1 billion
        
        account.deposit(500000000)  # 500 million
        account.withdraw(300000000)  # 300 million
        
        assert account.balance == 1200000000  # 1.2 billion
        
    def test_high_frequency_transfers(self):
        """Test many transfers between accounts."""
        account1 = BankAccount("Alice", 100000)
        account2 = BankAccount("Bob", 100000)
        
        # Transfer back and forth
        for _ in range(50):
            account1.transfer(account2, 100)
            account2.transfer(account1, 100)
        
        # Balances should return to original
        assert account1.balance == 100000
        assert account2.balance == 100000
