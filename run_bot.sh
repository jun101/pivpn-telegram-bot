#!/bin/bash

# Activate the virtual environment
source ./venv/bin/activate

# Run the bot module
python -m bot.main

# Optionally, deactivate after running (not necessary if script exits)
deactivate
