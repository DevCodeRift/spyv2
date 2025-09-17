#!/bin/bash
# Test script for Politics & War API

API_KEY="05e5e3753de6b6f257f4"
BASE_URL="https://api.politicsandwar.com/graphql"

# Query to check espionage status
QUERY='{me{nation{nation_name espionage_available spy_casualties spy_kills beige_turns vacation_mode_turns last_active}}}'

# URL encode the query
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g')

echo "Testing Politics & War API..."
echo "API Key: $API_KEY"
echo "Query: $QUERY"
echo "Encoded Query: $ENCODED_QUERY"
echo ""

# Make the request
curl -w "\n" "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"
