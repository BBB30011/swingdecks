import logging
import sys
import os

def get_logger(name="swingdesk"):
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if get_logger is called repeatedly
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format: YYYY-MM-DD HH:MM:SS | LEVEL | MESSAGE
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, 'logs')
        
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, 'swingdesk.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.propagate = False
        
    return logger
