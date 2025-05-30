import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

class CalendarScheduler:
    """Calendar scheduling tool (placeholder implementation)"""
    
    def __init__(self):
        # Mock calendar storage
        self.events = []
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "calendar_scheduler",
            "description": "Manage calendar events including creating, viewing, updating, and deleting appointments",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Calendar action to perform",
                        "enum": ["create_event", "list_events", "update_event", "delete_event", "find_free_time"]
                    },
                    "title": {
                        "type": "string",
                        "description": "Event title or name"
                    },
                    "date": {
                        "type": "string",
                        "description": "Event date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Event time in HH:MM format (24-hour)"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Event duration in minutes (default: 60)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description or notes"
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Event ID for update/delete operations"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for listing events (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for listing events (YYYY-MM-DD)"
                    }
                },
                "required": ["action"]
            }
        }
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute calendar operation"""
        try:
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
            else:
                return {"error": f"Unknown calendar action: {action}"}
        except Exception as e:
            return {"error": f"Calendar error: {str(e)}"}
    
    def _create_event(self, title: str = None, date: str = None, time: str = None, 
                     duration: int = 60, description: str = "") -> Dict[str, Any]:
        """Create a new calendar event"""
        if not title:
            return {"error": "Event title is required"}
        if not date:
            return {"error": "Event date is required"}
        if not time:
            return {"error": "Event time is required"}
        
        try:
            # Validate date and time format
            event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM"}
        
        event_id = str(uuid.uuid4())[:8]
        event = {
            "id": event_id,
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        self.events.append(event)
        
        return {
            "action": "create_event",
            "event": event,
            "message": f"Event '{title}' scheduled for {date} at {time} (Duration: {duration} minutes)"
        }
    
    def _list_events(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """List calendar events"""
        if not start_date:
            # Default to today
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        if not end_date:
            # Default to 7 days from start_date
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=7)
            end_date = end_dt.strftime("%Y-%m-%d")
        
        filtered_events = []
        for event in self.events:
            if start_date <= event["date"] <= end_date:
                filtered_events.append(event)
        
        # Sort events by date and time
        filtered_events.sort(key=lambda x: (x["date"], x["time"]))
        
        return {
            "action": "list_events",
            "events": filtered_events,
            "count": len(filtered_events),
            "date_range": f"{start_date} to {end_date}"
        }
    
    def _update_event(self, event_id: str = None, **kwargs) -> Dict[str, Any]:
        """Update an existing event"""
        if not event_id:
            return {"error": "Event ID is required for updates"}
        
        for event in self.events:
            if event["id"] == event_id:
                # Update provided fields
                for key, value in kwargs.items():
                    if key in event and value is not None:
                        event[key] = value
                
                return {
                    "action": "update_event",
                    "event": event,
                    "message": f"Event '{event['title']}' updated successfully"
                }
        
        return {"error": f"Event with ID {event_id} not found"}
    
    def _delete_event(self, event_id: str = None) -> Dict[str, Any]:
        """Delete an event"""
        if not event_id:
            return {"error": "Event ID is required for deletion"}
        
        for i, event in enumerate(self.events):
            if event["id"] == event_id:
                deleted_event = self.events.pop(i)
                return {
                    "action": "delete_event",
                    "deleted_event": deleted_event,
                    "message": f"Event '{deleted_event['title']}' deleted successfully"
                }
        
        return {"error": f"Event with ID {event_id} not found"}
    
    def _find_free_time(self, date: str = None, duration: int = 60) -> Dict[str, Any]:
        """Find free time slots on a given date"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get events for the specified date
        day_events = [event for event in self.events if event["date"] == date]
        day_events.sort(key=lambda x: x["time"])
        
        # Generate free time slots (simplified logic)
        work_start = "09:00"
        work_end = "17:00"
        
        free_slots = []
        current_time = work_start
        
        for event in day_events:
            if current_time < event["time"]:
                # Calculate duration until next event
                current_dt = datetime.strptime(current_time, "%H:%M")
                event_dt = datetime.strptime(event["time"], "%H:%M")
                available_minutes = int((event_dt - current_dt).total_seconds() / 60)
                
                if available_minutes >= duration:
                    free_slots.append({
                        "start_time": current_time,
                        "end_time": event["time"],
                        "duration_available": available_minutes
                    })
            
            # Move to after this event
            event_dt = datetime.strptime(event["time"], "%H:%M")
            event_end_dt = event_dt + timedelta(minutes=event["duration"])
            current_time = event_end_dt.strftime("%H:%M")
        
        # Check for time after last event
        if current_time < work_end:
            current_dt = datetime.strptime(current_time, "%H:%M")
            end_dt = datetime.strptime(work_end, "%H:%M")
            available_minutes = int((end_dt - current_dt).total_seconds() / 60)
            
            if available_minutes >= duration:
                free_slots.append({
                    "start_time": current_time,
                    "end_time": work_end,
                    "duration_available": available_minutes
                })
        
        return {
            "action": "find_free_time",
            "date": date,
            "requested_duration": duration,
            "free_slots": free_slots,
            "message": f"Found {len(free_slots)} free time slots on {date}"
        } 