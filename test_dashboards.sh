#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Timestamp for this run
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOGFILE="logs/dashboard_$TIMESTAMP.json"
SUMMARYFILE="logs/last_summary.txt"

# Login and extract tokens
STUDENT_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{"username":"higino","password":"Felici@2025"}' | jq -r '.access')

INSTRUCTOR_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{"username":"instructor1","password":"Felici@2025"}' | jq -r '.access')

ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{"username":"admin1","password":"Felici@2025"}' | jq -r '.access')

# Collect results
{
  echo "🔐 Testing Student Dashboard..."
  STUDENT_JSON=$(curl -s -X GET http://127.0.0.1:8000/api/dashboard/student/ \
  -H "Authorization: Bearer $STUDENT_TOKEN")
  echo "$STUDENT_JSON" | jq .

  echo ""
  echo "🔐 Testing Instructor Dashboard..."
  INSTRUCTOR_JSON=$(curl -s -X GET http://127.0.0.1:8000/api/dashboard/instructor/ \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN")
  echo "$INSTRUCTOR_JSON" | jq .

  echo ""
  echo "🔐 Testing Admin Dashboard..."
  ADMIN_JSON=$(curl -s -X GET http://127.0.0.1:8000/api/dashboard/admin/ \
  -H "Authorization: Bearer $ADMIN_TOKEN")
  echo "$ADMIN_JSON" | jq .

  echo ""
  echo "📊 Summary Table:"

  STUDENT_ASSIGN=$(echo "$STUDENT_JSON" | jq '.assignments | length')
  STUDENT_SUB=$(echo "$STUDENT_JSON" | jq '.submissions | length')
  STUDENT_GRADES=$(echo "$STUDENT_JSON" | jq '.grades | length')

  INSTRUCTOR_ASSIGN=$(echo "$INSTRUCTOR_JSON" | jq '.assignments | length')
  INSTRUCTOR_SUB=$(echo "$INSTRUCTOR_JSON" | jq '.submissions | length')
  INSTRUCTOR_GRADES=$(echo "$INSTRUCTOR_JSON" | jq '.grades | length')

  ADMIN_USERS=$(echo "$ADMIN_JSON" | jq '.total_users')
  ADMIN_COURSES=$(echo "$ADMIN_JSON" | jq '.total_courses')
  ADMIN_ENROLL=$(echo "$ADMIN_JSON" | jq '.total_enrollments')
  ADMIN_ASSIGN=$(echo "$ADMIN_JSON" | jq '.total_assignments')
  ADMIN_SUB=$(echo "$ADMIN_JSON" | jq '.total_submissions')
  ADMIN_GRADES=$(echo "$ADMIN_JSON" | jq '.total_grades')

  # Function to compare values with last run
  color_compare() {
    local current=$1
    local previous=$2
    if [ -z "$previous" ]; then
      echo "$current"
    elif [ "$current" -gt "$previous" ]; then
      echo -e "\033[0;32m$current (+$((current-previous)))\033[0m"
    elif [ "$current" -lt "$previous" ]; then
      echo -e "\033[0;31m$current (-$((previous-current)))\033[0m"
    else
      echo "$current"
    fi
  }

  # ASCII bar chart generator (using # for compatibility)
  bar_chart() {
    local value=$1
    local label=$2
    local bar=$(printf "%${value}s" | tr ' ' '#')
    echo -e "$label: $bar ($value)"
  }

  # Load previous summary if exists
  declare -A LAST
  if [ -f "$SUMMARYFILE" ]; then
    while IFS="=" read -r key value; do
      LAST[$key]=$value
    done < "$SUMMARYFILE"
  fi

  # Print table header
  printf "%-20s %-15s %-15s %-15s\n" "Role" "Assignments" "Submissions" "Grades"
  echo "--------------------------------------------------------------------------"

  # Student row
  printf "%-20s %-15s %-15s %-15s\n" "Student" \
    "$(color_compare $STUDENT_ASSIGN ${LAST[StudentAssignments]})" \
    "$(color_compare $STUDENT_SUB ${LAST[StudentSubmissions]})" \
    "$(color_compare $STUDENT_GRADES ${LAST[StudentGrades]})"

  # Instructor row
  printf "%-20s %-15s %-15s %-15s\n" "Instructor" \
    "$(color_compare $INSTRUCTOR_ASSIGN ${LAST[InstructorAssignments]})" \
    "$(color_compare $INSTRUCTOR_SUB ${LAST[InstructorSubmissions]})" \
    "$(color_compare $INSTRUCTOR_GRADES ${LAST[InstructorGrades]})"

  # Admin row
  printf "%-20s %-15s %-15s %-15s\n" "Admin (Totals)" \
    "$(color_compare $ADMIN_ASSIGN ${LAST[AdminAssignments]})" \
    "$(color_compare $ADMIN_SUB ${LAST[AdminSubmissions]})" \
    "$(color_compare $ADMIN_GRADES ${LAST[AdminGrades]})"

  echo ""
  printf "%-20s %-15s %-15s %-15s\n" "Admin Extra" "Users" "Courses" "Enrollments"
  echo "--------------------------------------------------------------------------"
  printf "%-20s %-15s %-15s %-15s\n" "" \
    "$(color_compare $ADMIN_USERS ${LAST[AdminUsers]})" \
    "$(color_compare $ADMIN_COURSES ${LAST[AdminCourses]})" \
    "$(color_compare $ADMIN_ENROLL ${LAST[AdminEnrollments]})"

  echo ""
  echo "📊 ASCII Bar Charts:"
  bar_chart $STUDENT_SUB "Student Submissions"
  bar_chart $STUDENT_GRADES "Student Grades"
  bar_chart $INSTRUCTOR_SUB "Instructor Submissions"
  bar_chart $INSTRUCTOR_GRADES "Instructor Grades"
  bar_chart $ADMIN_SUB "Admin Submissions"
  bar_chart $ADMIN_GRADES "Admin Grades"

  # Save current summary for next run
  {
    echo "StudentAssignments=$STUDENT_ASSIGN"
    echo "StudentSubmissions=$STUDENT_SUB"
    echo "StudentGrades=$STUDENT_GRADES"
    echo "InstructorAssignments=$INSTRUCTOR_ASSIGN"
    echo "InstructorSubmissions=$INSTRUCTOR_SUB"
    echo "InstructorGrades=$INSTRUCTOR_GRADES"
    echo "AdminUsers=$ADMIN_USERS"
    echo "AdminCourses=$ADMIN_COURSES"
    echo "AdminEnrollments=$ADMIN_ENROLL"
    echo "AdminAssignments=$ADMIN_ASSIGN"
    echo "AdminSubmissions=$ADMIN_SUB"
    echo "AdminGrades=$ADMIN_GRADES"
  } > "$SUMMARYFILE"

} | tee "$LOGFILE"

echo "✅ Results saved to $LOGFILE"
