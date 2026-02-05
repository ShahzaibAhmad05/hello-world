"""Pattern Library: Error Handlers

Few-shot examples for comprehensive error handling in microservices.
"""

import time
import functools
from typing import Callable, Any, Optional, Dict
import logging
from datetime import datetime, timedelta
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# VALIDATION ERROR HANDLER - Example 1
# ============================================================================

class ValidationError(Exception):
    """Custom validation error exception."""
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        self.message = message
        self.field_errors = field_errors or {}
        super().__init__(self.message)


def validation_error_handler(func: Callable) -> Callable:
    """
    Validation error handler decorator.
    
    Demonstrates: field error extraction, i18n support, user-friendly messages,
    logging, structured responses.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            # Log validation failure for monitoring
            logger.warning(
                f"Validation failed in {func.__name__}: {e.message}",
                extra={'field_errors': e.field_errors}
            )
            
            # Format user-friendly error response
            error_response = {
                'error': 'Validation Error',
                'message': e.message,
                'fields': e.field_errors,
                'suggestions': _generate_suggestions(e.field_errors),
                'timestamp': datetime.utcnow().isoformat(),
                'error_code': 'VALIDATION_ERROR'
            }
            
            return error_response, 400
        
    return wrapper


def _generate_suggestions(field_errors: Dict[str, str]) -> Dict[str, str]:
    """Generate helpful suggestions for fixing validation errors."""
    suggestions = {}
    for field, error in field_errors.items():
        if 'email' in field.lower():
            suggestions[field] = "Use format: user@example.com"
        elif 'password' in field.lower():
            suggestions[field] = "Use 8+ characters with uppercase, lowercase, number, and symbol"
        elif 'phone' in field.lower():
            suggestions[field] = "Use format: +1-555-123-4567"
    return suggestions


# ============================================================================
# DATABASE ERROR HANDLER - Example 2
# ============================================================================

class DatabaseError(Exception):
    """Custom database error exception."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern for database operations."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise DatabaseError("Circuit breaker is OPEN, database unavailable")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED state")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e


