#!/usr/bin/env bash

# Quickly stup the database for manual testing
# when a reset is needed

set -e

BASE_URL="http://localhost:8000"
EMAIL="user@example.com"
PASSWORD="password123"
TODAY=`date '+%Y-%m-%d'`

echo "==> Registering user..."
curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Test User\"
  }" > /dev/null || true

echo "==> Logging in..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD" \
  | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "Failed to obtain access token"
  exit 1
fi

echo "Authenticated"

echo "==> Creating account..."
ACCOUNT_ID=$(curl -s -X POST "$BASE_URL/api/accounts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Account",
    "currency_code": "USD",
    "description": "Primary account"
  }' | jq -r '.id')

echo "Account created: ID=$ACCOUNT_ID"

echo "==> Creating transaction..."
curl -s -X POST "$BASE_URL/api/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account_id\": $ACCOUNT_ID,
    \"category_id\": 1,
    \"type\": \"expense\",
    \"amount\": 25.50,
    \"description\": \"Coffee\",
    \"date\": \"$TODAY\"
  }" > /dev/null

echo "Transaction created"
echo "Bootstrap complete!"

