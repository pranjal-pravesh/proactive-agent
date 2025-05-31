# Weather API Setup Guide

The voice assistant now uses the [weatherstack API](https://weatherstack.com/documentation) for real-time weather information.

## Getting Started

### 1. Get Your Free API Key

1. Visit [weatherstack.com/signup](https://weatherstack.com/signup)
2. Sign up for a free account
3. Copy your API access key from the dashboard

### 2. Configure the API Key

You have three options to configure your API key:

#### Option A: .env File (Recommended for Development)
1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and replace the placeholder:
   ```
   WEATHERSTACK_API_KEY=your_actual_api_key_here
   WEATHERSTACK_DEFAULT_UNITS=m
   ```
3. The `.env` file is automatically excluded from git, keeping your API key secure

#### Option B: Environment Variable (Recommended for Production)
```bash
# Windows
set WEATHERSTACK_API_KEY=your_api_key_here

# Linux/Mac
export WEATHERSTACK_API_KEY=your_api_key_here
```

#### Option C: Config File (Not Recommended - Less Secure)
Edit `configs/config.yaml` or `configs/config_phi4mini.yaml`:
```yaml
weatherstack:
  api_key: "your_api_key_here"  # Replace with your actual API key
  default_units: "m"  # 'm' for Celsius, 'f' for Fahrenheit
```
**Note**: Be careful not to commit API keys to version control!

### 3. Install Dependencies

Make sure you have the required libraries installed:
```bash
pip install requests>=2.28.0 python-dotenv>=1.0.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Usage Examples

Once configured, you can ask for weather information:

- "What's the weather like?"
- "Temperature in London"
- "Weather in New York"
- "How hot is it in Tokyo?"
- "Is it raining in Paris?"

## API Features

### Free Plan Includes:
- 1,000 API calls per month
- Current weather data
- 150+ global data sources
- JSON API responses

### Temperature Units:
- **m** (metric): Celsius, km/h for wind
- **f** (fahrenheit): Fahrenheit, mph for wind  
- **s** (scientific): Kelvin, m/s for wind

### Available Data:
- Current temperature and "feels like" temperature
- Weather conditions (sunny, cloudy, rainy, etc.)
- Humidity percentage
- Wind speed and direction
- Atmospheric pressure
- Visibility
- UV index
- Local time

## Error Handling

The weather tool provides user-friendly error messages for common issues:

- **No API key**: "Weather service not configured..."
- **Invalid location**: "Invalid location... Please provide a valid city name"
- **API limit reached**: "Monthly API request limit reached..."
- **Network issues**: "Weather service connection failed..."

## Advanced Usage

### Coordinates
You can also use latitude,longitude coordinates:
```
"Weather at 40.7128,-74.0060"  # New York City coordinates
```

### International Locations
Include country/region for better accuracy:
```
"Weather in London, UK"
"Temperature in Paris, France" 
"Weather in Sydney, Australia"
```

## Troubleshooting

### Common Issues:

1. **"Weather service not configured"**
   - Check that your API key is set correctly
   - Verify the environment variable or config file

2. **"Invalid location"**
   - Check spelling of city/country names
   - Try including the country (e.g., "London, UK")
   - Use major cities or well-known locations

3. **"Monthly API request limit reached"**
   - You've used your 1,000 free requests
   - Wait until next month or upgrade your plan

For more information, visit the [weatherstack documentation](https://weatherstack.com/documentation). 