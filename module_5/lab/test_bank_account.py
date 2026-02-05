"""
Unit tests for BankAccount class following TDD approach.
Tests all core functionality and edge cases.
"""

import pytest
from datetime import datetime
from bank_account import BankAccount, InsufficientFundsError, InvalidAmountError


class TestAccountCreation:
    """Test suite for account creation functionality."""
    
    def test_create_account_with_initial_balance(self):
        """Test creating account with valid initial balance."""
        account = BankAccount("Alice", 1000.0)
        assert account.owner == "Alice"
        assert account.balance == 1000.0
        assert account.account_number is not None
        
    def test_create_account_with_zero_balance(self):
        """Test creating account with zero initial balance."""
        account = BankAccount("Bob", 0.0)
        assert account.balance == 0.0
        
    def test_create_account_generates_unique_account_number(self):
        """Test that each account gets a unique account number."""
        account1 = BankAccount("Alice", 100)
        account2 = BankAccount("Bob", 200)
        assert account1.account_number != account2.account_number
        
    def test_create_account_with_negative_balance_raises_error(self):
        """Test that creating account with negative balance raises error."""
        with pytest.raises(InvalidAmountError):
            BankAccount("Charlie", -100)


class TestDeposit:
    """Test suite for deposit functionality."""
    
    def test_deposit_positive_amount(self):
        """Test depositing a positive amount increases balance."""
        account = BankAccount("Alice", 1000)
        account.deposit(500)
        assert account.balance == 1500
        
    def test_deposit_zero_raises_error(self):
        """Test that depositing zero raises an error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(InvalidAmountError):
            account.deposit(0)
            
    def test_deposit_negative_amount_raises_error(self):
        """Test that depositing negative amount raises error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(InvalidAmountError):
            account.deposit(-100)
            
    def test_deposit_decimal_amount(self):
        """Test depositing decimal amounts."""
        account = BankAccount("Alice", 1000)
        account.deposit(123.45)
        assert account.balance == 1123.45


