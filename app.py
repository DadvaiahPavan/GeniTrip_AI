from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
import os
import sys
import traceback
from dotenv import load_dotenv
import json
import time
from datetime import date
from utils.pdf_generator import generate_pdf
from agents.travel_agent import TravelAgent
from agents.clean_real_flight_data import get_real_flight_data
from flask_session import Session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key-for-sessions')
# Configure server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_PERMANENT'] = False
Session(app)

# Register the image directory as a static folder
image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image')
app.static_folder = 'static'

# Add a custom filter to Jinja2 to access dictionary items with dot notation
@app.template_filter('get')
def get_dict_item(d, key):
    """Get a dictionary item safely with dot notation in templates."""
    if d is None:
        return None
    return d.get(key)

# Route to serve files from the image directory
@app.route('/static/image/<path:filename>')
def serve_image(filename):
    return send_file(os.path.join(image_folder, filename))

@app.route('/')
def index():
    """Render the homepage with the travel planner form"""
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('index.html', today_date=today_date)

@app.route('/plan', methods=['POST', 'GET'])  # Added GET for debugging
def plan_trip():
    """Process trip planning request and return results"""
    # Debug - check request method
    print(f"Request method: {request.method}")
    print(f"Request form data: {request.form}")
    
    # Allow both GET and POST for debugging
    if request.method == 'GET':
        flash('Please use the form to plan your trip', 'error')
        return redirect(url_for('index'))
    
    try:
        print("Plan trip function called...")
        # Extract form data
        source = request.form.get('from_location')
        destination = request.form.get('to_location')
        start_date = request.form.get('start_date')
        num_days = int(request.form.get('num_days'))
        travel_mode = request.form.get('travel_mode')
        
        print(f"Form data received: {source} to {destination}, {start_date}, {num_days} days, {travel_mode}")
        
        if not all([source, destination, start_date, num_days, travel_mode]):
            print(f"Missing form data: source={source}, dest={destination}, date={start_date}, days={num_days}, mode={travel_mode}")
            flash('Please fill all the required fields', 'error')
            return redirect(url_for('index'))
        
        # Initialize travel agent
        print("Initializing TravelAgent...")
        travel_agent = TravelAgent()
        
        # Get travel data based on mode using the updated methods
        print(f"Getting travel data for {travel_mode}...")
        try:
            if travel_mode == 'car':
                print("Calling get_car_travel_data...")
                travel_data = travel_agent.get_car_travel_data(source, destination, start_date, num_days)
                print("Car travel data retrieved!")
            else:
                print("Calling get_real_flight_data for ACTUAL real-time flight data...")
                # Use our improved real-time flight data function
                travel_data = get_real_flight_data(source, destination, start_date, num_days)
                
                # Check if we got real data or fallback data
                if travel_data.get('using_real_data', False):
                    print("✅ Successfully retrieved REAL flight data!")
                    
                    # Process the flight data - extract outbound flights
                    flight_options = travel_data.get('flight_options', [])
                    
                    # Add a clear label to indicate these are VERIFIED real-time prices
                    for flight in flight_options:
                        if 'price' in flight and '₹' not in flight['price'] and not flight['price'].startswith('₹'):
                            flight['price'] = f"₹ {flight['price']}"
                        
                        # Ensure consistent naming between departure/arrival 
                        if 'departure_time' in flight and 'departure' not in flight:
                            flight['departure'] = flight['departure_time']
                        if 'arrival_time' in flight and 'arrival' not in flight:
                            flight['arrival'] = flight['arrival_time']
                        
                        # Add a marker noting these are verified prices
                        if 'data_source' not in flight:
                            flight['data_source'] = "Google Flights (VERIFIED)"
                        
                        # Ensure we have all required fields
                        if 'source' not in flight:
                            flight['source'] = source
                        if 'destination' not in flight:
                            flight['destination'] = destination
                else:
                    print("⚠ Using fallback flight data - no real-time data available")
                
                print("Flight travel data retrieved!")
            print(f"Travel data retrieved: {str(travel_data)[:100]}...")
        except Exception as e:
            print(f"Error getting travel data: {e}")
            traceback.print_exc()
            # Use fallback data
            print("Using fallback travel data due to error")
            if travel_mode == 'car':
                # Let the travel_agent generate appropriate fallback data with estimated distances
                travel_data = {
                    'driving_options': [],  # This will get populated by travel_agent's fallback mechanism
                    'attractions': travel_agent.get_real_attractions(destination),
                    'route_attractions': travel_agent.get_real_route_attractions(source, destination)
                }
            else:
                source_len = len(source)
                dest_len = len(destination)
                base_price = 3000 + (ord(source[0].lower()) - ord('a')) * 100
                
                travel_data = {
                    'flight_options': [
                        {
                            'airline': 'IndiGo',
                            'flight_number': f'6E {900 + (source_len % 100)}',
                            'departure': f'0{6 + (source_len % 3)}:15',
                            'arrival': f'0{8 + (dest_len % 3)}:45',
                            'duration': f'1h {30 + (dest_len % 30)}m',
                            'price': f'₹ {base_price:,}'
                        }
                    ],
                    'attractions': travel_agent.get_real_attractions(destination)
                }
        
        # Get hotel data
        print(f"Getting hotel data for {destination}...")
        try:
            print("Calling get_hotel_data...")
            hotel_data = travel_agent.get_hotel_data(destination, start_date, num_days)
            print("Hotel data retrieved!")
            print(f"Hotel data retrieved: {str(hotel_data)[:100]}...")
        except Exception as e:
            print(f"Error getting hotel data: {e}")
            traceback.print_exc()
            # Use fallback data
            print("Using fallback hotel data due to error")
            hotel_data = travel_agent._get_fallback_hotels(destination)
        
        # Generate itinerary
        print("Generating itinerary...")
        try:
            # Try to use LLaMA via Groq if available
            print("Calling generate_itinerary...")
            itinerary = travel_agent.generate_itinerary(source, destination, start_date, num_days, travel_mode, travel_data, hotel_data)
            print("Itinerary generated successfully")
        except Exception as e:
            print(f"Error generating itinerary: {e}")
            traceback.print_exc()
            # Use fallback itinerary
            print("Using fallback itinerary due to error")
            itinerary = travel_agent._generate_fallback_itinerary(source, destination, start_date, num_days, travel_mode, travel_data, hotel_data)
        
        # Calculate trip cost based on travel mode
        print("Calculating trip costs...")
        cost_breakdown = {}
        try:
            if travel_mode == 'car':
                cost_breakdown = travel_agent.calculate_car_trip_cost(travel_data, hotel_data, num_days)
                print(f"Car trip cost calculated: ₹{cost_breakdown['total']:.2f}")
            else:  # flight mode
                cost_breakdown = travel_agent.calculate_flight_trip_cost(travel_data, hotel_data, num_days)
                print(f"Flight trip cost calculated: ₹{cost_breakdown['total']:.2f}")
        except Exception as e:
            print(f"Error calculating trip costs: {e}")
            traceback.print_exc()
            # Create fallback cost breakdown with hotel price at 1500 per night
            hotel_price_per_night = 1500.0  # Set hotel price to 1500 per night
            if travel_mode == 'car':
                cost_breakdown = {
                    'fuel': 2000.0,
                    'hotel': hotel_price_per_night * num_days,
                    'food': 1000.0 * num_days,
                    'num_nights': num_days,
                    'total': 2000.0 + hotel_price_per_night * num_days + 1000.0 * num_days
                }
            else:  # flight mode
                cost_breakdown = {
                    'flight': 5000.0,
                    'hotel': hotel_price_per_night * num_days,
                    'food': 1000.0 * num_days,
                    'local_transport': 500.0 * num_days,
                    'num_nights': num_days,
                    'total': 5000.0 + hotel_price_per_night * num_days + 1000.0 * num_days + 500.0 * num_days
                }
        
        # Format the itinerary for better display
        print("Formatting itinerary for display...")
        import json
        from html import escape
        
        # Initialize with default values to prevent errors
        formatted_itinerary = "<p>Your itinerary has been generated.</p>"
        
        # Ensure travel_data has the necessary keys to prevent template errors
        if travel_data is None:
            travel_data = {}
        
        # Ensure travel_data has a 'stops' key to prevent template errors
        if 'stops' not in travel_data:
            travel_data['stops'] = []
            
        # Ensure travel_data has driving_options
        if 'driving_options' not in travel_data:
            travel_data['driving_options'] = []
            
        # Ensure travel_data has flight_options
        if 'flight_options' not in travel_data:
            travel_data['flight_options'] = []
        
        # Debug the type of itinerary
        print(f"DEBUG - Itinerary type: {type(itinerary)}")
        
        try:
            # Convert itinerary to a dictionary if it's not already
            if isinstance(itinerary, dict):
                itinerary_data = itinerary
                print("Itinerary is already a dictionary")
                if itinerary:
                    print(f"DEBUG - Itinerary keys: {list(itinerary.keys())}")
            elif isinstance(itinerary, str) and itinerary.strip():
                # Only try to parse if it's a non-empty string
                print(f"DEBUG - Itinerary string length: {len(itinerary)}")
                print(f"DEBUG - Itinerary string preview: {itinerary[:100] if len(itinerary) > 100 else itinerary}")
                
                try:
                    # Try to parse as JSON if it starts with '{'
                    if itinerary.strip().startswith('{'):
                        itinerary_data = json.loads(itinerary.replace("'", '"'))
                        print("Successfully parsed itinerary from JSON string")
                    else:
                        print("Itinerary is a string but not JSON format")
                        # Create a simple dictionary with the string as summary
                        itinerary_data = {
                            'summary': itinerary,
                            'daily_plans': []
                        }
                except Exception as json_error:
                    print(f"Failed to parse itinerary as JSON: {json_error}")
                    # Create a simple dictionary with the string as summary
                    itinerary_data = {
                        'summary': itinerary,
                        'daily_plans': []
                    }
            else:
                print(f"Itinerary is neither a valid dict nor str. Type: {type(itinerary)}")
                # Create an empty dictionary to prevent errors
                itinerary_data = {
                    'summary': 'No itinerary data available',
                    'daily_plans': []
                }
    
            if itinerary_data:
                # Add trip summary
                if 'summary' in itinerary_data:
                    formatted_itinerary += f'<div class="trip-overview mb-4 p-3 bg-light rounded">\n'
                    formatted_itinerary += f'<h4 class="border-bottom pb-2 mb-3">Trip Overview</h4>\n'
                    formatted_itinerary += f'<p>{escape(str(itinerary_data["summary"]))}</p>\n'
                    formatted_itinerary += f'</div>\n'
                
                # Add travel details
                if 'travel_details' in itinerary_data:
                    formatted_itinerary += f'<div class="travel-details mb-4 p-3 bg-light rounded">\n'
                    formatted_itinerary += f'<h4 class="border-bottom pb-2 mb-3">Travel Details</h4>\n'
                    formatted_itinerary += f'<p>{escape(str(itinerary_data["travel_details"]))}</p>\n'
                    formatted_itinerary += f'</div>\n'
                
                # Add accommodation details
                if 'accommodation' in itinerary_data:
                    formatted_itinerary += f'<div class="accommodation mb-4 p-3 bg-light rounded">\n'
                    formatted_itinerary += f'<h4 class="border-bottom pb-2 mb-3">Accommodation</h4>\n'
                    formatted_itinerary += f'<p>{escape(str(itinerary_data["accommodation"]))}</p>\n'
                    formatted_itinerary += f'</div>\n'
                
                # Add daily plans
                if 'daily_plans' in itinerary_data and isinstance(itinerary_data['daily_plans'], list):
                    formatted_itinerary += f'<h4 class="mt-4 mb-3">Daily Itinerary</h4>'
                    
                    for i, day in enumerate(itinerary_data['daily_plans']):
                        day_num = i + 1
                        day_date = day.get('date', f'Day {day_num}')
                        
                        formatted_itinerary += f'<div class="day-plan mb-4">'
                        formatted_itinerary += f'<div class="day-header p-2 bg-primary text-white rounded-top">'
                        formatted_itinerary += f'<h5 class="mb-0">Day {day_num}: {escape(str(day_date))}</h5>'
                        formatted_itinerary += f'</div>'
                        formatted_itinerary += f'<div class="day-content p-3 border border-top-0 rounded-bottom">'
                        
                        # Morning
                        if 'morning' in day:
                            morning_text = day.get('morning', '')
                            formatted_itinerary += f'<div class="time-block mb-3">'
                            formatted_itinerary += f'<h6 class="text-primary"><i class="fas fa-sun me-2"></i>Morning</h6>'
                            formatted_itinerary += f'<p>{escape(str(morning_text))}</p>'
                            formatted_itinerary += f'</div>'
                        
                        # Afternoon
                        if 'afternoon' in day:
                            afternoon_text = day.get('afternoon', '')
                            formatted_itinerary += f'<div class="time-block mb-3">'
                            formatted_itinerary += f'<h6 class="text-warning"><i class="fas fa-cloud-sun me-2"></i>Afternoon</h6>'
                            formatted_itinerary += f'<p>{escape(str(afternoon_text))}</p>'
                            formatted_itinerary += f'</div>'
                        
                        # Evening
                        if 'evening' in day:
                            evening_text = day.get('evening', '')
                            formatted_itinerary += f'<div class="time-block">'
                            formatted_itinerary += f'<h6 class="text-info"><i class="fas fa-moon me-2"></i>Evening</h6>'
                            formatted_itinerary += f'<p>{escape(str(evening_text))}</p>'
                            formatted_itinerary += f'</div>'
                        
                        formatted_itinerary += f'</div></div>'
                
                # If we successfully created a formatted itinerary, use it
                if formatted_itinerary:
                    itinerary = formatted_itinerary
                    print("Successfully formatted itinerary")
        except Exception as e:
            print(f"Error formatting itinerary: {e}")
            traceback.print_exc()
            # Keep the original itinerary if formatting fails
        
        # Add the trip details to the session for downloading PDF later
        trip_data = {
            'source': source,
            'destination': destination,
            'start_date': start_date,
            'num_days': num_days,
            'travel_mode': travel_mode,
            'itinerary': itinerary_data,
            'cost_breakdown': cost_breakdown,  # Add cost breakdown to session data
            # Add attractions, hotels, and route attractions to the session data for PDF generation
            'attractions': travel_data.get('attractions', []),
            'hotels': hotel_data if isinstance(hotel_data, list) else [],
            'route_attractions': travel_data.get('route_attractions', [])
        }
        session['trip_data'] = trip_data
        
        # Render the result template with the trip data
        return render_template('result.html', 
                               source=source,
                               destination=destination,
                               start_date=start_date,
                               num_days=num_days,
                               travel_mode=travel_mode,
                               itinerary=itinerary_data,
                               travel_data=travel_data,
                               hotel_data=hotel_data,
                               cost_breakdown=cost_breakdown)  # Pass cost breakdown to template
    
    except Exception as e:
        print(f"Unexpected error in plan_trip: {e}")
        traceback.print_exc()
        flash('An error occurred while processing your request. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/download-pdf')
