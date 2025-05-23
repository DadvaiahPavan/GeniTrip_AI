from agents.travel_agent import TravelAgent

agent = TravelAgent()

# Test with Delhi
print("\n--- Testing with Delhi ---")
attractions_delhi = agent.get_real_attractions("Delhi")
print(f"Retrieved {len(attractions_delhi)} attractions for Delhi")
for i, attraction in enumerate(attractions_delhi):
    print(f"\n{i+1}. {attraction.get('name', 'Unknown')}")
    print(f"   Rating: {attraction.get('rating', 'N/A')}")
    print(f"   Description: {attraction.get('description', 'No description')}")

# Test with Mumbai
print("\n--- Testing with Mumbai ---")
attractions_mumbai = agent.get_real_attractions("Mumbai")
print(f"Retrieved {len(attractions_mumbai)} attractions for Mumbai")
for i, attraction in enumerate(attractions_mumbai):
    print(f"\n{i+1}. {attraction.get('name', 'Unknown')}")
    print(f"   Rating: {attraction.get('rating', 'N/A')}")
    print(f"   Description: {attraction.get('description', 'No description')}") 