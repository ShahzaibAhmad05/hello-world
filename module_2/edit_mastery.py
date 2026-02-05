import logging
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sum function with comprehensive error handling and validation
def sum(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers together with validation and error handling.
    
    Args:
        a: First number (int or float)
        b: Second number (int or float)
    
    Returns:
        The sum of a and b
    
    Raises:
        TypeError: If arguments are not numeric types
        ValueError: If arguments are None
    """
    logger.info(f"sum function called with arguments: a={a}, b={b}")
    
    try:
        # Input validation
        if a is None or b is None:
            logger.error("None value provided as argument")
            raise ValueError("Arguments cannot be None")
        
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            logger.error(f"Invalid argument types: a={type(a)}, b={type(b)}")
            raise TypeError(f"Both arguments must be numbers. Got {type(a).__name__} and {type(b).__name__}")
        
        # Perform calculation
        result = a + b
        logger.info(f"Successfully calculated sum: {result}")
        return result
        
    except (TypeError, ValueError) as e:
        logger.exception(f"Error in sum function: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in sum function: {str(e)}")
        raise

