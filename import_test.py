"""
Minimal test of get_real_flight_data import
"""
import traceback

print("Testing import of get_real_flight_data...")

try:
    from agents.clean_real_flight_data import get_real_flight_data
    print("✓ Import successful!")
    
    # Verify the function exists
    print(f"Function type: {type(get_real_flight_data)}")
    print("Function signature:", get_real_flight_data.__code__.co_varnames[:get_real_flight_data.__code__.co_argcount])
    
except ImportError as e:
    print(f"✗ Import error: {str(e)}")
    traceback.print_exc()
except SyntaxError as e:
    print(f"✗ Syntax error in module: {str(e)}")
    print(f"  File: {e.filename}, Line: {e.lineno}, Offset: {e.offset}")
    print(f"  Text: {e.text}")
    traceback.print_exc()
except Exception as e:
    print(f"✗ Unexpected error: {str(e)}")
    traceback.print_exc()

print("Test completed.") 