def database_error_handler(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    circuit_breaker: Optional[CircuitBreaker] = None
):
    """
    Database error handler with retry logic and circuit breaker.
    
    Demonstrates: connection timeouts, deadlocks, constraint violations,
    exponential backoff, circuit breaker, fallback mechanisms.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # Use circuit breaker if provided
                    if circuit_breaker:
                        return circuit_breaker.call(func, *args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                    
                except ConnectionError as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Database connection failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s...",
                        extra={'error': str(e)}
                    )
                    time.sleep(wait_time)
                    
                except Exception as e:
                    error_type = type(e).__name__
                    
                    # Handle specific database errors
                    if 'deadlock' in str(e).lower():
                        logger.error(f"Database deadlock detected: {str(e)}")
                        # Implement deadlock-specific retry logic
                        time.sleep(0.1 * (attempt + 1))
                        last_exception = e
                    elif 'constraint' in str(e).lower():
                        # Don't retry constraint violations
                        logger.error(f"Database constraint violation: {str(e)}")
                        return {
                            'error': 'Data Integrity Error',
                            'message': 'The operation violates database constraints',
                            'error_code': 'CONSTRAINT_VIOLATION'
                        }, 409
                    else:
                        # Send alert for persistent issues
                        if attempt >= max_retries - 1:
                            _send_alert(f"Persistent database error: {str(e)}")
                        raise e
            
            # All retries exhausted
            logger.error(
                f"Database operation failed after {max_retries} attempts",
                extra={'last_error': str(last_exception)}
            )
            
            # Try fallback mechanism
            fallback_result = _try_fallback(func.__name__, *args, **kwargs)
            if fallback_result is not None:
                return fallback_result
            
            return {
                'error': 'Database Unavailable',
                'message': 'Service temporarily unavailable. Please try again later.',
                'error_code': 'DATABASE_ERROR',
                'retry_after': 60
            }, 503
        
        return wrapper
    return decorator


def _try_fallback(operation_name: str, *args, **kwargs) -> Optional[Any]:
    """Attempt fallback for read operations using cache."""
    if 'get' in operation_name.lower() or 'read' in operation_name.lower():
        logger.info(f"Attempting cache fallback for {operation_name}")
        # Return cached data if available
        # This would integrate with actual cache system
        return None
    return None


def _send_alert(message: str) -> None:
    """Send alert for critical database issues."""
    logger.critical(f"ALERT: {message}")
    # Integrate with alerting system (PagerDuty, Slack, etc.)


# ============================================================================
# EXTERNAL SERVICE ERROR HANDLER - Example 3
# ============================================================================

class ExternalServiceError(Exception):
    """Custom external service error exception."""
    pass


class ServiceHealthMonitor:
    """Monitor external service health and manage failover."""
    
    def __init__(self):
        self.services = {}
        self.failure_counts = {}
        self.last_check = {}
    
    def record_failure(self, service_name: str):
        """Record service failure."""
        self.failure_counts[service_name] = self.failure_counts.get(service_name, 0) + 1
        self.last_check[service_name] = datetime.now()
    
    def is_healthy(self, service_name: str, threshold: int = 5) -> bool:
        """Check if service is healthy."""
        return self.failure_counts.get(service_name, 0) < threshold
    
    def get_backup_service(self, primary: str) -> Optional[str]:
        """Get backup service endpoint."""
        backup_map = {
            'payment_primary': 'payment_backup',
            'email_primary': 'email_backup'
        }
        return backup_map.get(primary)


service_monitor = ServiceHealthMonitor()


def external_service_handler(
    service_name: str,
    timeout: int = 10,
    cache_ttl: int = 300,
    enable_fallback: bool = True
):
    """
    External service error handler with rate limiting, timeouts, caching.
    
    Demonstrates: API rate limiting, timeout handling, service unavailability,
    graceful degradation, fallback providers, health monitoring.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check service health
                if not service_monitor.is_healthy(service_name):
                    logger.warning(f"Service {service_name} marked unhealthy, trying backup")
                    backup = service_monitor.get_backup_service(service_name)
                    if backup and enable_fallback:
                        kwargs['service_endpoint'] = backup
                
                # Execute with timeout
                result = func(*args, **kwargs, timeout=timeout)
                
                # Cache successful responses
                # _cache_response(func.__name__, args, result, cache_ttl)
                
                return result
                
            except Timeout:
                logger.error(f"Timeout calling {service_name}")
                service_monitor.record_failure(service_name)
                
                # Try cached response
                # cached = _get_cached_response(func.__name__, args)
                # if cached:
                #     logger.info("Returning cached response due to timeout")
                #     return cached
                
                return {
                    'error': 'Service Timeout',
                    'message': f'{service_name} did not respond in time',
                    'error_code': 'TIMEOUT',
                    'retry_after': 30
                }, 504
                
            except ConnectionError as e:
                logger.error(f"Connection error with {service_name}: {str(e)}")
                service_monitor.record_failure(service_name)
                
                # Attempt backup service
                if enable_fallback:
                    backup = service_monitor.get_backup_service(service_name)
                    if backup:
                        logger.info(f"Switching to backup service: {backup}")
                        try:
                            kwargs['service_endpoint'] = backup
                            return func(*args, **kwargs)
                        except Exception as backup_error:
                            logger.error(f"Backup service also failed: {str(backup_error)}")
                
                return {
                    'error': 'Service Unavailable',
                    'message': f'{service_name} is currently unavailable',
                    'error_code': 'SERVICE_DOWN'
                }, 503
                
            except RequestException as e:
                # Handle rate limiting (429 status)
                if hasattr(e, 'response') and e.response.status_code == 429:
                    retry_after = e.response.headers.get('Retry-After', 60)
                    logger.warning(f"Rate limited by {service_name}. Retry after {retry_after}s")
                    return {
                        'error': 'Rate Limit Exceeded',
                        'message': 'Too many requests. Please try again later.',
                        'retry_after': retry_after,
                        'error_code': 'RATE_LIMITED'
                    }, 429
                
                logger.error(f"Request failed for {service_name}: {str(e)}")
                return {
                    'error': 'External Service Error',
                    'message': 'Failed to communicate with external service',
                    'error_code': 'EXTERNAL_ERROR'
                }, 502
        
        return wrapper
    return decorator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

@validation_error_handler
def register_user(email: str, password: str):
    """Example function with validation error handling."""
    errors = {}
    if '@' not in email:
        errors['email'] = 'Invalid email format'
    if len(password) < 8:
        errors['password'] = 'Password too short'
    
    if errors:
        raise ValidationError("Registration validation failed", errors)
    
    return {'success': True, 'user_id': 123}


circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

@database_error_handler(max_retries=3, circuit_breaker=circuit_breaker)
def get_user_from_db(user_id: int):
    """Example function with database error handling."""
    # Simulate database operation
    # This would use actual database connection
    return {'id': user_id, 'name': 'John Doe'}


@external_service_handler('payment_service', timeout=5, enable_fallback=True)
def process_payment(amount: float, card_token: str, **kwargs):
    """Example function with external service error handling."""
    endpoint = kwargs.get('service_endpoint', 'https://api.payment.com')
    # This would make actual API call
    return {'transaction_id': 'txn_123', 'status': 'success'}


if __name__ == '__main__':
    print("=== Error Handler Pattern Library ===")
    
    # Test validation error handler
    print("\n1. Validation Error Handler:")
    result, status = register_user('invalid-email', 'short')
    print(f"Status: {status}")
    print(f"Response: {result}")
    
    # Test database error handler
    print("\n2. Database Error Handler:")
    user = get_user_from_db(123)
    print(f"User: {user}")
    
    # Test external service handler
    print("\n3. External Service Error Handler:")
    payment = process_payment(99.99, 'tok_visa')
    print(f"Payment: {payment}")
