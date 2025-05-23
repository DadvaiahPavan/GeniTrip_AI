from agents.travel_agent import TravelAgent

def test_hyd_blr_route():
    """Test car travel data extraction between Hyderabad and Bangalore"""
    agent = TravelAgent()
    
    # Test with Hyderabad to Bengaluru (a route we just added specific attractions for)
    print("\n--- Testing car travel from Hyderabad to Bangalore ---")
    travel_data = agent.get_car_travel_data(
        source="hyd",
        destination="bengaluru",
        start_date="2023-07-15",
        num_days=2
    )
    
    # Print driving options
    print("\nDriving Options:")
    for i, route in enumerate(travel_data.get('driving_options', [])):
        print(f"\n{i+1}. {route.get('route_name', 'Unknown route')}")
        print(f"   Distance: {route.get('distance', 'Unknown')}")
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
    
    # Generate a sample itinerary
    print("\nGenerating Itinerary:")
    itinerary = agent._generate_fallback_itinerary(
        source="hyd",
        destination="bengaluru",
        start_date="2023-07-15",
        num_days=2,
        travel_mode="car",
        travel_data=travel_data,
        hotel_data=[{"name": "Test Hotel", "location": "Bengaluru", "price": "₹5000", "rating": "4.5", "amenities": ["WiFi", "Breakfast"]}]
    )
    
    # Print travel details
    print("\nTravel Details:")
    print(itinerary['travel_details'])
    
    # Print daily plans
    print("\nDaily Plans:")
    for i, day in enumerate(itinerary['daily_plans']):
        print(f"\nDay {i+1}: {day['date']}")
        print(f"Morning: {day['morning']}")
        print(f"Afternoon: {day['afternoon']}")
        print(f"Evening: {day['evening']}")

if __name__ == "__main__":
    test_hyd_blr_route() 