def download_pdf():
    """Generate and download the itinerary as a PDF file"""
    try:
        # Check if trip data exists in session
        if 'trip_data' not in session:
            app.logger.error("No trip_data found in session")
            flash('No itinerary found. Please plan a trip first.', 'error')
            return redirect(url_for('index'))
        
        trip_data = session['trip_data']
        
        # Log the keys present in trip_data for debugging
        app.logger.info(f"trip_data keys: {list(trip_data.keys())}")
        
        # Validate required fields
        required_fields = ['source', 'destination', 'start_date', 'num_days', 'travel_mode', 'itinerary']
        missing_fields = [field for field in required_fields if field not in trip_data or not trip_data[field]]
        
        if missing_fields:
            app.logger.error(f"Missing required fields in trip_data: {missing_fields}")
            flash(f"Missing data required for PDF generation: {', '.join(missing_fields)}", 'error')
            return redirect(url_for('index'))
        
        # Clean up the itinerary data before sending to PDF generator
        if 'itinerary' in trip_data and isinstance(trip_data['itinerary'], dict):
            # Make a copy of the trip data to avoid modifying the session data
            clean_trip_data = dict(trip_data)
            
            # Clean the summary if it exists
            if 'summary' in clean_trip_data['itinerary']:
                summary = clean_trip_data['itinerary']['summary']
                
                # If summary is a string with JSON-like format, clean it
                if isinstance(summary, str) and ('{' in summary or "'" in summary):
                    # Remove all JSON formatting characters
                    clean_summary = summary.replace('{', '').replace('}', '')
                    clean_summary = clean_summary.replace('[', '').replace(']', '')
                    clean_summary = clean_summary.replace("'", "").replace('"', "")
                    
                    # Replace key labels with proper formatting
                    clean_summary = clean_summary.replace("summary:", "")
                    clean_summary = clean_summary.replace("traveldetails:", "Travel Details: ")
                    clean_summary = clean_summary.replace("accommodation:", "Accommodation: ")
                    clean_summary = clean_summary.replace("dailyplans:", "")
                    clean_summary = clean_summary.replace("tips:", "Travel Tips: ")
                    
                    # Clean up extra spaces and commas
                    clean_summary = clean_summary.replace("  ", " ")
                    clean_summary = clean_summary.replace(", ,", ",")
                    clean_summary = clean_summary.replace(",,", ",")
                    
                    # Update the summary
                    clean_trip_data['itinerary']['summary'] = clean_summary
                
                # If summary is a dictionary, convert it to a clean string
                elif isinstance(summary, dict):
                    clean_parts = []
                    
                    if 'summary' in summary:
                        clean_parts.append(str(summary['summary']).strip("'\"[]{}"))
                    
                    if 'traveldetails' in summary:
                       clean_parts.append(f"""Travel Details: {str(summary['traveldetails']).strip("'\"[]{}")}"""))
 
                    
                    if 'accommodation' in summary:
                        clean_parts.append(f"Accommodation: {str(summary['accommodation']).strip("'\"[]{}")}") 
                    
                    # Join all parts with line breaks
                    clean_summary = "\n\n".join(clean_parts)
                    clean_trip_data['itinerary']['summary'] = clean_summary
            
            # Use the cleaned data for PDF generation
            app.logger.info("Using cleaned trip data for PDF generation")
            pdf_path = generate_pdf(clean_trip_data)
        else:
            # If no cleaning needed, use original data
            app.logger.info("Attempting to generate PDF...")
            pdf_path = generate_pdf(trip_data)
        
        if pdf_path and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            app.logger.info(f"PDF generated successfully at {pdf_path}")
            # Send the file as an attachment
            try:
                # Use a custom function to send file and delete it after sending
                response = send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=f"itinerary-{trip_data['source']}-to-{trip_data['destination']}.pdf",
                    mimetype='application/pdf'
                )
                
                # Set up a callback to delete the file after sending
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            app.logger.info(f"Temporary PDF file deleted: {pdf_path}")
                    except Exception as cleanup_error:
                        app.logger.error(f"Error cleaning up PDF file: {cleanup_error}")
                
                return response
            except Exception as file_error:
                app.logger.error(f"Error sending PDF file: {file_error}")
                import traceback
                app.logger.error(traceback.format_exc())
                
                # Clean up the file if there was an error
                if os.path.exists(pdf_path):
                    try:
                        os.remove(pdf_path)
                        app.logger.info(f"Temporary PDF file deleted after error: {pdf_path}")
                    except:
                        pass
                        
                flash('Error sending the PDF file. Please try again.', 'error')
                return redirect(url_for('index'))
        else:
            app.logger.error(f"PDF generation failed or produced empty file. Path: {pdf_path}")
            flash('Failed to generate PDF. Please try again.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error generating PDF: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        flash('An error occurred while generating the PDF. Please try again.', 'error')
        return redirect(url_for('index'))

# Blueprint for pages
from flask import Blueprint

# Create a blueprint for pages
pages = Blueprint('pages', __name__)

@pages.route('/resources')
def resources():
    """Render the resources page"""
    return render_template('pages/resources.html')

@pages.route('/travel-guides')
def travel_guides():
    """Render the travel guides page"""
    return render_template('pages/travel_guides.html')

@pages.route('/faq')
def faq():
    """Render the FAQ page"""
    return render_template('pages/faq.html')

@pages.route('/support')
def support():
    """Render the support page"""
    return render_template('pages/support.html')

@pages.route('/privacy-policy')
def privacy_policy():
    """Render the privacy policy page"""
    return render_template('pages/privacy_policy.html')

# Register the blueprint
app.register_blueprint(pages, url_prefix='/pages')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    print(f"500 error: {e}")
    print(traceback.format_exc())
    return render_template('index.html', error="An internal server error occurred"), 500

if __name__ == '__main__':
    # Configure the application to run
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"Starting application in {'debug' if debug_mode else 'production'} mode on port {port}")
    print(f"Environment variables set: GROQ_API_KEY={'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
    
    # Run with use_reloader=False to prevent Playwright issues
    app.run(debug=debug_mode, port=port, host='0.0.0.0', use_reloader=False) 
