"""
Simple test script to check Python and imports
"""
import sys
import os
import traceback

print("Starting simple test...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# List all files in the agents directory
print("\nFiles in agents directory:")
try:
    for f in os.listdir("agents"):
        print(f"  - {f}")
except Exception as e:
    print(f"Error listing agents directory: {str(e)}")

# Try to import a basic module from agents
print("\nTrying to import TravelAgent...")
try:
    from agents.travel_agent import TravelAgent
    print("Successfully imported TravelAgent")
except Exception as e:
    print(f"Error importing TravelAgent: {str(e)}")
    traceback.print_exc()

print("\nTest completed!") 