import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Optional Google Calendar imports - graceful degradation if not available
try:
    import pytz
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError as e:
    GOOGLE_CALENDAR_AVAILABLE = False
    _missing_import = str(e)

class GoogleCalendarManager:
    """Google Calendar integration for the voice assistant"""
    
    # If modifying these scopes, delete the token.json file
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Initialize Google Calendar Manager"""
        if not GOOGLE_CALENDAR_AVAILABLE:
            raise Exception(
                f"Google Calendar dependencies not available: {_missing_import}\n"
                "Install with: pip install -r requirements_google_calendar.txt\n"
                "Then run: python setup_google_calendar.py"
            )
            
        self.service = None
        self.calendar_id = 'primary'  # Default to primary calendar
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load credentials from environment variables
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        
        # Check if we have stored credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If we have environment variables, create credentials
        if not creds and client_id and client_secret and refresh_token:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                id_token=None,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.SCOPES
            )
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                # Try to use credentials.json for initial setup
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    raise Exception("No Google Calendar credentials found. Please set up credentials.json or environment variables.")
        
        # Save the credentials for the next run
        if creds:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
        else:
            raise Exception("Failed to authenticate with Google Calendar")
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "google_calendar",
            "description": "Manage Google Calendar events including creating, viewing, updating, and deleting appointments",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Calendar action to perform",
                        "enum": ["create_event", "list_events", "update_event", "delete_event", 
                                "find_free_time", "get_event_details", "list_calendars"]
                    },
                    "title": {
                        "type": "string",
                        "description": "Event title or summary"
                    },
                    "date": {
                        "type": "string",
                        "description": "Event date in YYYY-MM-DD format or natural language like 'today', 'tomorrow', 'next Monday'. For list_events, this sets both start and end date to the same day."
                    },
                    "time": {
                        "type": "string",
                        "description": "Event start time in HH:MM format (24-hour) or natural language like '2 PM', '9:30 AM'"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Event end time in HH:MM format (24-hour) or natural language"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Event duration in minutes (default: 60)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description or notes"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location or address"
                    },
                    "attendees": {
                        "type": "string",
                        "description": "Comma-separated list of attendee email addresses"
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Google Calendar event ID for update/delete operations"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for listing events (YYYY-MM-DD) or natural language"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for listing events (YYYY-MM-DD) or natural language"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default: 10)"
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (default: 'primary' for main calendar)"
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (default: system timezone)"
                    }
                },
                "required": ["action"]
            }
        }
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Google Calendar operation"""
        try:
            if not self.service:
                return {"error": "Google Calendar service not initialized"}
            
            if action == "create_event":
                return self._create_event(**kwargs)
            elif action == "list_events":
                return self._list_events(**kwargs)
            elif action == "update_event":
                return self._update_event(**kwargs)
            elif action == "delete_event":
                return self._delete_event(**kwargs)
            elif action == "find_free_time":
                return self._find_free_time(**kwargs)
            elif action == "get_event_details":
                return self._get_event_details(**kwargs)
            elif action == "list_calendars":
                return self._list_calendars(**kwargs)
            else:
                return {"error": f"Unknown calendar action: {action}"}
                
        except HttpError as e:
            return {"error": f"Google Calendar API error: {e}"}
        except Exception as e:
            return {"error": f"Calendar error: {str(e)}"}
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()
        
        # Handle natural language dates
        today = datetime.now()
        date_str = date_str.lower().strip()
        
        if date_str in ['today', 'now']:
            return today
        elif date_str == 'tomorrow':
            return today + timedelta(days=1)
        elif date_str == 'yesterday':
            return today - timedelta(days=1)
        elif date_str.startswith('next '):
            day_name = date_str[5:]
            days_ahead = self._get_days_until_weekday(day_name)
            if days_ahead is not None:
                return today + timedelta(days=days_ahead)
        
        # Try to parse as YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            pass
        
        # Try other common formats
        formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all else fails, return today
        return today
    
    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string and return (hour, minute)"""
        if not time_str:
            return (9, 0)  # Default to 9 AM
        
        time_str = time_str.lower().strip()
        
        # Handle AM/PM format
        if 'am' in time_str or 'pm' in time_str:
            is_pm = 'pm' in time_str
            time_str = time_str.replace('am', '').replace('pm', '').strip()
            
            if ':' in time_str:
                hour, minute = time_str.split(':')
                hour = int(hour)
                minute = int(minute)
            else:
                hour = int(time_str)
                minute = 0
            
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
                
            return (hour, minute)
        
        # Handle 24-hour format
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return (hour, minute)
        
        # Single number assumed to be hour
        hour = int(time_str)
        return (hour, 0)
    
    def _get_days_until_weekday(self, day_name: str) -> Optional[int]:
        """Get number of days until the specified weekday"""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        if day_name not in weekdays:
            return None
        
        today = datetime.now()
        days_ahead = weekdays[day_name] - today.weekday()
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        return days_ahead
    
    def _create_datetime(self, date_str: str, time_str: str, timezone_str: str = None) -> datetime:
        """Create datetime object from date and time strings"""
        date_obj = self._parse_date(date_str)
        hour, minute = self._parse_time(time_str)
        
        # Combine date and time
        dt = datetime.combine(date_obj.date(), datetime.min.time().replace(hour=hour, minute=minute))
        
        # Handle timezone - use local timezone by default
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                dt = tz.localize(dt)
            except:
                # Default to local timezone
                import time
                local_tz_name = time.tzname[0] if not time.daylight else time.tzname[1]
                try:
                    local_tz = pytz.timezone(local_tz_name)
                except:
                    local_tz = pytz.timezone('UTC')
                dt = local_tz.localize(dt)
        else:
            # Use local timezone instead of UTC
            import time
            try:
                # Try to get system timezone
                import platform
                if platform.system() == 'Windows':
                    # For Windows, try to detect timezone
                    local_tz = pytz.timezone('UTC')  # Fallback to UTC for Windows
                else:
                    local_tz_name = time.tzname[0] if not time.daylight else time.tzname[1]
                    local_tz = pytz.timezone(local_tz_name)
            except:
                local_tz = pytz.timezone('UTC')
            dt = local_tz.localize(dt)
        
        return dt
    
    def _create_event(self, title: str = None, date: str = None, time: str = None,
                     end_time: str = None, duration: int = 60, description: str = "",
                     location: str = "", attendees: str = "", calendar_id: str = None,
                     timezone: str = None) -> Dict[str, Any]:
        """Create a new Google Calendar event"""
        
        if not title:
            return {"error": "Event title is required"}
        
        # Use provided calendar_id or default
        cal_id = calendar_id or self.calendar_id
        
        try:
            # Parse start time
            start_dt = self._create_datetime(date or "today", time or "09:00", timezone)
            
            # Calculate end time
            if end_time:
                end_dt = self._create_datetime(date or "today", end_time, timezone)
            else:
                end_dt = start_dt + timedelta(minutes=duration)
            
            # Parse attendees
            attendee_list = []
            if attendees:
                emails = [email.strip() for email in attendees.split(',')]
                attendee_list = [{'email': email} for email in emails if email]
            
            # Create event object
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': str(start_dt.tzinfo),
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': str(end_dt.tzinfo),
                },
                'attendees': attendee_list,
                'reminders': {
                    'useDefault': True,
                },
            }
            
            # Create the event
            event_result = self.service.events().insert(calendarId=cal_id, body=event).execute()
            
            return {
                "action": "create_event",
                "event_id": event_result.get('id'),
                "event_link": event_result.get('htmlLink'),
                "event": {
                    "title": title,
                    "start": start_dt.strftime("%Y-%m-%d %H:%M"),
                    "end": end_dt.strftime("%Y-%m-%d %H:%M"),
                    "location": location,
                    "description": description,
                    "attendees": len(attendee_list)
                },
                "message": f"Event '{title}' created successfully for {start_dt.strftime('%Y-%m-%d at %H:%M')}"
            }
            
        except Exception as e:
            return {"error": f"Failed to create event: {str(e)}"}
    
    def _list_events(self, start_date: str = None, end_date: str = None,
                    max_results: int = 10, calendar_id: str = None, date: str = None) -> Dict[str, Any]:
        """List Google Calendar events"""
        
        cal_id = calendar_id or self.calendar_id
        
        try:
            # Handle convenience 'date' parameter
            if date and not start_date:
                start_date = date
            if date and not end_date:
                end_date = date
            
            # Parse date range - start from beginning of day
            if start_date:
                start_dt = self._parse_date(start_date)
                # Start from beginning of the day
                start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if end_date:
                end_dt = self._parse_date(end_date)
                # End at the end of the day
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                if date:
                    # If specific date requested, search only that day
                    end_dt = start_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    # Default to next 7 days
                    end_dt = start_dt + timedelta(days=7)
                    end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Ensure end_dt is after start_dt
            if end_dt <= start_dt:
                end_dt = start_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convert to UTC for Google Calendar API
            # Apply local timezone first, then convert to UTC
            import time
            try:
                import platform
                if platform.system() == 'Windows':
                    local_tz = pytz.timezone('UTC')  # Fallback to UTC for Windows
                else:
                    local_tz_name = time.tzname[0] if not time.daylight else time.tzname[1]
                    local_tz = pytz.timezone(local_tz_name)
            except:
                local_tz = pytz.timezone('UTC')
            
            # Localize to timezone then convert to UTC
            start_dt_tz = local_tz.localize(start_dt)
            end_dt_tz = local_tz.localize(end_dt)
            
            start_dt_utc = start_dt_tz.astimezone(pytz.UTC)
            end_dt_utc = end_dt_tz.astimezone(pytz.UTC)
            
            # Convert to ISO format for API
            time_min = start_dt_utc.isoformat()
            time_max = end_dt_utc.isoformat()
            
            print(f"[DEBUG] Calendar search range: {time_min} to {time_max}")
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            print(f"[DEBUG] Found {len(events)} events in Google Calendar")
            
            # Format events for display
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse datetime
                if 'T' in start:  # DateTime format
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    start_str = start_dt.strftime("%Y-%m-%d %H:%M")
                    end_str = end_dt.strftime("%H:%M")
                else:  # Date only format
                    start_str = start
                    end_str = "All day"
                
                formatted_events.append({
                    "id": event.get('id'),
                    "title": event.get('summary', 'No title'),
                    "start": start_str,
                    "end": end_str,
                    "location": event.get('location', ''),
                    "description": event.get('description', ''),
                    "attendees": len(event.get('attendees', [])),
                    "link": event.get('htmlLink', '')
                })
            
            return {
                "action": "list_events",
                "events": formatted_events,
                "count": len(formatted_events),
                "date_range": f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            print(f"[DEBUG] Calendar list error: {str(e)}")
            return {"error": f"Failed to list events: {str(e)}"}
    
    def _update_event(self, event_id: str = None, calendar_id: str = None, **kwargs) -> Dict[str, Any]:
        """Update an existing Google Calendar event"""
        
        if not event_id:
            return {"error": "Event ID is required for updates"}
        
        cal_id = calendar_id or self.calendar_id
        
        try:
            # Get the existing event
            event = self.service.events().get(calendarId=cal_id, eventId=event_id).execute()
            
            # Update fields based on provided parameters
            if 'title' in kwargs and kwargs['title']:
                event['summary'] = kwargs['title']
            
            if 'description' in kwargs and kwargs['description'] is not None:
                event['description'] = kwargs['description']
            
            if 'location' in kwargs and kwargs['location'] is not None:
                event['location'] = kwargs['location']
            
            # Handle time updates
            if 'date' in kwargs or 'time' in kwargs:
                date_str = kwargs.get('date', '')
                time_str = kwargs.get('time', '')
                timezone_str = kwargs.get('timezone', '')
                
                if date_str or time_str:
                    # Get current start time as fallback
                    current_start = event['start'].get('dateTime', event['start'].get('date'))
                    current_dt = datetime.fromisoformat(current_start.replace('Z', '+00:00'))
                    
                    # Create new start time
                    if not date_str:
                        date_str = current_dt.strftime('%Y-%m-%d')
                    if not time_str:
                        time_str = current_dt.strftime('%H:%M')
                    
                    new_start_dt = self._create_datetime(date_str, time_str, timezone_str)
                    
                    # Calculate duration to preserve it
                    current_end = event['end'].get('dateTime', event['end'].get('date'))
                    current_end_dt = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
                    duration = current_end_dt - current_dt
                    
                    new_end_dt = new_start_dt + duration
                    
                    # Update start and end times
                    event['start'] = {
                        'dateTime': new_start_dt.isoformat(),
                        'timeZone': str(new_start_dt.tzinfo),
                    }
                    event['end'] = {
                        'dateTime': new_end_dt.isoformat(),
                        'timeZone': str(new_end_dt.tzinfo),
                    }
            
            # Handle attendees update
            if 'attendees' in kwargs and kwargs['attendees'] is not None:
                if kwargs['attendees']:
                    emails = [email.strip() for email in kwargs['attendees'].split(',')]
                    event['attendees'] = [{'email': email} for email in emails if email]
                else:
                    event['attendees'] = []
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=cal_id, eventId=event_id, body=event
            ).execute()
            
            return {
                "action": "update_event",
                "event_id": event_id,
                "event_link": updated_event.get('htmlLink'),
                "message": f"Event '{event.get('summary')}' updated successfully"
            }
            
        except HttpError as e:
            if e.resp.status == 404:
                return {"error": f"Event with ID {event_id} not found"}
            else:
                return {"error": f"Failed to update event: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to update event: {str(e)}"}
    
    def _delete_event(self, event_id: str = None, calendar_id: str = None) -> Dict[str, Any]:
        """Delete a Google Calendar event"""
        
        if not event_id:
            return {"error": "Event ID is required for deletion"}
        
        cal_id = calendar_id or self.calendar_id
        
        try:
            # Get event details before deletion
            event = self.service.events().get(calendarId=cal_id, eventId=event_id).execute()
            event_title = event.get('summary', 'Unknown')
            
            # Delete the event
            self.service.events().delete(calendarId=cal_id, eventId=event_id).execute()
            
            return {
                "action": "delete_event",
                "event_id": event_id,
                "event_title": event_title,
                "message": f"Event '{event_title}' deleted successfully"
            }
            
        except HttpError as e:
            if e.resp.status == 404:
                return {"error": f"Event with ID {event_id} not found"}
            else:
                return {"error": f"Failed to delete event: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to delete event: {str(e)}"}
    
    def _get_event_details(self, event_id: str = None, calendar_id: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific event"""
        
        if not event_id:
            return {"error": "Event ID is required"}
        
        cal_id = calendar_id or self.calendar_id
        
        try:
            event = self.service.events().get(calendarId=cal_id, eventId=event_id).execute()
            
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Format attendees
            attendees = event.get('attendees', [])
            attendee_info = []
            for attendee in attendees:
                attendee_info.append({
                    'email': attendee.get('email'),
                    'status': attendee.get('responseStatus', 'needsAction'),
                    'optional': attendee.get('optional', False)
                })
            
            return {
                "action": "get_event_details",
                "event": {
                    "id": event.get('id'),
                    "title": event.get('summary', 'No title'),
                    "description": event.get('description', ''),
                    "location": event.get('location', ''),
                    "start": start,
                    "end": end,
                    "attendees": attendee_info,
                    "creator": event.get('creator', {}).get('email', 'Unknown'),
                    "link": event.get('htmlLink', ''),
                    "status": event.get('status', 'confirmed')
                }
            }
            
        except HttpError as e:
            if e.resp.status == 404:
                return {"error": f"Event with ID {event_id} not found"}
            else:
                return {"error": f"Failed to get event details: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get event details: {str(e)}"}
    
    def _list_calendars(self) -> Dict[str, Any]:
        """List available calendars"""
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            formatted_calendars = []
            for cal in calendars:
                formatted_calendars.append({
                    "id": cal.get('id'),
                    "name": cal.get('summary'),
                    "description": cal.get('description', ''),
                    "primary": cal.get('primary', False),
                    "access_role": cal.get('accessRole', 'reader')
                })
            
            return {
                "action": "list_calendars",
                "calendars": formatted_calendars,
                "count": len(formatted_calendars)
            }
            
        except Exception as e:
            return {"error": f"Failed to list calendars: {str(e)}"}
    
    def _find_free_time(self, date: str = None, duration: int = 60, 
                       calendar_id: str = None, work_start: str = "09:00",
                       work_end: str = "17:00") -> Dict[str, Any]:
        """Find free time slots on a given date"""
        
        cal_id = calendar_id or self.calendar_id
        
        try:
            # Parse target date
            target_date = self._parse_date(date or "today")
            
            # Get events for the day
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            events_result = self.service.events().list(
                calendarId=cal_id,
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Parse work hours
            work_start_hour, work_start_min = self._parse_time(work_start)
            work_end_hour, work_end_min = self._parse_time(work_end)
            
            work_start_dt = target_date.replace(hour=work_start_hour, minute=work_start_min)
            work_end_dt = target_date.replace(hour=work_end_hour, minute=work_end_min)
            
            # Find free slots
            free_slots = []
            current_time = work_start_dt
            
            for event in events:
                event_start = event['start'].get('dateTime')
                event_end = event['end'].get('dateTime')
                
                if event_start and event_end:
                    event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                    
                    # Convert to local date if needed
                    if event_start_dt.date() == target_date.date():
                        if current_time < event_start_dt:
                            slot_duration = int((event_start_dt - current_time).total_seconds() / 60)
                            if slot_duration >= duration:
                                free_slots.append({
                                    "start_time": current_time.strftime("%H:%M"),
                                    "end_time": event_start_dt.strftime("%H:%M"),
                                    "duration_available": slot_duration
                                })
                        
                        current_time = max(current_time, event_end_dt)
            
            # Check for time after last event
            if current_time < work_end_dt:
                slot_duration = int((work_end_dt - current_time).total_seconds() / 60)
                if slot_duration >= duration:
                    free_slots.append({
                        "start_time": current_time.strftime("%H:%M"),
                        "end_time": work_end_dt.strftime("%H:%M"),
                        "duration_available": slot_duration
                    })
            
            return {
                "action": "find_free_time",
                "date": target_date.strftime("%Y-%m-%d"),
                "requested_duration": duration,
                "work_hours": f"{work_start} - {work_end}",
                "free_slots": free_slots,
                "message": f"Found {len(free_slots)} free time slots on {target_date.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            return {"error": f"Failed to find free time: {str(e)}"} 