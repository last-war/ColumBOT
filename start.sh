#!/bin/bash

# Apply Alembic migrations
alembic upgrade heads

# Start your application
uvicorn main:app --host localhost --port 8000 --reload