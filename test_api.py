#!/usr/bin/env python3
"""
Test script for Politics & War GraphQL API
"""
import requests
import urllib.parse
import json

# API configuration
API_KEY = "05e5e3753de6b6f257f4"
BASE_URL = "https://api.politicsandwar.com/graphql"

def test_api():
    """Test the Politics & War API with a simple query"""
    
    # Simple query to get basic nation info
    query = """
    {
        me {
            nation {
                nation_name
                leader_name
                score
                num_cities
                alliance {
                    name
                    acronym
                }
            }
            requests
            max_requests
        }
    }
    """
    
    # Method 1: Using URL parameters (as described in the docs)
    print("Testing API with URL parameters...")
    encoded_query = urllib.parse.quote(query.strip())
    url = f"{BASE_URL}?api_key={API_KEY}&query={encoded_query}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response (URL method):")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error with URL method: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Method 2: Using POST with JSON body (alternative method)
    print("Testing API with POST method...")
    headers = {
        'Content-Type': 'application/json',
    }
    
    payload = {
        'query': query.strip()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}?api_key={API_KEY}",
            headers=headers,
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response (POST method):")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error with POST method: {e}")

if __name__ == "__main__":
    test_api()
