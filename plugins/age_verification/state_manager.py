from datetime import datetime
from .models import AgeVerificationState
import logging

logger = logging.getLogger(__name__)


class AgeVerificationStateManager:
    def __init__(self):
        self._basket_states = {}
    
    def get_basket_state(self, basket_id):
        """Get basket verification state"""
        try:
            state = AgeVerificationState.objects.get(basket_id=basket_id)
            return {
                'basket_id': state.basket_id,
                'requires_verification': state.requires_verification,
                'verification_completed': state.verification_completed,
                'restricted_items': state.restricted_items,
                'verified_at': state.verified_at,
                'verifier_employee_id': state.verifier_employee_id,
                'customer_age': state.customer_age,
                'verification_method': state.verification_method
            }
        except AgeVerificationState.DoesNotExist:
            return None
    
    def create_basket_state(self, basket_id):
        """Create new basket verification state"""
        state, created = AgeVerificationState.objects.get_or_create(
            basket_id=basket_id,
            defaults={'requires_verification': False}
        )
        return state
    
    def update_verification_requirement(self, basket_id, restricted_items):
        """Update basket verification requirements"""
        state, created = AgeVerificationState.objects.get_or_create(
            basket_id=basket_id,
            defaults={'requires_verification': False}
        )
        
        state.requires_verification = len(restricted_items) > 0
        state.restricted_items = restricted_items
        state.save()
        
        logger.info(f"Updated verification requirement for {basket_id}: {state.requires_verification}")
        return state
    
    def complete_verification(self, basket_id, verifier_employee_id, customer_age, verification_method):
        """Mark verification as completed"""
        try:
            state = AgeVerificationState.objects.get(basket_id=basket_id)
            state.verification_completed = True
            state.verified_at = datetime.now()
            state.verifier_employee_id = verifier_employee_id
            state.customer_age = customer_age
            state.verification_method = verification_method
            state.save()
            
            logger.info(f"Verification completed for {basket_id}")
            return state
        except AgeVerificationState.DoesNotExist:
            logger.error(f"No verification state found for basket {basket_id}")
            return None
    
    def clear_basket_state(self, basket_id):
        """Clear basket state after payment completion"""
        try:
            AgeVerificationState.objects.filter(basket_id=basket_id).delete()
            logger.info(f"Cleared verification state for {basket_id}")
        except Exception as e:
            logger.error(f"Failed to clear state for {basket_id}: {e}")
    
    def is_verification_required(self, basket_id):
        """Check if verification is required for basket"""
        state = self.get_basket_state(basket_id)
        return state and state['requires_verification']
    
    def is_verification_completed(self, basket_id):
        """Check if verification is completed for basket"""
        state = self.get_basket_state(basket_id)
        return state and state['verification_completed']


# Singleton instance
state_manager = AgeVerificationStateManager()