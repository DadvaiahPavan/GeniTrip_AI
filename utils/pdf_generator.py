import os
import tempfile
from datetime import datetime
from xhtml2pdf import pisa
import logging

def generate_pdf(data):
    """Generate a PDF file from the itinerary data"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('pdf_generator')
    
    try:
        # Extract data with validation
        if not isinstance(data, dict):
            logger.error(f"Invalid data type: {type(data)}. Expected dictionary.")
            return None
            
        # Extract with default values to prevent errors
        source = str(data.get('source', 'Unknown'))
        destination = str(data.get('destination', 'Unknown'))
        start_date = str(data.get('start_date', 'Unknown'))
        num_days = int(data.get('num_days', 1))
        travel_mode = str(data.get('travel_mode', 'Unknown'))
        itinerary_data = data.get('itinerary', '')
        cost_breakdown = data.get('cost_breakdown', {})
        
        # Log the data we're working with
        logger.info(f"Generating PDF for {source} to {destination}, {start_date}, {num_days} days, {travel_mode}")
        
        # Project name - customize this
        project_name = "GeniTrip AI"
        
        # Extract summary directly from the itinerary data
        summary_html = ""
        content_html = ""
        daily_plans_html = ""
        tips_html = ""
        
        try:
            # Process the summary section
            if isinstance(itinerary_data, dict) and 'summary' in itinerary_data:
                summary = itinerary_data['summary']
                
                # Direct extraction of summary components without using JSON format
                summary_html = "<div class='trip-summary-section'>"
                summary_html += "<h2>Trip Summary</h2>"
                
                # Extract overview/summary
                overview = ""
                travel_details = ""
                accommodation = ""
                
                # Handle different summary formats
                if isinstance(summary, str):
                    # If summary is a string, extract parts directly
                    if "'summary'" in summary and "'traveldetails'" in summary:
                        # Extract main trip summary
                        parts = summary.split("'summary':", 1)
                        if len(parts) > 1:
                            overview_part = parts[1].split("'traveldetails'", 1)[0]
                            overview = overview_part.strip(" ',{}[]\"").replace("'", "")
                        
                        # Extract travel details
                        parts = summary.split("'traveldetails':", 1)
                        if len(parts) > 1:
                            travel_part = parts[1].split("'accommodation'", 1)[0]
                            travel_details = travel_part.strip(" ',{}[]\"").replace("'", "")
                        
                        # Extract accommodation
                        parts = summary.split("'accommodation':", 1)
                        if len(parts) > 1:
                            accom_part = parts[1].split("'dailyplans'", 1)[0]
                            if "'dailyplans'" not in parts[1]:
                                accom_part = parts[1].split("'tips'", 1)[0]
                            accommodation = accom_part.strip(" ',{}[]\"").replace("'", "")
                    else:
                        # If it's a simple string, use it as overview
                        overview = summary.strip(" ',{}[]\"").replace("'", "")
                
                elif isinstance(summary, dict):
                    # If summary is a dictionary, extract values directly
                    if 'summary' in summary:
                        overview = str(summary['summary']).strip(" ',{}[]\"").replace("'", "")
                    
                    if 'traveldetails' in summary:
                        travel_details = str(summary['traveldetails']).strip(" ',{}[]\"").replace("'", "")
                    
                    if 'accommodation' in summary:
                        accommodation = str(summary['accommodation']).strip(" ',{}[]\"").replace("'", "")
                
                # Add the extracted sections to the HTML
                if overview:
                    summary_html += "<div class='summary-subsection'>"
                    summary_html += "<h3>Trip Overview</h3>"
                    summary_html += f"<p>{overview}</p>"
                    summary_html += "</div>"
                
                if travel_details:
                    summary_html += "<div class='summary-subsection'>"
                    summary_html += "<h3>Travel Details</h3>"
                    summary_html += f"<p>{travel_details}</p>"
                    summary_html += "</div>"
                
                if accommodation:
                    summary_html += "<div class='summary-subsection'>"
                    summary_html += "<h3>Accommodation</h3>"
                    summary_html += f"<p>{accommodation}</p>"
                    summary_html += "</div>"
                
                summary_html += "</div>"
            
            # Process daily plans if available
            if isinstance(itinerary_data, dict):
                # Try to get daily plans from different possible locations in the data
                daily_plans = None
                
                # Check for dailyplans key
                if 'dailyplans' in itinerary_data:
                    daily_plans = itinerary_data['dailyplans']
                # Check for daily_plans key (alternative format)
                elif 'daily_plans' in itinerary_data:
                    daily_plans = itinerary_data['daily_plans']
                # Check if it might be in the summary
                elif 'summary' in itinerary_data and isinstance(itinerary_data['summary'], str):
                    summary_str = itinerary_data['summary']
                    if "'dailyplans'" in summary_str:
                        # Try to extract daily plans from the summary string
                        try:
                            parts = summary_str.split("'dailyplans':", 1)
                            if len(parts) > 1:
                                daily_plans_str = parts[1].split("'tips'", 1)[0] if "'tips'" in parts[1] else parts[1]
                                # Clean up the string and try to parse it
                                daily_plans_str = daily_plans_str.strip(" ',[]")
                                
                                # Extract day information using regex
                                import re
                                day_pattern = r"\{\s*'date':\s*'([^']+)'[,}].*?'morning':\s*'([^']+)'[,}].*?'afternoon':\s*'([^']+)'[,}].*?'evening':\s*'([^']+)'[,}]"
                                day_matches = re.findall(day_pattern, daily_plans_str, re.DOTALL)
                                
                                if day_matches:
                                    # Convert matches to a list of day dictionaries
                                    daily_plans = []
                                    for date, morning, afternoon, evening in day_matches:
                                        daily_plans.append({
                                            'date': date,
                                            'morning': morning,
                                            'afternoon': afternoon,
                                            'evening': evening
                                        })
                        except Exception as e:
                            logger.error(f"Error extracting daily plans from summary: {e}")
                
                # Generate HTML for daily plans if we found them
                if daily_plans:
                    daily_plans_html = "<div class='daily-plans-section'>"
                    daily_plans_html += "<h2>Daily Itinerary</h2>"
                    
                    if isinstance(daily_plans, list):
                        for i, day in enumerate(daily_plans):
                            day_num = i + 1
                            day_date = day.get('date', f'Day {day_num}')
                            
                            daily_plans_html += f"<div class='day-plan'>"
                            daily_plans_html += f"<div class='day-header'><h3>Day {day_num}: {day_date}</h3></div>"
                            daily_plans_html += f"<div class='day-content'>"
                            
                            # Morning activities
                            if 'morning' in day:
                                morning = str(day['morning']).strip(" ',{}[]\"").replace("'", "")
                                daily_plans_html += f"<div class='time-block'>"
                                daily_plans_html += f"<h4>Morning</h4>"
                                daily_plans_html += f"<p>{morning}</p>"
                                daily_plans_html += f"</div>"
                            
                            # Afternoon activities
                            if 'afternoon' in day:
                                afternoon = str(day['afternoon']).strip(" ',{}[]\"").replace("'", "")
                                daily_plans_html += f"<div class='time-block'>"
                                daily_plans_html += f"<h4>Afternoon</h4>"
                                daily_plans_html += f"<p>{afternoon}</p>"
                                daily_plans_html += f"</div>"
                            
                            # Evening activities
                            if 'evening' in day:
                                evening = str(day['evening']).strip(" ',{}[]\"").replace("'", "")
                                daily_plans_html += f"<div class='time-block'>"
                                daily_plans_html += f"<h4>Evening</h4>"
                                daily_plans_html += f"<p>{evening}</p>"
                                daily_plans_html += f"</div>"
                            
                            daily_plans_html += f"</div></div>"
                    elif isinstance(daily_plans, str):
                        # If it's a string, display it directly
                        clean_text = daily_plans.strip(" ',{}[]\"").replace("'", "")
                        daily_plans_html += f"<div class='day-content'><p>{clean_text}</p></div>"
                    
                    daily_plans_html += "</div>"
                else:
                    # If we couldn't find daily plans, check if there's a raw itinerary we can display
                    raw_itinerary = str(itinerary_data).replace("{", "").replace("}", "")
                    raw_itinerary = raw_itinerary.replace("[", "").replace("]", "")
                    raw_itinerary = raw_itinerary.replace("'", "").replace('"', "")
                    
                    # Remove summary and other sections we've already handled
                    if "summary:" in raw_itinerary:
                        raw_itinerary = raw_itinerary.split("summary:", 1)[1]
                    if "traveldetails:" in raw_itinerary:
                        raw_itinerary = raw_itinerary.split("traveldetails:", 1)[1]
                    if "accommodation:" in raw_itinerary:
                        raw_itinerary = raw_itinerary.split("accommodation:", 1)[1]
                    
                    # Display the remaining content as the itinerary
                    daily_plans_html = "<div class='daily-plans-section'>"
                    daily_plans_html += "<h2>Trip Itinerary</h2>"
                    daily_plans_html += f"<div class='day-content'><p>{raw_itinerary}</p></div>"
                    daily_plans_html += "</div>"
            
            # Process travel tips if available
            if isinstance(itinerary_data, dict) and 'tips' in itinerary_data:
                tips = itinerary_data['tips']
                
                tips_html = "<div class='tips-section'>"
                tips_html += "<h2>Travel Tips</h2>"
                tips_html += "<ul class='tips-list'>"
                
                if isinstance(tips, list):
                    for tip in tips:
                        clean_tip = str(tip).strip(" ',{}[]\"").replace("'", "")
                        tips_html += f"<li>{clean_tip}</li>"
                else:
                    # If tips is a string, try to split it
                    tips_str = str(tips).strip(" ',{}[]\"").replace("'", "")
                    tip_items = [t.strip() for t in tips_str.split(",") if t.strip()]
                    
                    for tip in tip_items:
                        tips_html += f"<li>{tip}</li>"
                
                tips_html += "</ul></div>"
            
            # Generate attractions HTML if available
            attractions_html = ""
            if 'attractions' in data and data['attractions']:
                attractions = data['attractions']
                
                attractions_html = "<div class='poi-section'>"
                attractions_html += "<h2>Top Attractions in " + destination + "</h2>"
                attractions_html += "<div class='attractions-list'>"
                
                if isinstance(attractions, list):
                    for i, attraction in enumerate(attractions):
                        if isinstance(attraction, dict):
                            name = attraction.get('name', '')
                            description = attraction.get('description', '')
                            rating = attraction.get('rating', '')
                            
                            attractions_html += f"<div class='attraction-item'>"
                            attractions_html += f"<div class='attraction-number'>{i+1}.</div>"
                            attractions_html += f"<div class='attraction-content'>"
                            attractions_html += f"<div class='attraction-name'>{name}</div>"
                            if rating:
                                attractions_html += f"<div class='attraction-desc'>Rating: {rating}</div>"
                            if description:
                                attractions_html += f"<div class='attraction-desc'>{description}</div>"
                            attractions_html += f"</div></div>"
                        elif isinstance(attraction, str):
                            attractions_html += f"<div class='attraction-item'>"
                            attractions_html += f"<div class='attraction-number'>{i+1}.</div>"
                            attractions_html += f"<div class='attraction-content'>"
                            attractions_html += f"<div class='attraction-name'>{attraction}</div>"
                            attractions_html += f"</div></div>"
                
                attractions_html += "</div></div>"
            
            # Generate hotels HTML if available
            hotels_html = ""
            if 'hotels' in data and data['hotels']:
                hotels = data['hotels']
                
                hotels_html = "<div class='poi-section'>"
                hotels_html += "<h2>Recommended Hotels</h2>"
                hotels_html += "<div class='attractions-list'>"
                
                if isinstance(hotels, list):
                    for i, hotel in enumerate(hotels):
                        if isinstance(hotel, dict):
                            name = hotel.get('name', '')
                            description = hotel.get('description', '')
                            price = hotel.get('price', '')
                            
                            hotels_html += f"<div class='attraction-item'>"
                            hotels_html += f"<div class='attraction-number'>{i+1}.</div>"
                            hotels_html += f"<div class='attraction-content'>"
                            hotels_html += f"<div class='attraction-name'>{name}</div>"
                            if price:
                                hotels_html += f"<div class='attraction-desc'>Price: {price}</div>"
                            if description:
                                hotels_html += f"<div class='attraction-desc'>{description}</div>"
                            hotels_html += f"</div></div>"
                        elif isinstance(hotel, str):
                            hotels_html += f"<div class='attraction-item'>"
                            hotels_html += f"<div class='attraction-number'>{i+1}.</div>"
                            hotels_html += f"<div class='attraction-content'>"
                            hotels_html += f"<div class='attraction-name'>{hotel}</div>"
                            hotels_html += f"</div></div>"
                
                hotels_html += "</div></div>"
            
            # Generate route attractions HTML if available
            route_attractions_html = ""
            if 'route_attractions' in data and data['route_attractions']:
                route_attractions = data['route_attractions']
                
                route_attractions_html = "<div class='poi-section'>"
                route_attractions_html += "<h2>Points of Interest Along the Route</h2>"
                route_attractions_html += "<div class='attractions-list'>"
                
                if isinstance(route_attractions, list):
                    for i, attraction in enumerate(route_attractions):
                        if isinstance(attraction, dict):
                            name = attraction.get('name', '')
                            description = attraction.get('description', '')
                            rating = attraction.get('rating', '')
                            
                            route_attractions_html += f"<div class='attraction-item'>"
                            route_attractions_html += f"<div class='attraction-number'>{i+1}.</div>"
                            route_attractions_html += f"<div class='attraction-content'>"
                            route_attractions_html += f"<div class='attraction-name'>{name}</div>"
                            if rating:
                                route_attractions_html += f"<div class='attraction-desc'>Rating: {rating}</div>"
                            if description:
                                route_attractions_html += f"<div class='attraction-desc'>{description}</div>"
                            route_attractions_html += f"</div></div>"
                        elif isinstance(attraction, str):
                            route_attractions_html += f"<div class='attraction-item'>"
                            route_attractions_html += f"<div class='attraction-number'>{i+1}.</div>"
                            route_attractions_html += f"<div class='attraction-content'>"
                            route_attractions_html += f"<div class='attraction-name'>{attraction}</div>"
                            route_attractions_html += f"</div></div>"
                
                route_attractions_html += "</div></div>"
            
            # Combine all sections
            html_content = summary_html + attractions_html + hotels_html + route_attractions_html + daily_plans_html + tips_html
            
            # If we somehow ended up with empty content, create a basic version
            if not html_content.strip():
                # Create a simple version from the raw data
                clean_text = str(itinerary_data).replace("{", "").replace("}", "")
                clean_text = clean_text.replace("[", "").replace("]", "")
                clean_text = clean_text.replace("'", "").replace('"', "")
                
                html_content = f"<div class='trip-summary-section'><h2>Trip Summary</h2><div class='summary-content'><p>{clean_text}</p></div></div>"
        
        except Exception as e:
            # If there's an error, create a simple version
            logger.error(f"Error processing itinerary data: {e}")
            clean_text = str(itinerary_data).replace("{", "").replace("}", "")
            clean_text = clean_text.replace("[", "").replace("]", "")
            clean_text = clean_text.replace("'", "").replace('"', "")
            
            html_content = f"<div class='trip-summary-section'><h2>Trip Summary</h2><div class='summary-content'><p>{clean_text}</p></div></div>"
        
        # Generate cost breakdown HTML
        try:
            cost_html = _generate_cost_breakdown_html(travel_mode, cost_breakdown)
        except Exception as e:
            logger.error(f"Error generating cost breakdown: {e}")
            cost_html = "<div class='cost-breakdown'><h2>Trip Cost</h2><p>Cost details not available</p></div>"
        
        # Create a complete HTML document with styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Travel Itinerary: {source} to {destination}</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    color: #333;
                    position: relative;
                    background-color: #fff;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    color: #1a365d;
                    border-bottom: 3px solid #3182ce;
                    padding-bottom: 15px;
                    background-color: #ebf8ff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #1a365d;
                    font-size: 28px;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                h2 {{
                    color: #2b6cb0;
                    font-size: 22px;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #bee3f8;
                    padding-bottom: 8px;
                    font-weight: 600;
                }}
                h3 {{
                    color: #3182ce;
                    font-size: 20px;
                    margin-top: 25px;
                    margin-bottom: 10px;
                    font-weight: 500;
                }}
                ul, ol {{
                    margin-bottom: 20px;
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                p {{
                    margin-bottom: 15px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    font-size: 12px;
                    color: #718096;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 15px;
                }}
                .summary-box {{
                    background-color: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }}
                .summary-item {{
                    margin-bottom: 12px;
                    display: flex;
                }}
                .summary-item strong {{
                    color: #2d3748;
                    min-width: 120px;
                    display: inline-block;
                }}
                strong {{
                    color: #2d3748;
                    font-weight: 600;
                }}
                .attraction {{
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px dashed #e2e8f0;
                }}
                .date {{
                    color: #718096;
                    font-style: italic;
                    font-weight: 500;
                    margin-bottom: 8px;
                }}
                .budget {{
                    background-color: #e6fffa;
                    border: 1px solid #b2f5ea;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 25px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }}
                .watermark {{
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 100px;
                    color: rgba(200, 200, 200, 0.1);
                    z-index: -1;
                    white-space: nowrap;
                }}
                .cost-breakdown {{
                    background-color: #f0fff4;
                    border: 1px solid #c6f6d5;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }}
                .cost-breakdown h2 {{
                    color: #276749;
                    border-bottom: 2px solid #9ae6b4;
                    margin-top: 0;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-size: 22px;
                }}
                .cost-breakdown-inner {{
                    padding: 0 10px;
                }}
                .cost-category {{
                    margin-bottom: 20px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    overflow: hidden;
                }}
                .cost-category-header {{
                    background-color: #c6f6d5;
                    color: #276749;
                    font-weight: 600;
                    padding: 8px 15px;
                    font-size: 16px;
                }}
                .cost-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 15px;
                    border-bottom: 1px dotted #e2e8f0;
                }}
                .cost-item:last-child {{
                    border-bottom: none;
                }}
                .cost-label {{
                    color: #4a5568;
                    font-weight: 500;
                }}
                .cost-value {{
                    color: #2d3748;
                    font-weight: 600;
                }}
                .cost-total {{
                    margin-top: 25px;
                    border: 2px solid #48bb78;
                    border-radius: 6px;
                    padding: 15px 20px;
                    font-weight: bold;
                    display: flex;
                    justify-content: space-between;
                    font-size: 18px;
                    background-color: #d4edda;
                }}
                .total-label {{
                    color: #276749;
                    font-size: 18px;
                    font-weight: 700;
                }}
                .total-value {{
                    color: #276749;
                    font-size: 20px;
                    font-weight: 700;
                }}
                
                /* New styles for the driving options section */
                .driving-options-section {{
                    background-color: #ebf8ff;
                    border: 1px solid #90cdf4;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }}
                .driving-options-section h2 {{
                    color: #2c5282;
                    border-bottom: 2px solid #90cdf4;
                    margin-top: 0;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }}
                .driving-details p {{
                    margin-bottom: 10px;
                    padding: 8px 0;
                    border-bottom: 1px dotted #bee3f8;
                }}
                
                /* New styles for the points of interest section */
                .poi-section {{
                    background-color: #faf5ff;
                    border: 1px solid #d6bcfa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }}
                .poi-section h2 {{
                    color: #553c9a;
                    border-bottom: 2px solid #d6bcfa;
                    margin-top: 0;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .attractions-list {{
                    margin-top: 15px;
                }}
                .attraction-item {{
                    display: flex;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px dashed #e9d8fd;
                }}
                .attraction-number {{
                    color: #6b46c1;
                    font-weight: bold;
                    margin-right: 10px;
                    min-width: 25px;
                }}
                .attraction-content {{
                    flex: 1;
                }}
                .attraction-name {{
                    font-weight: 600;
                    color: #4a5568;
                    margin-bottom: 5px;
                }}
                .attraction-desc {{
                    color: #718096;
                    font-size: 14px;
                }}
                
                /* Trip Summary Section Styling */
                .trip-summary-section {{
                    background-color: #fff8e1;
                    border: 1px solid #ffe082;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }}
                .trip-summary-section h2 {{
                    color: #f57c00;
                    border-bottom: 2px solid #ffcc80;
                    margin-top: 0;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .summary-subsection {{
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #fffaf0;
                    border-radius: 6px;
                    border-left: 3px solid #ffb74d;
                }}
                .summary-subsection h3 {{
                    color: #e65100;
                    margin-top: 0;
                    margin-bottom: 10px;
                    font-size: 18px;
                    font-weight: 600;
                }}
                .summary-subsection p {{
                    margin: 0;
                    line-height: 1.6;
                    color: #424242;
                }}
                .summary-content p {{
                    margin-bottom: 12px;
                    line-height: 1.6;
                    color: #424242;
                    text-align: justify;
                }}
                
                /* Daily Plans Section Styling */
                .daily-plans-section {{
                    background-color: #f0f4ff;
                    border-left: 3px solid #4c6ef5;
                }}
                .daily-plans-list {{
                    margin-top: 15px;
                }}
                .daily-plan-item {{
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px dashed #c5cae9;
                }}
                .daily-plan-item:last-child {{
                    border-bottom: none;
                    margin-bottom: 0;
                }}
                .daily-plan-date {{
                    font-weight: 600;
                    color: #3949ab;
                    font-size: 16px;
                    margin-bottom: 8px;
                    padding: 5px 10px;
                    background-color: #e8eaf6;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .daily-plan-time {{
                    margin: 5px 0;
                    padding-left: 15px;
                }}
                .time-label {{
                    font-weight: 600;
                    color: #5c6bc0;
                    display: inline-block;
                    width: 90px;
                }}
                
                /* Tips Section Styling */
                .tips-section {{
                    background-color: #f3e5f5;
                    border-left: 3px solid #9c27b0;
                }}
                .tips-list {{
                    margin: 10px 0;
                    padding-left: 25px;
                }}
                .tips-list li {{
                    margin-bottom: 10px;
                    color: #4a148c;
                    position: relative;
                }}
                .tips-list li:before {{
                    content: '\2022';
                    color: #9c27b0;
                    font-weight: bold;
                    position: absolute;
                    left: -15px;
                }}
                
                /* Daily itinerary styling */
                .day-header {{
                    background-color: #e6fffa;
                    padding: 10px 15px;
                    border-radius: 6px;
                    margin: 20px 0 15px 0;
                    border-left: 4px solid #38b2ac;
                }}
                .day-number {{
                    font-weight: bold;
                    color: #285e61;
                }}
                .day-title {{
                    color: #2c7a7b;
                    font-weight: 500;
                }}
                
                @page {{
                    size: a4 portrait;
                    margin: 2cm;
                    @frame footer {{
                        -pdf-frame-content: footerContent;
                        bottom: 1cm;
                        margin-left: 1cm;
                        margin-right: 1cm;
                        height: 1cm;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="watermark">{project_name}</div>
            
            <div class="header">
                <h1>Travel Itinerary</h1>
                <p>{source} to {destination} | {start_date} | {num_days} Days | {travel_mode.capitalize()} Travel</p>
            </div>
            
            <div class="summary-box">
                <div class="summary-item"><strong>From:</strong> {source}</div>
                <div class="summary-item"><strong>To:</strong> {destination}</div>
                <div class="summary-item"><strong>Start Date:</strong> {start_date}</div>
                <div class="summary-item"><strong>Duration:</strong> {num_days} Days</div>
                <div class="summary-item"><strong>Travel Mode:</strong> {travel_mode.capitalize()}</div>
            </div>
            
            {cost_html}
            
            {html_content}
            
            <div id="footerContent" class="footer">
                <p>Generated by {project_name} | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        # Create a temporary file for the PDF
        try:
            # Create a unique temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            logger.info(f"Created temporary file at {temp_path}")
            
            # Convert HTML to PDF with error handling
            pdf_file = open(temp_path, "wb")
            pisa_status = pisa.CreatePDF(
                src=html,  # HTML content
                dest=pdf_file,  # File handle to receive PDF
                encoding='utf-8',
            )
            pdf_file.close()
            
            # Check for errors
            if pisa_status.err:
                logger.error(f"PDF generation failed with pisa error: {pisa_status.err}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
            
            # Verify the file exists and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                logger.info(f"PDF generated successfully at {temp_path} with size {os.path.getsize(temp_path)} bytes")
                return temp_path
            else:
                logger.error(f"PDF file is empty or does not exist at {temp_path}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
        except Exception as e:
            logger.error(f"Exception during PDF generation: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return None
    
    except Exception as e:
        logger.error(f"Exception in generate_pdf: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def _generate_cost_breakdown_html(travel_mode, cost_breakdown):
    """Generate HTML for the cost breakdown section with improved visual design"""
    if not cost_breakdown or 'total' not in cost_breakdown:
        return ""
    
    # Format numbers with commas for thousands
    def format_price(price):
        return f"₹ {price:,.2f}"
    
    html = """
    <div class="cost-breakdown">
        <h2>Estimated Trip Cost Breakdown</h2>
        <div class="cost-breakdown-inner">
    """
    
    # Get number of nights for accommodation
    num_nights = cost_breakdown.get('num_nights', '')
    
    if travel_mode == 'car':
        html += f"""
        <div class="cost-category">
            <div class="cost-category-header">Transportation</div>
            <div class="cost-item">
                <div class="cost-label">Fuel Cost</div>
                <div class="cost-value">{format_price(cost_breakdown.get('fuel', 0))}</div>
            </div>
        </div>
        
        <div class="cost-category">
            <div class="cost-category-header">Accommodation</div>
            <div class="cost-item">
                <div class="cost-label">Hotel ({num_nights} nights @ ₹1,500 per night)</div>
                <div class="cost-value">{format_price(cost_breakdown.get('hotel', 0))}</div>
            </div>
        </div>
        
        <div class="cost-category">
            <div class="cost-category-header">Food & Miscellaneous</div>
            <div class="cost-item">
                <div class="cost-label">Meals & Dining</div>
                <div class="cost-value">{format_price(cost_breakdown.get('food', 0))}</div>
            </div>
        </div>
        """
    else:  # flight mode
        html += f"""
        <div class="cost-category">
            <div class="cost-category-header">Transportation</div>
            <div class="cost-item">
                <div class="cost-label">Flight Tickets</div>
                <div class="cost-value">{format_price(cost_breakdown.get('flight', 0))}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Local Transportation</div>
                <div class="cost-value">{format_price(cost_breakdown.get('local_transport', 0))}</div>
            </div>
        </div>
        
        <div class="cost-category">
            <div class="cost-category-header">Accommodation</div>
            <div class="cost-item">
                <div class="cost-label">Hotel ({num_nights} nights @ ₹1,500 per night)</div>
                <div class="cost-value">{format_price(cost_breakdown.get('hotel', 0))}</div>
            </div>
        </div>
        
        <div class="cost-category">
            <div class="cost-category-header">Food & Miscellaneous</div>
            <div class="cost-item">
                <div class="cost-label">Meals & Dining</div>
                <div class="cost-value">{format_price(cost_breakdown.get('food', 0))}</div>
            </div>
        </div>
        """
    
    # Total cost
    html += f"""
        <div class="cost-total">
            <div class="total-label">Total Estimated Cost</div>
            <div class="total-value">{format_price(cost_breakdown.get('total', 0))}</div>
        </div>
        </div>
    </div>
    """
    
    return html

def _clean_text(text):
    """Clean text by removing quotes, brackets, and other formatting characters"""
    if not text:
        return ""
        
    # Remove common dictionary formatting characters
    cleaned = text.replace("{", "").replace("}", "")
    cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = cleaned.replace("'", "")
    cleaned = cleaned.replace('"', "")
    
    # Remove key labels
    cleaned = cleaned.replace("summary:", "")
    cleaned = cleaned.replace("traveldetails:", "")
    cleaned = cleaned.replace("accommodation:", "")
    cleaned = cleaned.replace("dailyplans:", "")
    cleaned = cleaned.replace("tips:", "")
    
    # Clean up extra spaces and commas
    cleaned = cleaned.replace("  ", " ")
    cleaned = cleaned.replace(", ,", ",")
    cleaned = cleaned.replace(",,", ",")
    
    return cleaned.strip()

def _extract_section(text, start_marker, end_markers):
    """Extract a section from text between start_marker and the first occurrence of any end_marker"""
    if not text or not start_marker:
        return ""
        
    # Find the start of the section
    if start_marker not in text:
        return ""
        
    section = text.split(start_marker, 1)[1]
    
    # Find the end of the section (first occurrence of any end marker)
    for marker in end_markers:
        if marker in section:
            section = section.split(marker, 1)[0]
    
    return _clean_text(section)

def _format_summary(summary_text):
    """Format the summary text to make it more readable without JSON format"""
    if not summary_text:
        return ""
    
    # If it's already a dictionary, convert to string
    if isinstance(summary_text, dict):
        summary_str = str(summary_text)
    else:
        summary_str = str(summary_text)
    
    # Extract the main sections directly as text, not as a dictionary
    trip_overview = ""
    travel_details = ""
    accommodation = ""
    daily_plans = ""
    tips = ""
    
    try:
        # Extract trip overview
        if "'summary'" in summary_str:
            trip_overview = _extract_section(summary_str, "'summary':", ["'traveldetails'", "'travel"])
        
        # Extract travel details
        if "'traveldetails'" in summary_str:
            travel_details = _extract_section(summary_str, "'traveldetails':", ["'accommodation'"])
        
        # Extract accommodation
        if "'accommodation'" in summary_str:
            accommodation = _extract_section(summary_str, "'accommodation':", ["'dailyplans'", "'tips'"])
        
        # Extract daily plans
        if "'dailyplans'" in summary_str:
            daily_plans = _extract_section(summary_str, "'dailyplans':", ["'tips'"])
        
        # Extract tips
        if "'tips'" in summary_str:
            tips = _extract_section(summary_str, "'tips':", [])
            
        # If we couldn't extract anything, just clean the whole text
        if not any([trip_overview, travel_details, accommodation, daily_plans, tips]):
            # Just clean the whole text
            trip_overview = _clean_text(summary_str)
    except Exception as e:
        # If any error occurs, just clean the whole text
        trip_overview = _clean_text(summary_str)
    
    # Return the extracted sections as plain text, not as a dictionary
    return {
        "overview": trip_overview,
        "travel": travel_details,
        "accommodation": accommodation,
        "daily_plans": daily_plans,
        "tips": tips
    }

def _generate_summary_html(summary_data):
    """Generate HTML for the summary section with improved formatting"""
    if not summary_data:
        return ""
    
    html = "<div class='trip-summary-section'>"
    html += "<h2>Trip Summary</h2>"
    
    try:
        if isinstance(summary_data, dict):
            # If we have structured data
            if "overview" in summary_data and summary_data["overview"]:
                html += "<div class='summary-subsection'>"
                html += "<h3>Trip Overview</h3>"
                html += f"<p>{summary_data['overview']}</p>"
                html += "</div>"
            
            if "travel" in summary_data and summary_data["travel"]:
                html += "<div class='summary-subsection'>"
                html += "<h3>Travel Details</h3>"
                html += f"<p>{summary_data['travel']}</p>"
                html += "</div>"
            
            if "accommodation" in summary_data and summary_data["accommodation"]:
                html += "<div class='summary-subsection'>"
                html += "<h3>Accommodation</h3>"
                html += f"<p>{summary_data['accommodation']}</p>"
                html += "</div>"
        else:
            # If we have plain text or other format, just display it directly
            html += "<div class='summary-content'>"
            html += f"<p>{str(summary_data)}</p>"
            html += "</div>"
    except Exception as e:
        # If any error occurs, display a simple message
        html += "<div class='summary-content'>"
        html += "<p>Trip summary information is available in the detailed itinerary below.</p>"
        html += "</div>"
    
    html += "</div>"
    return html

def _markdown_to_html(markdown_text):
    """Convert markdown to HTML with improved formatting for itinerary sections"""
    # Pre-process special sections to enhance their formatting
    processed_text = markdown_text
    
    # Format Driving Options section
    if "Driving Options" in processed_text:
        driving_section = processed_text.split("Driving Options")[1].split("\n\n")[0]
        formatted_driving = "<div class='driving-options-section'><h2>Driving Options</h2>"
        formatted_driving += "<div class='driving-details'>"
        
        # Extract and format the driving details
        lines = driving_section.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("Driving Options"):
                formatted_driving += f"<p>{line.strip()}</p>"
        
        formatted_driving += "</div></div>"
        processed_text = processed_text.replace("Driving Options" + driving_section, formatted_driving)
    
    # Format Points of Interest section
    if "Points of Interest Along the Route" in processed_text:
        poi_section = processed_text.split("Points of Interest Along the Route")[1]
        end_marker = "\n\n"
        if "Estimated Trip Cost" in poi_section:
            poi_section = poi_section.split("Estimated Trip Cost")[0]
        elif "\n\n" in poi_section:
            poi_section = poi_section.split("\n\n")[0]
            
        formatted_poi = "<div class='poi-section'><h2>Points of Interest Along the Route</h2>"
        formatted_poi += "<div class='attractions-list'>"
        
        # Extract and format the attractions
        lines = poi_section.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("Points of Interest"):
                if any(line.startswith(str(i) + ".") for i in range(1, 20)):
                    # This is a numbered attraction
                    num, content = line.split(".", 1)
                    if " - " in content:
                        name, desc = content.split(" - ", 1)
                        formatted_poi += f"<div class='attraction-item'>"
                        formatted_poi += f"<div class='attraction-number'>{num}.</div>"
                        formatted_poi += f"<div class='attraction-content'>"
                        formatted_poi += f"<div class='attraction-name'>{name.strip()}</div>"
                        formatted_poi += f"<div class='attraction-desc'>{desc.strip()}</div>"
                        formatted_poi += f"</div></div>"
                    else:
                        formatted_poi += f"<div class='attraction-item'>"
                        formatted_poi += f"<div class='attraction-number'>{num}.</div>"
                        formatted_poi += f"<div class='attraction-content'>{content.strip()}</div>"
                        formatted_poi += f"</div>"
                else:
                    formatted_poi += f"<p>{line.strip()}</p>"
        
        formatted_poi += "</div></div>"
        if "Estimated Trip Cost" in processed_text:
            processed_text = processed_text.replace("Points of Interest Along the Route" + poi_section, formatted_poi)
        else:
            processed_text = processed_text.replace("Points of Interest Along the Route" + poi_section + end_marker, formatted_poi)
    
    # Now process the modified text with standard markdown conversion
    html = processed_text
    
    # Headers
    html = html.replace("# ", "<h1>").replace("\n## ", "</h1>\n<h2>").replace("\n### ", "</h2>\n<h3>")
    html = html.replace("\n#### ", "</h3>\n<h4>").replace("\n##### ", "</h4>\n<h5>").replace("\n###### ", "</h5>\n<h6>")
    
    # Close the last header
    if "<h1>" in html and "</h1>" not in html:
        html = html + "</h1>"
    if "<h2>" in html and "</h2>" not in html:
        html = html + "</h2>"
    if "<h3>" in html and "</h3>" not in html:
        html = html + "</h3>"
    if "<h4>" in html and "</h4>" not in html:
        html = html + "</h4>"
    if "<h5>" in html and "</h5>" not in html:
        html = html + "</h5>"
    if "<h6>" in html and "</h6>" not in html:
        html = html + "</h6>"
    
    # Bold and Italic
    html = html.replace("**", "<strong>").replace("__", "<strong>")
    count_bold = html.count("<strong>")
    for i in range(count_bold // 2):
        html = html.replace("<strong>", "<strong>", 1).replace("<strong>", "</strong>", 1)
    
    html = html.replace("*", "<em>").replace("_", "<em>")
    count_italic = html.count("<em>")
    for i in range(count_italic // 2):
        html = html.replace("<em>", "<em>", 1).replace("<em>", "</em>", 1)
    
    # Lists (only process sections that haven't been specially formatted)
    if "<div class='poi-section'>" not in html:
        lines = html.split("\n")
        in_list = False
        list_type = None
        
        for i in range(len(lines)):
            # Unordered lists
            if lines[i].strip().startswith("- "):
                if not in_list or list_type != "ul":
                    lines[i] = "<ul>\n<li>" + lines[i][2:] + "</li>"
                    in_list = True
                    list_type = "ul"
                else:
                    lines[i] = "<li>" + lines[i][2:] + "</li>"
            # Ordered lists
            elif lines[i].strip() and lines[i][0].isdigit() and ". " in lines[i][:4]:
                if not in_list or list_type != "ol":
                    lines[i] = "<ol>\n<li>" + lines[i][lines[i].find(". ") + 2:] + "</li>"
                    in_list = True
                    list_type = "ol"
                else:
                    lines[i] = "<li>" + lines[i][lines[i].find(". ") + 2:] + "</li>"
            # End of lists
            elif in_list and lines[i].strip() and not lines[i].strip().startswith("-") and not (lines[i][0].isdigit() and ". " in lines[i][:4]):
                if list_type == "ul":
                    lines[i-1] += "\n</ul>"
                else:
                    lines[i-1] += "\n</ol>"
                in_list = False
                list_type = None
        
        # Close any open lists at the end of the document
        if in_list:
            if list_type == "ul":
                lines.append("</ul>")
            else:
                lines.append("</ol>")
        
        html = "\n".join(lines)
    
    # Paragraphs (only for sections that haven't been specially formatted)
    if "<div class='driving-options-section'>" not in html or "<div class='poi-section'>" not in html:
        lines = html.split("\n")
        html_with_paragraphs = ""
        in_paragraph = False
        
        for line in lines:
            if line.strip() and not line.strip().startswith("<h") and not line.strip().startswith("<li") and \
               not line.strip().startswith("<ul") and not line.strip().startswith("<ol") and \
               not line.strip().startswith("</") and not line.strip().startswith("<div"):
                if not in_paragraph:
                    html_with_paragraphs += "<p>" + line + "\n"
                    in_paragraph = True
                else:
                    html_with_paragraphs += line + "\n"
            else:
                if in_paragraph:
                    html_with_paragraphs += "</p>\n" + line + "\n"
                    in_paragraph = False
                else:
                    html_with_paragraphs += line + "\n"
        
        # Close any open paragraph at the end
        if in_paragraph:
            html_with_paragraphs += "</p>"
            
        html = html_with_paragraphs
    
    # Format daily itinerary sections
    days_pattern = r"Day (\d+): ([^\n]+)"
    import re
    html = re.sub(days_pattern, r'<div class="day-header"><span class="day-number">Day \1:</span> <span class="day-title">\2</span></div>', html)
    
    return html