"""
Playwright installation check script
Run this to verify your Playwright installation is working correctly
"""
import sys
import platform
import traceback

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")

try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright module is installed correctly")
    
    try:
        with sync_playwright() as p:
            print("✅ Playwright launched successfully")
            
            try:
                browser = p.chromium.launch(headless=True)
                print("✅ Browser launched successfully")
                
                try:
                    context = browser.new_context()
                    print("✅ Browser context created successfully")
                    
                    try:
                        page = context.new_page()
                        print("✅ Page created successfully")
                        
                        try:
                            page.goto("https://example.com")
                            print("✅ Network connection successful")
                            title = page.title()
                            print(f"Page title: {title}")
                            print("✅ Page interaction successful")
                        except Exception as e:
                            print(f"❌ Failed to navigate to page: {str(e)}")
                            traceback.print_exc()
                    except Exception as e:
                        print(f"❌ Failed to create page: {str(e)}")
                        traceback.print_exc()
                except Exception as e:
                    print(f"❌ Failed to create browser context: {str(e)}")
                    traceback.print_exc()
            except Exception as e:
                print(f"❌ Failed to launch browser: {str(e)}")
                print("\nTry reinstalling browsers with: playwright install")
                traceback.print_exc()
    except Exception as e:
        print(f"❌ Failed to initialize Playwright: {str(e)}")
        traceback.print_exc()
except ImportError:
    print("❌ Playwright not installed!")
    print("\nTry installing it with: pip install playwright")
    print("And then install browsers with: playwright install")

print("\nTest complete. If all steps show ✅, your Playwright installation is working correctly.")
print("If any steps show ❌, follow the suggestions to fix the issues.") 