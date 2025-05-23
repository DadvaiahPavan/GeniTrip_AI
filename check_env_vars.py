"""
Environment variable checker for flight search
Run this to verify your credentials are set up correctly
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Checking environment variables for flight data scraping...\n")

# Check for EaseMyTrip credentials
emt_username = os.getenv('EASEMYTRIP_USERNAME')
emt_password = os.getenv('EASEMYTRIP_PASSWORD')

if emt_username and emt_password:
    print(f"✅ EaseMyTrip credentials found: {emt_username[:3]}***")
else:
    print("❌ EaseMyTrip credentials missing! Add them to your .env file:")
    print("   EASEMYTRIP_USERNAME=your_username")
    print("   EASEMYTRIP_PASSWORD=your_password")

# Check for MakeMyTrip credentials
mmt_username = os.getenv('MAKEMYTRIP_USERNAME')
mmt_password = os.getenv('MAKEMYTRIP_PASSWORD')

if mmt_username and mmt_password:
    print(f"✅ MakeMyTrip credentials found: {mmt_username[:3]}***")
else:
    print("❌ MakeMyTrip credentials missing! Add them to your .env file:")
    print("   MAKEMYTRIP_USERNAME=your_username")
    print("   MAKEMYTRIP_PASSWORD=your_password")

print("\nNOTE: You need at least one set of credentials for real-time flight data.")
print("If you don't have accounts, create one at https://www.easemytrip.com or https://www.makemytrip.com")

# Check for .env file
if os.path.exists('.env'):
    print("\nℹ️ .env file exists in the current directory")
else:
    print("\n❌ No .env file found in the current directory!")
    print("Create a .env file in the project root with your credentials.") 