#!/bin/bash
# Run compare_prices.py with RAPIDAPI_KEY. Use this in cron.
# On the server: create .env.rapidapi with: export RAPIDAPI_KEY="your_key"
# Then: chmod +x run_compare_prices.sh && chmod 600 .env.rapidapi
# Cron: 0 6 * * * /home/ubuntu/grocery-api/run_compare_prices.sh
cd "$(dirname "$0")"
[ -f .env.rapidapi ] && source .env.rapidapi
./venv/bin/python compare_prices.py
