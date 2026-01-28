#!/bin/bash

# Login as student1
STUDENT_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"Felly","password":"Felicia@2025"}' | jq -r .access)

# Login as instructor1
INSTRUCTOR_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"Costa","password":"Felicia@2025"}' | jq -r .access)

# Login as admin1
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"Paulus","password":"Felicia@2025"}' | jq -r .access)

# Export tokens as environment variables
export STUDENT_TOKEN
export INSTRUCTOR_TOKEN
export ADMIN_TOKEN

echo "Student token: $STUDENT_TOKEN"
echo "Instructor token: $INSTRUCTOR_TOKEN"
echo "Admin token: $ADMIN_TOKEN"
