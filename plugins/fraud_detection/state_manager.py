import time
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self):
        self.employee_sessions = {}
        self.terminal_states = {}
        self.basket_states = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_expired_state(self):
        """Remove expired state objects"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        now = datetime.now()
        
        # Cleanup employee sessions (8 hours TTL)
        expired_sessions = [
            emp_id for emp_id, session in self.employee_sessions.items()
            if now - session['login_time'] > timedelta(hours=8)
        ]
        for emp_id in expired_sessions:
            del self.employee_sessions[emp_id]
        
        # Cleanup terminal states (8 hours TTL)
        expired_terminals = [
            term_id for term_id, state in self.terminal_states.items()
            if now - state['session_start'] > timedelta(hours=8)
        ]
        for term_id in expired_terminals:
            del self.terminal_states[term_id]
        
        # Cleanup basket states (2 hours TTL)
        expired_baskets = [
            basket_id for basket_id, state in self.basket_states.items()
            if now - state['start_time'] > timedelta(hours=2)
        ]
        for basket_id in expired_baskets:
            del self.basket_states[basket_id]
        
        self.last_cleanup = current_time
        if expired_sessions or expired_terminals or expired_baskets:
            logger.info(f"Cleaned up {len(expired_sessions)} sessions, {len(expired_terminals)} terminals, {len(expired_baskets)} baskets")
    
    def update_employee_session(self, employee_id, terminal_id, event_type, event_data):
        """Update employee session state"""
        self._cleanup_expired_state()
        
        if event_type == "employee.login":
            if employee_id not in self.employee_sessions:
                self.employee_sessions[employee_id] = {
                    'terminal_ids': set(),
                    'login_time': datetime.now(),
                    'active_baskets': set(),
                    'total_payments': 0
                }
            self.employee_sessions[employee_id]['terminal_ids'].add(terminal_id)
        
        elif event_type == "employee.logout":
            if employee_id in self.employee_sessions:
                self.employee_sessions[employee_id]['terminal_ids'].discard(terminal_id)
                if not self.employee_sessions[employee_id]['terminal_ids']:
                    del self.employee_sessions[employee_id]
        
        elif event_type == "payment.completed" and employee_id in self.employee_sessions:
            amount = event_data.get('amount', 0)
            self.employee_sessions[employee_id]['total_payments'] += amount
    
    def update_terminal_state(self, terminal_id, employee_id, event_type):
        """Update terminal state"""
        if event_type == "employee.login":
            self.terminal_states[terminal_id] = {
                'current_employee_id': employee_id,
                'session_start': datetime.now(),
                'basket_count': 0
            }
        elif event_type == "basket.started" and terminal_id in self.terminal_states:
            self.terminal_states[terminal_id]['basket_count'] += 1
        elif event_type == "employee.logout":
            self.terminal_states.pop(terminal_id, None)
    
    def update_basket_state(self, basket_id, employee_id, terminal_id, event_type, event_data):
        """Update basket state"""
        if event_type == "basket.started":
            self.basket_states[basket_id] = {
                'employee_id': employee_id,
                'terminal_id': terminal_id,
                'start_time': datetime.now(),
                'item_count': 0,
                'item_velocity': [],
                'customer_identified': False,
                'payment_amount': 0
            }
            if employee_id in self.employee_sessions:
                self.employee_sessions[employee_id]['active_baskets'].add(basket_id)
        
        elif basket_id in self.basket_states:
            if event_type == "item.added":
                self.basket_states[basket_id]['item_count'] += 1
                self.basket_states[basket_id]['item_velocity'].append(datetime.now())
            elif event_type == "customer.identified":
                self.basket_states[basket_id]['customer_identified'] = True
            elif event_type == "payment.completed":
                self.basket_states[basket_id]['payment_amount'] = event_data.get('amount', 0)
    
    def get_employee_session(self, employee_id):
        """Get employee session state"""
        return self.employee_sessions.get(employee_id)
    
    def get_terminal_state(self, terminal_id):
        """Get terminal state"""
        return self.terminal_states.get(terminal_id)
    
    def get_basket_state(self, basket_id):
        """Get basket state"""
        return self.basket_states.get(basket_id)


# Singleton instance
state_manager = StateManager()