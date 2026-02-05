"""
Banking System Implementation
Provides BankAccount class with full transaction management and interest calculation.
"""

from datetime import datetime
from typing import List, Dict
import uuid


class InsufficientFundsError(Exception):
    """Raised when attempting to withdraw or transfer more than available balance."""
    pass


class InvalidAmountError(Exception):
    """Raised when attempting to use an invalid amount (negative or zero)."""
    pass


class BankAccount:
    """
    Represents a bank account with deposit, withdrawal, transfer, and interest functionality.
    
    Attributes:
        owner: Name of the account owner
        balance: Current account balance
        account_number: Unique account identifier
        interest_rate: Annual interest rate (default 0.0)
    """
    
    def __init__(self, owner: str, initial_balance: float, interest_rate: float = 0.0):
        """
        Initialize a new bank account.
        
        Args:
            owner: Name of the account owner
            initial_balance: Starting balance (must be >= 0)
            interest_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
            
        Raises:
            InvalidAmountError: If initial_balance is negative
        """
        if initial_balance < 0:
            raise InvalidAmountError("Initial balance cannot be negative")
            
        self.owner = owner
        self._balance = round(initial_balance, 2)
        self.account_number = str(uuid.uuid4())
        self.interest_rate = interest_rate
        self._transaction_history: List[Dict] = []
        
        # Record account creation
        self._add_transaction({
            "type": "account_created",
            "amount": initial_balance,
            "balance_after": self._balance,
            "timestamp": datetime.now()
        })
    
    @property
    def balance(self) -> float:
        """Get current account balance."""
        return self._balance
    
    def deposit(self, amount: float) -> None:
        """
        Deposit money into the account.
        
        Args:
            amount: Amount to deposit (must be positive)
            
        Raises:
            InvalidAmountError: If amount is <= 0
        """
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
            
        self._balance = round(self._balance + amount, 2)
        
        self._add_transaction({
            "type": "deposit",
            "amount": amount,
            "balance_after": self._balance,
            "timestamp": datetime.now()
        })
    
    def withdraw(self, amount: float) -> None:
        """
        Withdraw money from the account.
        
        Args:
            amount: Amount to withdraw (must be positive)
            
        Raises:
            InvalidAmountError: If amount is <= 0
            InsufficientFundsError: If amount exceeds balance
        """
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
            
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Balance: {self._balance}, Attempted withdrawal: {amount}"
            )
            
        self._balance = round(self._balance - amount, 2)
        
        self._add_transaction({
            "type": "withdrawal",
            "amount": amount,
            "balance_after": self._balance,
            "timestamp": datetime.now()
        })
    
    def transfer(self, to_account: 'BankAccount', amount: float) -> None:
        """
        Transfer money to another account.
        
        Args:
            to_account: Destination BankAccount instance
            amount: Amount to transfer (must be positive)
            
        Raises:
            InvalidAmountError: If amount is <= 0
            InsufficientFundsError: If amount exceeds balance
            ValueError: If attempting to transfer to same account
        """
        if to_account is self or to_account.account_number == self.account_number:
            raise ValueError("Cannot transfer to the same account")
            
        if amount <= 0:
            raise InvalidAmountError("Transfer amount must be positive")
            
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds for transfer. Balance: {self._balance}, Transfer amount: {amount}"
            )
        
        # Deduct from sender
        self._balance = round(self._balance - amount, 2)
        self._add_transaction({
            "type": "transfer_out",
            "amount": amount,
            "to_account": to_account.account_number,
            "balance_after": self._balance,
            "timestamp": datetime.now()
        })
        
        # Add to receiver
        to_account._balance = round(to_account._balance + amount, 2)
        to_account._add_transaction({
            "type": "transfer_in",
            "amount": amount,
            "from_account": self.account_number,
            "balance_after": to_account._balance,
            "timestamp": datetime.now()
        })
    
    def apply_monthly_interest(self) -> None:
        """
        Apply monthly interest to the account balance.
        Interest is calculated as: balance * (annual_rate / 12)
        """
        if self._balance <= 0 or self.interest_rate <= 0:
            return
            
        monthly_rate = self.interest_rate / 12
        interest_amount = round(self._balance * monthly_rate, 2)
        self._balance = round(self._balance + interest_amount, 2)
        
        self._add_transaction({
            "type": "interest",
            "amount": interest_amount,
            "balance_after": self._balance,
            "timestamp": datetime.now()
        })
    
    def get_transaction_history(self) -> List[Dict]:
        """
        Get complete transaction history.
        
        Returns:
            List of transaction dictionaries (copy to prevent external modification)
        """
        # Return a deep copy to prevent external modification
        return [transaction.copy() for transaction in self._transaction_history]
    
    def _add_transaction(self, transaction: Dict) -> None:
        """
        Add a transaction to the history.
        
        Args:
            transaction: Dictionary containing transaction details
        """
        self._transaction_history.append(transaction)
    
    def __str__(self) -> str:
        """String representation of the account."""
        return f"BankAccount(owner='{self.owner}', balance={self._balance}, account_number='{self.account_number}')"
    
    def __repr__(self) -> str:
        """Detailed representation of the account."""
        return (f"BankAccount(owner='{self.owner}', balance={self._balance}, "
                f"account_number='{self.account_number}', interest_rate={self.interest_rate})")
