#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the database initialization script
python -m app.db.init_db

echo "Database initialization completed" 