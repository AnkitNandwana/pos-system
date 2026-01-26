#!/bin/bash

# Test runner script for plugin tests using Django TestCase

PLUGIN_NAME=${1:-"all"}
VERBOSE=${2:-""}

if [ "$PLUGIN_NAME" = "all" ]; then
    echo "Running tests for all plugins..."
    echo
    
    if [ "$VERBOSE" = "-v" ]; then
        python manage.py test plugins.employee_time_tracker plugins.customer_lookup plugins.purchase_recommender plugins.fraud_detection plugins.age_verification --verbosity=2
    else
        python manage.py test plugins.employee_time_tracker plugins.customer_lookup plugins.purchase_recommender plugins.fraud_detection plugins.age_verification
    fi
else
    echo "Running tests for $PLUGIN_NAME plugin..."
    echo
    
    if [ "$VERBOSE" = "-v" ]; then
        python manage.py test plugins.$PLUGIN_NAME --verbosity=2
    else
        python manage.py test plugins.$PLUGIN_NAME
    fi
fi