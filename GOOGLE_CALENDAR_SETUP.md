# Google Calendar Integration for Voice Assistant

This guide will help you set up Google Calendar integration for your voice assistant, allowing you to create, update, and manage calendar events using voice commands.

## 🚀 Features

- **Create Events**: Schedule meetings, appointments, and reminders
- **List Events**: View upcoming events for any date range
- **Update Events**: Modify existing events (title, time, location, etc.)
- **Delete Events**: Remove events from your calendar
- **Find Free Time**: Automatically find available time slots
- **Natural Language**: Use natural language for dates and times
- **Multiple Calendars**: Support for multiple Google calendars

## 📋 Prerequisites

1. **Google Account**: You need a Google account with Google Calendar enabled
2. **Python Dependencies**: Install required packages
3. **Google Cloud Project**: Set up API credentials

## 🔧 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements_google_calendar.txt
```

### Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Give it a name (e.g., "Voice Assistant")
5. Download the credentials as `credentials.json`
6. Place `credentials.json` in your project root directory

### Step 4: Run Setup Script

```bash
python setup_google_calendar.py
```

This script will:
- Guide you through the OAuth flow
- Generate necessary tokens
- Test the API connection
- Show you the environment variables to add to your `.env` file

### Step 5: Update Environment Variables

Add the following to your `.env` file:

```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_here
```

### Step 6: Test the Integration

```bash
python test_google_calendar.py
```

This will run comprehensive tests to ensure everything is working correctly.

## 🗣️ Voice Commands

Once set up, you can use these voice commands:

### Creating Events
- "Schedule a meeting tomorrow at 2 PM"
- "Create an appointment for next Monday at 9 AM"
- "Book a dentist appointment for December 15th at 10:30"
- "Schedule a lunch meeting with John today at noon for 90 minutes"

### Viewing Events
- "What are my events for today?"
- "Show me my calendar for tomorrow"
- "List my meetings for next week"
- "What do I have scheduled for Friday?"

### Finding Free Time
- "Find free time tomorrow for 30 minutes"
- "When am I available next week for a 2-hour meeting?"
- "Find a 1-hour slot on Monday"

### Updating Events
- "Update my 3 PM meeting to 4 PM"
- "Change the location of my Monday meeting to the conference room"
- "Move my dentist appointment to next Tuesday"

### Deleting Events
- "Cancel my 2 PM meeting"
- "Delete the event at 10 AM tomorrow"

## ⚙️ Configuration Options

### Default Settings
The system uses these defaults (can be customized):
- **Default Duration**: 60 minutes
- **Work Hours**: 9 AM - 5 PM (for free time search)
- **Calendar**: Primary calendar
- **Timezone**: System timezone

### Advanced Configuration
You can customize behavior by modifying the GoogleCalendarManager class:

```python
# Custom work hours for free time search
calendar_manager.execute(
    "find_free_time",
    date="tomorrow",
    duration=30,
    work_start="08:00",
    work_end="18:00"
)

# Use a specific calendar
calendar_manager.execute(
    "create_event",
    title="Meeting",
    calendar_id="specific_calendar_id@group.calendar.google.com"
)
```

## 🛠️ Troubleshooting

### Common Issues

#### "No Google Calendar credentials found"
- Ensure `credentials.json` is in the project root
- Run `setup_google_calendar.py` to complete authentication

#### "Failed to refresh token"
- Delete `token.json` and run setup again
- Check that your OAuth client is still active in Google Cloud Console

#### "API quota exceeded"
- Google Calendar API has usage limits
- For development, these are usually sufficient
- For production, consider requesting quota increases

#### "Calendar tool not available"
- Check that Google Calendar packages are installed
- Verify credentials are properly set up
- Check console output for initialization errors

### Debug Mode
To see detailed API calls and responses, you can modify the GoogleCalendarManager to include debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Security Notes

- **Token Storage**: `token.json` contains sensitive data - don't commit to version control
- **Environment Variables**: Use `.env` for credentials - don't commit to version control
- **Scope Permissions**: The integration only requests calendar access, not broader Google account access
- **Local Storage**: Tokens are stored locally and not transmitted to third parties

## 📊 Supported Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `create_event` | Create a new event | `title` | `date`, `time`, `duration`, `description`, `location`, `attendees` |
| `list_events` | List upcoming events | None | `start_date`, `end_date`, `max_results` |
| `update_event` | Update existing event | `event_id` | `title`, `date`, `time`, `description`, `location` |
| `delete_event` | Delete an event | `event_id` | None |
| `find_free_time` | Find available time slots | None | `date`, `duration`, `work_start`, `work_end` |
| `get_event_details` | Get detailed event info | `event_id` | None |
| `list_calendars` | List available calendars | None | None |

## 🌍 Natural Language Support

The system understands natural language for dates and times:

### Dates
- "today", "tomorrow", "yesterday"
- "next Monday", "next Friday"
- "December 15th", "Jan 3rd"
- "2024-01-15", "01/15/2024"

### Times
- "2 PM", "14:30", "9 AM"
- "noon", "midnight"
- "10:30", "17:00"

## 🎯 Best Practices

1. **Be Specific**: Include as much detail as possible in voice commands
2. **Test First**: Use the test script to verify functionality
3. **Backup**: Consider backing up important calendar data
4. **Permissions**: Only grant necessary permissions to the application
5. **Updates**: Keep the Google API client libraries updated

## 📝 Example Usage

```python
from src.tool_calls.google_calendar import GoogleCalendarManager

# Initialize the calendar manager
calendar = GoogleCalendarManager()

# Create an event
result = calendar.execute(
    "create_event",
    title="Team Meeting",
    date="tomorrow",
    time="2 PM",
    duration=60,
    location="Conference Room A",
    description="Weekly team sync"
)

# List today's events
events = calendar.execute(
    "list_events",
    start_date="today",
    end_date="today"
)

# Find free time
free_slots = calendar.execute(
    "find_free_time",
    date="tomorrow",
    duration=30
)
```

## 🆘 Support

If you encounter issues:

1. Run the test script: `python test_google_calendar.py`
2. Check the setup script: `python setup_google_calendar.py`
3. Verify your Google Cloud Console settings
4. Check the console output for error messages

## 🔄 Updates and Maintenance

- Google API credentials may need periodic renewal
- Keep the Google client libraries updated
- Monitor API usage in Google Cloud Console
- Test functionality after any system updates

---

**Happy scheduling! 📅🎉** 