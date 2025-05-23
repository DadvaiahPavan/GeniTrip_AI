from agents.travel_agent import TravelAgent

def test_hyd_varanasi_route():
    """Test car travel data extraction between Hyderabad and Varanasi"""
    agent = TravelAgent()
    
    # Test with Hyderabad to Varanasi (a route with a large distance of 1,339 km)
    print("\n--- Testing car travel from Hyderabad to Varanasi ---")
    travel_data = agent.get_car_travel_data(
        source="Hyderabad",
        destination="Varanasi",
        start_date="2023-07-15",
        num_days=3
    )
    
    # Print driving options
    print("\nDriving Options:")
    for i, route in enumerate(travel_data.get('driving_options', [])):
        print(f"\n{i+1}. {route.get('route_name', 'Unknown route')}")
        print(f"   Distance: {route.get('distance', 'Unknown')}")
        print(f"   Distance in km: {route.get('distance_km', 'Unknown')}")
        print(f"   Duration: {route.get('duration', 'Unknown')}")
        print(f"   Via: {route.get('via', 'Unknown')}")
        
        # Print route steps if available
        if 'path_steps' in route and route['path_steps']:
            print("\n   Route Steps:")
            for step in route['path_steps'][:5]:  # Show first 5 steps
                print(f"   - {step}")
    
    # Print attractions along the route
    print("\nAttractions Along the Route:")
    for i, attraction in enumerate(travel_data.get('route_attractions', [])):
        print(f"\n{i+1}. {attraction.get('name', 'Unknown')}")
        print(f"   Rating: {attraction.get('rating', 'N/A')}")
        print(f"   Description: {attraction.get('description', 'No description')}")

    # Calculate trip cost to verify distance is being used correctly
    print("\nCalculating Trip Cost:")
    cost = agent.calculate_car_trip_cost(travel_data, [], 3)
    print(f"Total trip cost: ₹{cost['total']:.2f}")
    print(f"Fuel cost: ₹{cost.get('fuel', 0):.2f}")

if __name__ == "__main__":
    test_hyd_varanasi_route() 