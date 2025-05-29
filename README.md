  <p align="center">
  <img width="180" src="image\Geni_Trip_Logo.png" alt="GeniTrip AI">
  <p align="center">GeniTrip AI: Intelligent Travel Planning System</p>
</p>

---

# GeniTrip AI

GeniTrip AI is a comprehensive travel planning web application that leverages artificial intelligence to generate personalized travel itineraries. The system integrates real-time flight data extraction, car travel route planning, hotel recommendations, and attraction suggestions to create detailed travel plans.

## Features

- **Multi-modal Transportation**: Plan trips by flight or car with real-time data
- **Real-time Flight Information**: Extract current flight prices and schedules from Google Flights
- **Intelligent Route Planning**: Get detailed driving routes with attractions along the way
- **Hotel Recommendations**: Receive accommodation suggestions at your destination
- **AI-Generated Itineraries**: Get personalized day-by-day plans with morning, afternoon, and evening activities
- **Cost Estimation**: View comprehensive breakdown of expected trip expenses
- **PDF Export**: Download your complete travel plan for offline reference

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Web Scraping**: Playwright
- **AI Integration**: Groq API
- **PDF Generation**: xhtml2pdf
- **Mapping**: Google Maps integration



## Project Structure

```
GeniTrip_AI_Project/
├── agents/                    # Core business logic
│   ├── clean_real_flight_data.py  # Flight data extraction
│   ├── real_flight_data.py    # Flight data processing
│   └── travel_agent.py        # Main travel planning logic
├── static/                    # Static assets
│   ├── css/                   # Stylesheets
│   ├── images/                # Image assets
│   └── js/                    # JavaScript files
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Homepage
│   └── result.html            # Results page
├── utils/                     # Utility functions
│   └── pdf_generator.py       # PDF generation
├── app.py                     # Main Flask application
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Usage

1. Enter your source location, destination, start date, and number of days
2. Select your preferred travel mode (flight or car)
3. Click "Plan My Trip" to generate your personalized itinerary
4. View your comprehensive travel plan with transportation options, accommodations, and daily activities
5. Download your itinerary as a PDF for offline reference

## Future Enhancements

- Integration with booking platforms for one-click reservations
- User accounts for saving and managing multiple trip plans
- Mobile application for on-the-go planning
- Additional transportation options (train, bus)
- More personalization options based on user preferences

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## Contact

Pavan Dadvaiah - pavannetha219@gmail.com

Project Link: [https://github.com/yourusername/genitrip-ai](https://github.com/yourusername/genitrip-ai)
