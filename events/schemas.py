from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EmployeeLoginEvent:
    event_type: str = "EMPLOYEE_LOGIN"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    timestamp: str = None


@dataclass
class EmployeeLogoutEvent:
    event_type: str = "EMPLOYEE_LOGOUT"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    timestamp: str = None


@dataclass
class SessionTerminatedEvent:
    event_type: str = "SESSION_TERMINATED"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    reason: str = "auto_logout"
    timestamp: str = None


@dataclass
class BasketStartedEvent:
    event_type: str = "basket.started"
    employee_id: int = None
    terminal_id: str = None
    basket_id: str = None
    timestamp: str = None


@dataclass
class ItemAddedEvent:
    event_type: str = "item.added"
    employee_id: int = None
    terminal_id: str = None
    basket_id: str = None
    product_id: int = None
    quantity: int = 1
    timestamp: str = None


@dataclass
class CustomerIdentifiedEvent:
    event_type: str = "customer.identified"
    employee_id: int = None
    terminal_id: str = None
    basket_id: str = None
    customer_id: int = None
    timestamp: str = None


@dataclass
class PaymentCompletedEvent:
    event_type: str = "payment.completed"
    employee_id: int = None
    terminal_id: str = None
    basket_id: str = None
    amount: float = None
    payment_method: str = None
    timestamp: str = None


@dataclass
class FraudAlertEvent:
    event_type: str = "fraud.alert"
    alert_id: str = None
    rule_id: str = None
    severity: str = None
    employee_id: int = None
    terminal_id: str = None
    basket_id: str = None
    details: dict = None
    timestamp: str = None
