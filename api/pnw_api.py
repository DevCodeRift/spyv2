"""
Politics & War API wrapper
Handles GraphQL queries to the Politics & War API
"""

import requests
import json
import urllib.parse
from typing import Dict, Any, Optional

class PoliticsAndWarAPI:
    """API wrapper for Politics & War GraphQL API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.politicsandwar.com/graphql"
    
    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query
        
        Args:
            query: GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            Dict containing the API response
        """
        # URL encode the query
        encoded_query = urllib.parse.quote(query)
        
        # Build the full URL
        url = f"{self.base_url}?api_key={self.api_key}&query={encoded_query}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {"errors": [{"message": str(e)}]}
    
    def get_nation(self, nation_id: int = None) -> Dict[str, Any]:
        """Get nation information"""
        if nation_id:
            query = f"{{nations(id:{nation_id}){{data{{nation_name leader_name alliance{{name}} score cities{{name}}}}}}}}"
        else:
            query = "{me{nation{nation_name leader_name alliance{name} score cities{name}}}}"
        
        return self.query(query)
    
    def get_alliance(self, alliance_id: int) -> Dict[str, Any]:
        """Get alliance information"""
        query = f"{{alliances(id:{alliance_id}){{data{{name acronym score nations{{data{{nation_name}}}}}}}}}}"
        return self.query(query)
    
    def get_wars(self, active_only: bool = True) -> Dict[str, Any]:
        """Get war information"""
        query = "{wars{data{id date reason attacker{nation_name} defender{nation_name} turns_left}}}"
        return self.query(query)
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get basic game information"""
        query = "{game_info{game_date radiation{global north_america south_america europe africa asia australia antarctica}}}"
        return self.query(query)
    
    def search_nations(self, name: str = None, alliance_id: int = None, limit: int = 10) -> Dict[str, Any]:
        """Search for nations"""
        filters = []
        if name:
            filters.append(f'nation_name:"{name}"')
        if alliance_id:
            filters.append(f'alliance_id:{alliance_id}')
        
        filter_string = f"({','.join(filters)})" if filters else ""
        query = f"{{nations{filter_string}{{data{{nation_name leader_name alliance{{name}} score}}}}}}"
        
        return self.query(query)
    
    def get_spy_activity(self, nation_id: int = None) -> Dict[str, Any]:
        """Get spy-related activity for a nation"""
        if nation_id:
            query = f"{{nations(id:[{nation_id}]){{data{{nation_name spy_casualties spy_kills spy_attacks espionage_available last_active}}}}}}"
        else:
            query = "{me{nation{nation_name spy_casualties spy_kills spy_attacks espionage_available last_active}}}"
        
        return self.query(query)
    
    def check_recent_attacks(self, nation_id: int = None, hours: int = 24) -> Dict[str, Any]:
        """Check for recent attacks on or by a nation"""
        from datetime import datetime, timedelta
        
        # Calculate the time threshold
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        time_str = time_ago.strftime("%Y-%m-%dT%H:%M:%S")
        
        if nation_id:
            # Check attacks involving this specific nation
            query = f"{{warattacks(after:\"{time_str}\"){{data{{id date type attacker{{id nation_name}} defender{{id nation_name}} success}}}}}}"
        else:
            # Check recent attacks in general
            query = f"{{warattacks(after:\"{time_str}\",first:50){{data{{id date type attacker{{nation_name}} defender{{nation_name}} success}}}}}}"
        
        return self.query(query)
    
    def get_active_wars(self, nation_id: int = None) -> Dict[str, Any]:
        """Get active wars for a nation"""
        if nation_id:
            query = f"{{wars(nation_id:[{nation_id}],active:true){{data{{id date reason attacker{{nation_name}} defender{{nation_name}} turns_left attacks{{type date}}}}}}}}"
        else:
            query = "{me{nation{wars(active:true){id date reason attacker{nation_name} defender{nation_name} turns_left attacks{type date}}}}}"
        
        return self.query(query)
    
    def check_espionage_status(self, nation_id: int = None) -> Dict[str, Any]:
        """Check if a nation is available for espionage and recent spy activity"""
        if nation_id:
            query = f"{{nations(id:[{nation_id}]){{data{{nation_name espionage_available spy_casualties spy_kills beige_turns vacation_mode_turns last_active}}}}}}"
        else:
            query = "{me{nation{nation_name espionage_available spy_casualties spy_kills beige_turns vacation_mode_turns last_active}}}"
        
        return self.query(query)
