#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the battle..."
  # response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
  #   -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price.0, \"difficulty\":\"$difficulty\"}") #| grep -q "{\"status\": \"combatant added\",\"combatant\": \"$meal\"}"
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  
  if echo "$response" | grep -q '"status": "combatant added"'; then 
    echo "Meal added"
  else 
    echo "Failed to add meal"
    exit 1
  fi
}
clear_catalogue() {
  echo "Clearing the catalogue..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}


delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": *"meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  echo $response
  if echo "$response" | grep -q '"status": *"success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal=$1

  echo "Getting meal by name ($meal)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$(echo $meal | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $meal):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal)."
    exit 1
  fi
}

prep_combatant() {
  meal=$1

  echo "Preping combatant for battle: $meal ..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Combatant prepped succesfully"
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo $response
    echo "Failed to prep combatant"
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

get_combatants() {  
  echo "Retrieving all combatants for the battle..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all combatants."
    exit 1
  fi
}

battle() {
  echo "Entering battle..."

  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "battle complete"'; then
    echo "Battle finished successfully."
    echo "The winner of the battle is "
    echo "$response" | jq .winner
  else
    echo $response
    echo "Failed to start battle."
    exit 1
  fi
}

# Function to get the song leaderboard sorted by play count
get_leaderboard() {
  ECHO_JSON=true
  sort=$1
  echo "Getting meal leaderboard sorted by $sort..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal leaderboard JSON (sorted by $sort):"
      echo "$response" | jq .
    fi
  else
    echo $response 
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}



# Health checks
check_health
check_db

# Create meals
create_meal "Meal A" "Cuisine A" 1 "LOW"
create_meal "Meal B" "Cuisine B" 3 "LOW"
create_meal "Meal C" "Cuisine C" 5 "MED"
create_meal "Meal D" "Cuisine D" 7 "MED"
create_meal "Meal E" "Cuisine E" 9 "HIGH"

get_meal_by_id 1
get_meal_by_name "Meal A"

delete_meal_by_id 1

prep_combatant "Meal B" "Cuisine B" 3 "LOW"
prep_combatant "Meal C" "Cuisine C" 5 "MED"

get_combatants
battle
get_leaderboard "wins"

clear_combatants


prep_combatant "Meal C" "Cuisine C" 5 "MED"
prep_combatant "Meal E" "Cuisine E" 9 "HIGH"

get_combatants
battle
get_leaderboard "win_pct"

clear_combatants

echo "All tests passed successfully!"