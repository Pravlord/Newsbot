#!/bin/bash

# Function to run FastAPI with auto-restart
run_fastapi() {
    while true; do
        echo "[$(date)] Starting FastAPI service..."
        uvicorn social_post_service:app --host 0.0.0.0 --port 8000
        echo "[$(date)] FastAPI exited, restarting in 5s..."
        sleep 5
    done
}

# Function to run bot with auto-restart
run_bot() {
    while true; do
        echo "[$(date)] Starting NewsWrite bot..."
        python main.py
        echo "[$(date)] Bot exited, restarting in 5s..."
        sleep 5
    done
}

# Start both with auto-restart
run_fastapi &
run_bot &

# Wait for both (keeps container alive)
wait