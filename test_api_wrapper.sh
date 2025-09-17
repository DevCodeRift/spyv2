#!/bin/bash
# Test the API wrapper functionality

echo "Testing Politics & War API wrapper..."
echo "======================================"

# Test multiple API endpoints
echo ""
echo "1. Testing Game Info:"
curl -s "https://api.politicsandwar.com/graphql?api_key=05e5e3753de6b6f257f4&query=%7Bgame_info%7Bgame_date%7D%7D"

echo ""
echo "2. Testing Nation Info (your nation):"
curl -s "https://api.politicsandwar.com/graphql?api_key=05e5e3753de6b6f257f4&query=%7Bme%7Bnation%7Bnation_name%20leader_name%20score%7D%7D%7D"

echo ""
echo "3. Testing API Key Details:"
curl -s "https://api.politicsandwar.com/graphql?api_key=05e5e3753de6b6f257f4&query=%7Bme%7Bkey%20requests%20max_requests%7D%7D"

echo ""
echo "4. Testing Colors:"
curl -s "https://api.politicsandwar.com/graphql?api_key=05e5e3753de6b6f257f4&query=%7Bcolors%7Bcolor%20bonus%7D%7D"

echo ""
echo "API wrapper testing complete!"
echo "======================================"
