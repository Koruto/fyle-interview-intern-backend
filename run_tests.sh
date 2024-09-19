#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [--coverage | --test | --cov-report]"
    echo "  --coverage    Run tests and generate a basic coverage report."
    echo "  --test         Run tests with verbose output (default if no argument is provided)."
    echo "  --cov-report   Generate a detailed coverage report in HTML format."
    exit 1
}

# Determine the mode based on the argument or default to 'test'
MODE="test"  # Default mode

case "$1" in
    --coverage)
        MODE="coverage"
        ;;
    --test)
        MODE="test"
        ;;
    --cov-report)
        MODE="cov-report"
        ;;
    "")
        # No argument provided, default mode is 'test'
        MODE="test"
        ;;
    *)
        usage
        ;;
esac

# Remove existing SQLite database
rm -f core/store.sqlite3

export FLASK_APP=core.server.py

flask db upgrade -d core/migrations/

# Run tests based on the selected mode
if [ "$MODE" == "coverage" ]; then
    echo "Generating basic coverage report..."
    pytest --cov
elif [ "$MODE" == "cov-report" ]; then
    echo "Generating detailed coverage report in HTML format..."
    pytest --cov --cov-report=html tests/
elif [ "$MODE" == "test" ]; then
    echo "Running tests with verbose output..."
    pytest -vvv -s tests/
fi