class TestWithdraw:
    """Test suite for withdrawal functionality."""
    
    def test_withdraw_with_sufficient_balance(self):
        """Test withdrawing with sufficient balance."""
        account = BankAccount("Alice", 1000)
        account.withdraw(300)
        assert account.balance == 700
        
    def test_withdraw_insufficient_balance_raises_error(self):
        """Test withdrawing more than balance raises error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(InsufficientFundsError):
            account.withdraw(1500)
            
    def test_withdraw_exact_balance(self):
        """Test withdrawing exact balance amount."""
        account = BankAccount("Alice", 1000)
        account.withdraw(1000)
        assert account.balance == 0
        
    def test_withdraw_negative_amount_raises_error(self):
        """Test that withdrawing negative amount raises error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(InvalidAmountError):
            account.withdraw(-100)
            
    def test_withdraw_zero_raises_error(self):
        """Test that withdrawing zero raises error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(InvalidAmountError):
            account.withdraw(0)


class TestTransfer:
    """Test suite for transfer functionality."""
    
    def test_transfer_between_accounts(self):
        """Test transferring money between two accounts."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        account1.transfer(account2, 300)
        assert account1.balance == 700
        assert account2.balance == 800
        
    def test_transfer_insufficient_funds_raises_error(self):
        """Test transfer with insufficient funds raises error."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        with pytest.raises(InsufficientFundsError):
            account1.transfer(account2, 1500)
            
    def test_transfer_negative_amount_raises_error(self):
        """Test transfer with negative amount raises error."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        with pytest.raises(InvalidAmountError):
            account1.transfer(account2, -100)
            
    def test_transfer_to_self_raises_error(self):
        """Test that transferring to same account raises error."""
        account = BankAccount("Alice", 1000)
        with pytest.raises(ValueError, match="Cannot transfer to the same account"):
            account.transfer(account, 100)
            
    def test_transfer_zero_amount_raises_error(self):
        """Test transfer with zero amount raises error."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        with pytest.raises(InvalidAmountError):
            account1.transfer(account2, 0)


class TestTransactionHistory:
    """Test suite for transaction history functionality."""
    
    def test_initial_account_has_creation_transaction(self):
        """Test that new account records creation in history."""
        account = BankAccount("Alice", 1000)
        history = account.get_transaction_history()
        assert len(history) == 1
        assert history[0]["type"] == "account_created"
        assert history[0]["amount"] == 1000
        
    def test_deposit_recorded_in_history(self):
        """Test that deposits are recorded in transaction history."""
        account = BankAccount("Alice", 1000)
        account.deposit(500)
        history = account.get_transaction_history()
        assert len(history) == 2
        assert history[1]["type"] == "deposit"
        assert history[1]["amount"] == 500
        assert history[1]["balance_after"] == 1500
        
    def test_withdraw_recorded_in_history(self):
        """Test that withdrawals are recorded in transaction history."""
        account = BankAccount("Alice", 1000)
        account.withdraw(300)
        history = account.get_transaction_history()
        assert len(history) == 2
        assert history[1]["type"] == "withdrawal"
        assert history[1]["amount"] == 300
        assert history[1]["balance_after"] == 700
        
    def test_transfer_recorded_in_both_accounts(self):
        """Test that transfers are recorded in both accounts."""
        account1 = BankAccount("Alice", 1000)
        account2 = BankAccount("Bob", 500)
        account1.transfer(account2, 200)
        
        history1 = account1.get_transaction_history()
        history2 = account2.get_transaction_history()
        
        # Check sender's history
        assert history1[-1]["type"] == "transfer_out"
        assert history1[-1]["amount"] == 200
        assert history1[-1]["to_account"] == account2.account_number
        
        # Check receiver's history
        assert history2[-1]["type"] == "transfer_in"
        assert history2[-1]["amount"] == 200
        assert history2[-1]["from_account"] == account1.account_number
        
    def test_transaction_history_has_timestamps(self):
        """Test that all transactions have timestamps."""
        account = BankAccount("Alice", 1000)
        account.deposit(500)
        history = account.get_transaction_history()
        for transaction in history:
            assert "timestamp" in transaction
            assert isinstance(transaction["timestamp"], datetime)


class TestInterestCalculation:
    """Test suite for monthly interest calculation."""
    
    def test_calculate_monthly_interest_basic(self):
        """Test basic monthly interest calculation."""
        account = BankAccount("Alice", 1000, interest_rate=0.05)  # 5% annual
        account.apply_monthly_interest()
        # Monthly rate = 5% / 12 = 0.4167%
        # Interest = 1000 * 0.05 / 12 = 4.17 (rounded)
        expected_balance = 1000 + (1000 * 0.05 / 12)
        assert abs(account.balance - expected_balance) < 0.01
        
    def test_interest_with_zero_balance(self):
        """Test interest calculation on zero balance."""
        account = BankAccount("Alice", 0, interest_rate=0.05)
        account.apply_monthly_interest()
        assert account.balance == 0
        
    def test_interest_with_zero_rate(self):
        """Test interest calculation with zero interest rate."""
        account = BankAccount("Alice", 1000, interest_rate=0.0)
        account.apply_monthly_interest()
        assert account.balance == 1000
        
    def test_interest_recorded_in_history(self):
        """Test that interest is recorded in transaction history."""
        account = BankAccount("Alice", 1000, interest_rate=0.05)
        account.apply_monthly_interest()
        history = account.get_transaction_history()
        assert history[-1]["type"] == "interest"
        assert "amount" in history[-1]
        assert history[-1]["amount"] > 0
        
    def test_multiple_interest_applications(self):
        """Test applying interest multiple times compounds correctly."""
        account = BankAccount("Alice", 1000, interest_rate=0.12)  # 12% annual
        initial_balance = account.balance
        account.apply_monthly_interest()
        balance_after_1_month = account.balance
        account.apply_monthly_interest()
        balance_after_2_months = account.balance
        
        # Second month interest should be calculated on new balance
        assert balance_after_2_months > balance_after_1_month
        assert balance_after_1_month > initial_balance


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    def test_very_large_balance(self):
        """Test handling very large balance amounts."""
        account = BankAccount("Alice", 999999999.99)
        account.deposit(0.01)
        assert account.balance == 1000000000.00
        
    def test_very_small_decimal_amounts(self):
        """Test handling very small decimal amounts."""
        account = BankAccount("Alice", 100)
        account.deposit(0.01)
        assert account.balance == 100.01
        
    def test_multiple_operations_maintain_accuracy(self):
        """Test that multiple operations maintain decimal accuracy."""
        account = BankAccount("Alice", 100.00)
        account.deposit(0.10)
        account.deposit(0.20)
        account.withdraw(0.15)
        assert abs(account.balance - 100.15) < 0.001
        
    def test_get_balance_does_not_modify_balance(self):
        """Test that getting balance doesn't modify it."""
        account = BankAccount("Alice", 1000)
        balance1 = account.balance
        balance2 = account.balance
        assert balance1 == balance2 == 1000
        
    def test_transaction_history_is_immutable(self):
        """Test that returned transaction history cannot modify internal state."""
        account = BankAccount("Alice", 1000)
        history = account.get_transaction_history()
        original_length = len(history)
        history.append({"fake": "transaction"})
        
        # Get history again and verify it wasn't modified
        new_history = account.get_transaction_history()
        assert len(new_history) == original_length
