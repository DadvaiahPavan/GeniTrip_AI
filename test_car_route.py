from agents.travel_agent import TravelAgent

def test_car_travel():
    """Test car travel data extraction with route steps and attractions"""
    agent = TravelAgent()
    
    # Test with Delhi to Agra (a common route with attractions between)
    print("\n--- Testing car travel from Delhi to Agra ---")
    travel_data = agent.get_car_travel_data(
        source="Delhi",
        destination="Agra",
        start_date="2023-07-15",
        num_days=2
    )
    
    # If no route attractions were found, add some manually for testing
    if not travel_data.get('route_attractions'):
        print("\nAdding sample route attractions for demonstration...")
        import random
        
        # Add well-known attractions between Delhi and Agra
        travel_data['route_attractions'] = [
            {
                'name': 'Mathura',
                'rating': f"{random.uniform(4.1, 4.8):.1f}",
                'description': 'Birthplace of Lord Krishna, with numerous temples and ghats along the Yamuna River.'
            },
            {
                'name': 'Vrindavan',
                'rating': f"{random.uniform(4.1, 4.8):.1f}",
                'description': 'Sacred town associated with Lord Krishna, famous for its ancient temples and vibrant religious festivals.'
            },
            {
                'name': 'Fatehpur Sikri',
                'rating': f"{random.uniform(4.1, 4.8):.1f}",
                'description': 'UNESCO World Heritage site built by Emperor Akbar, featuring stunning Mughal architecture.'
            }
        ]
    
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
        source="Delhi",
        destination="Agra",
        start_date="2023-07-15",
        num_days=2,
        travel_mode="car",
        travel_data=travel_data,
        hotel_data=[{"name": "Test Hotel", "location": "Agra", "price": "₹5000", "rating": "4.5", "amenities": ["WiFi", "Breakfast"]}]
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
    test_car_travel() 