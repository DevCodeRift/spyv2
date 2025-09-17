"""
Utility functions for the Politics & War Discord Bot
"""

import json
import datetime
from typing import Dict, Any, List

def format_number(number: float) -> str:
    """Format large numbers with commas"""
    if isinstance(number, (int, float)):
        return f"{number:,.2f}" if isinstance(number, float) else f"{number:,}"
    return str(number)

def format_date(date_string: str) -> str:
    """Format ISO date string to readable format"""
    try:
        dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except:
        return date_string

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = "Unknown") -> Any:
    """Safely get a value from a dictionary"""
    return dictionary.get(key, default)

def calculate_nation_strength(nation_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate various strength metrics for a nation"""
    soldiers = safe_get(nation_data, 'soldiers', 0)
    tanks = safe_get(nation_data, 'tanks', 0)
    aircraft = safe_get(nation_data, 'aircraft', 0)
    ships = safe_get(nation_data, 'ships', 0)
    
    # Basic military strength calculation
    military_strength = (soldiers * 1) + (tanks * 40) + (aircraft * 20) + (ships * 30)
    
    return {
        'military_strength': military_strength,
        'soldiers': soldiers,
        'tanks': tanks,
        'aircraft': aircraft,
        'ships': ships
    }

def create_nation_embed_data(nation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create structured data for Discord embeds"""
    return {
        'name': safe_get(nation_data, 'nation_name'),
        'leader': safe_get(nation_data, 'leader_name'),
        'alliance': safe_get(nation_data.get('alliance', {}), 'name', 'None'),
        'score': format_number(safe_get(nation_data, 'score', 0)),
        'cities': len(nation_data.get('cities', [])),
        'founded': format_date(safe_get(nation_data, 'date', '')),
        'last_active': format_date(safe_get(nation_data, 'last_active', ''))
    }

def validate_api_response(response: Dict[str, Any]) -> bool:
    """Validate that an API response is successful"""
    return 'errors' not in response and 'data' in response

def extract_error_message(response: Dict[str, Any]) -> str:
    """Extract error message from API response"""
    if 'errors' in response and response['errors']:
        return response['errors'][0].get('message', 'Unknown error')
    return 'Unknown error occurred'
