#!/bin/bash
# Comprehensive spy functionality test for Politics & War API

echo "🕵️ Politics & War Spy Activity Test"
echo "===================================="

API_KEY="05e5e3753de6b6f257f4"
BASE_URL="https://api.politicsandwar.com/graphql"

echo ""
echo "1. Testing Own Nation Spy Status:"
echo "--------------------------------"
QUERY='{me{nation{nation_name spy_casualties spy_kills spy_attacks espionage_available}}}'
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g')
curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}" | python3 -m json.tool 2>/dev/null || curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"

echo ""
echo ""
echo "2. Testing Espionage Protection Status:"
echo "--------------------------------------"
QUERY='{me{nation{nation_name espionage_available beige_turns vacation_mode_turns last_active}}}'
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g')
curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"

echo ""
echo ""
echo "3. Testing Active Wars:"
echo "----------------------"
QUERY='{me{nation{nation_name wars(active:true){id attacker{nation_name} defender{nation_name} turns_left}}}}'
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g' | sed 's/(/%28/g' | sed 's/)/%29/g' | sed 's/:/%3A/g')
curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"

echo ""
echo ""
echo "4. Testing Nation Search (example: 'Test'):"
echo "-------------------------------------------"
QUERY='{nations(nation_name:["Test"],first:3){data{nation_name leader_name spy_casualties spy_kills espionage_available}}}'
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g' | sed 's/(/%28/g' | sed 's/)/%29/g' | sed 's/:/%3A/g' | sed 's/\[/%5B/g' | sed 's/\]/%5D/g' | sed 's/"/%22/g' | sed 's/,/%2C/g')
curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"

echo ""
echo ""
echo "5. Testing Central Intelligence Agency Project:"
echo "----------------------------------------------"
QUERY='{me{nation{nation_name central_intelligence_agency spy_satellite surveillance_network}}}'
ENCODED_QUERY=$(echo "$QUERY" | sed 's/{/%7B/g' | sed 's/}/%7D/g' | sed 's/ /%20/g')
curl -s "${BASE_URL}?api_key=${API_KEY}&query=${ENCODED_QUERY}"

echo ""
echo ""
echo "Test completed! 🎯"
echo "=================="
