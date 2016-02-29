#!/bin/bash

# NOTE: Run this script in the root project

echo "Deleting all .pyc files from project..."
find . -name '*.pyc' -delete

echo "Deleting all .swp files from project..."
find . -name '*.swp' -delete
