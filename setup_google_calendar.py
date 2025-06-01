#!/usr/bin/env python3
"""
Google Calendar Setup Script for Voice Assistant

This script helps you set up Google Calendar integration for your voice assistant.
Follow these steps:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials as 'credentials.json'
6. Run this script to complete the setup

Environment Variables Required (add to .env file):
- GOOGLE_CLIENT_ID: Your OAuth 2.0 Client ID
- GOOGLE_CLIENT_SECRET: Your OAuth 2.0 Client Secret
- GOOGLE_REFRESH_TOKEN: Generated during initial auth flow
"""

import os
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def setup_credentials():
    """Set up Google Calendar API credentials"""
    
    print("🔧 Google Calendar Setup for Voice Assistant")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found!")
        print("\n📋 To set up Google Calendar API:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download as 'credentials.json' in this directory")
        print("6. Run this script again")
        return False
    
    print("✅ Found credentials.json")
    
    # Load credentials
    creds = None
    
    # Check if token.json already exists
    if os.path.exists('token.json'):
        print("✅ Found existing token.json")
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Error refreshing token: {e}")
                creds = None
        
        if not creds:
            print("🔐 Starting OAuth flow...")
            print("📱 Your browser will open for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authentication successful!")
    
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("✅ Saved credentials to token.json")
    
    # Extract information for .env file
    creds_data = json.loads(creds.to_json())
    
    print("\n📝 Environment Variables for .env file:")
    print("-" * 40)
    print(f"GOOGLE_CLIENT_ID={creds_data.get('client_id', 'N/A')}")
    print(f"GOOGLE_CLIENT_SECRET={creds_data.get('client_secret', 'N/A')}")
    print(f"GOOGLE_REFRESH_TOKEN={creds_data.get('refresh_token', 'N/A')}")
    
    # Test the API
    print("\n🧪 Testing Google Calendar API...")
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # List calendars
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        print(f"✅ Successfully connected! Found {len(calendars)} calendars:")
        for cal in calendars[:3]:  # Show first 3 calendars
            name = cal.get('summary', 'Unknown')
            cal_id = cal.get('id', 'Unknown')
            primary = " (Primary)" if cal.get('primary') else ""
            print(f"   📅 {name}{primary}")
        
        # Test creating a test event (we'll delete it right after)
        print("\n🧪 Testing event creation...")
        from datetime import datetime, timedelta
        
        now = datetime.now()
        test_event = {
            'summary': 'Voice Assistant Test Event',
            'description': 'This is a test event created by the voice assistant setup script. It will be deleted automatically.',
            'start': {
                'dateTime': (now + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (now + timedelta(hours=2)).isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=test_event).execute()
        print(f"✅ Test event created: {event.get('htmlLink')}")
        
        # Delete the test event
        service.events().delete(calendarId='primary', eventId=event['id']).execute()
        print("✅ Test event deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def create_env_template():
    """Create a .env template file with Google Calendar variables"""
    env_template = """# Google Calendar API Configuration
# Get these values from Google Cloud Console after setting up OAuth 2.0 credentials

GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_here

# Optional: Specify default timezone
# GOOGLE_CALENDAR_TIMEZONE=America/New_York
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Created .env template file")
    else:
        print("ℹ️  .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Starting Google Calendar setup for Voice Assistant\n")
    
    # Check if required packages are installed
    try:
        import google.auth
        import google_auth_oauthlib
        import googleapiclient
        print("✅ Required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Install with: pip install -r requirements_google_calendar.txt")
        return
    
    # Create .env template
    create_env_template()
    
    # Set up credentials
    if setup_credentials():
        print("\n🎉 Google Calendar setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your .env file with the credentials shown above")
        print("2. Start your voice assistant")
        print("3. Try saying: 'Schedule a meeting tomorrow at 2 PM'")
        print("4. Or: 'What are my upcoming events?'")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 