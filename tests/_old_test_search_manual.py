#!/usr/bin/env python3
"""Test script to check search API response"""

import requests
import json

# Test without auth to see what happens
response = requests.get("http://localhost:5000/api/search/?page=1&limit=3")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
