"""
Test script for real-time flight data
Run this to validate the flight data extraction is working
"""
import json
import traceback
from datetime import datetime, timedelta

print("Starting test script...")

try:
    print("Importing clean_real_flight_data module...")
    from agents.clean_real_flight_data import get_real_flight_data
    print("Successfully imported get_real_flight_data")
except Exception as e:
    print(f"Error importing module: {str(e)}")
    traceback.print_exc()
    exit(1)

def test_flight_data():
    """Test the flight data extraction function with sample routes"""
    print("Entering test_flight_data function...")
    
    # Get a date 30 days from now (more likely to have flight data)
    future_date = datetime.now() + timedelta(days=30)
    date_str = future_date.strftime("%Y-%m-%d")
    print(f"Using test date: {date_str} (30 days from today)")
    
    # Test routes - common Indian city pairs
    test_routes = [
        ("Delhi", "Mumbai", date_str, 2),
        ("Bangalore", "Hyderabad", date_str, 3),
        ("Chennai", "Kolkata", date_str, 2)
    ]
    
    print("Testing flight data extraction...\n")
    
    # Try each route
    for source, destination, start_date, num_days in test_routes:
        print(f"\n{'='*80}")
        print(f"TESTING ROUTE: {source} to {destination} on {start_date}")
        print(f"{'='*80}")
        
        try:
            # Get flight data
            result = get_real_flight_data(source, destination, start_date, num_days)
            
            # Check if we got real data
            is_real = result.get('using_real_data', False)
            flight_options = result.get('flight_options', [])
            
            print(f"\nRESULTS: {'REAL DATA' if is_real else 'FALLBACK DATA'}")
            print(f"Found {len(flight_options)} flight options")
            
            # Print each flight option
            for i, flight in enumerate(flight_options):
                print(f"\nFlight {i+1}:")
                print(f"  Airline: {flight.get('airline', 'Unknown')}")
                print(f"  Flight #: {flight.get('flight_number', 'Unknown')}")
                print(f"  Departure: {flight.get('departure', 'Unknown')}")
                print(f"  Arrival: {flight.get('arrival', 'Unknown')}")
                print(f"  Duration: {flight.get('duration', 'Unknown')}")
                print(f"  Price: {flight.get('price', 'Unknown')}")
                print(f"  Source: {flight.get('source', 'Unknown')}")
                print(f"  Is Real: {flight.get('is_real', False)}")
            
        except Exception as e:
            print(f"Error testing route {source} to {destination}: {str(e)}")
            traceback.print_exc()
    
    print("\nTest completed!")

if __name__ == "__main__":
    print("Calling test_flight_data()...")
    try:
        test_flight_data()
    except Exception as e:
        print(f"Unhandled exception in test_flight_data: {str(e)}")
        traceback.print_exc() 