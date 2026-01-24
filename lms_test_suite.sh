#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"

# Full access tokens (updated)
STUDENT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.rA34ndToQHGiuNsP9WlEsediQJOQsk-zM73zbAMwmB4"
INSTRUCTOR_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.K9h15ZivGsMgJD3a3aZccpQiYamGAA5lPLmIxUiX2V8"
ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.K06AE1qelZCIVNgr3DtQesnNCwb3WC2dVnVjYiHzLnE"

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m" # No Color

check_status() {
  if [[ "$1" == "200" || "$1" == "201" ]]; then
    echo -e "${GREEN}$2 → $1 (SUCCESS)${NC}"
  else
    echo -e "${RED}$2 → $1 (FAILURE)${NC}"
  fi
}

echo "=== COURSES ==="
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/courses/ -H "Authorization: Bearer ${STUDENT_TOKEN}")
check_status $status "Student GET /courses"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/courses/ -H "Authorization: Bearer ${ADMIN_TOKEN}")
check_status $status "Admin GET /courses"

echo
echo "=== ENROLLMENTS ==="
# Student enrolls in Math 101 (course ID 1)
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/enrollments/ \
  -H "Authorization: Bearer ${STUDENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"course":1}')
check_status $status "Student POST /enrollments (Math 101)"

# Duplicate enrollment attempt
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/enrollments/ \
  -H "Authorization: Bearer ${STUDENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"course":1}')
check_status $status "Student duplicate enrollment"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/enrollments/ -H "Authorization: Bearer ${INSTRUCTOR_TOKEN}")
check_status $status "Instructor GET /enrollments"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/enrollments/ -H "Authorization: Bearer ${ADMIN_TOKEN}")
check_status $status "Admin GET /enrollments"

echo
echo "=== ASSIGNMENTS ==="
# Instructor creates assignment for Biology 101 (course ID 5)
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/assignments/ \
  -H "Authorization: Bearer ${INSTRUCTOR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"course":5,"title":"Homework 1","description":"Solve algebra problems","due_date":"2026-02-01"}')
check_status $status "Instructor POST /assignments (Biology 101)"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/assignments/ -H "Authorization: Bearer ${STUDENT_TOKEN}")
check_status $status "Student GET /assignments"

echo
echo "=== GRADES ==="
# Student submits assignment 1
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/assignments/submit/ \
  -H "Authorization: Bearer ${STUDENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"assignment":1,"content":"My solution to assignment 1"}')
check_status $status "Student POST /assignments/submit"

# Instructor grades submission 1
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/grades/ \
  -H "Authorization: Bearer ${INSTRUCTOR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"submission":1,"score":85,"feedback":"Good work, but improve clarity"}')
check_status $status "Instructor POST /grades"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/grades/ -H "Authorization: Bearer ${STUDENT_TOKEN}")
check_status $status "Student GET /grades"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/grades/ -H "Authorization: Bearer ${ADMIN_TOKEN}")
check_status $status "Admin GET /grades"

echo
echo "=== ANALYTICS ==="
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/analytics/student/ -H "Authorization: Bearer ${STUDENT_TOKEN}")
check_status $status "Student GET /analytics/student"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/analytics/instructor/ -H "Authorization: Bearer ${INSTRUCTOR_TOKEN}")
check_status $status "Instructor GET /analytics/instructor"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/analytics/admin/ -H "Authorization: Bearer ${ADMIN_TOKEN}")
check_status $status "Admin GET /analytics/admin"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/analytics/course/5/ -H "Authorization: Bearer ${INSTRUCTOR_TOKEN}")
check_status $status "Instructor GET /analytics/course/5"

status=$(curl -s -o /dev/null -w "%{http_code}" -X GET $BASE_URL/analytics/overview/ -H "Authorization: Bearer ${ADMIN_TOKEN}")
check_status $status "Admin GET /analytics/overview"
