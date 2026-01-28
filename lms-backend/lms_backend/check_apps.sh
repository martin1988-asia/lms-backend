#!/bin/bash

echo "🔍 Checking INSTALLED_APPS in settings.py..."
grep -n "INSTALLED_APPS" -A 30 lms_backend/settings.py | egrep "courses|assignments|grades" || echo "  ❌ Apps not found in INSTALLED_APPS"

echo ""
for app in courses assignments grades; do
  echo "🔍 Checking $app app..."
  if [ -d "$app" ]; then
    for file in models.py serializers.py views.py urls.py admin.py; do
      if [ -f "$app/$file" ]; then
        echo "  ✅ Found $file"
        grep -E "class " "$app/$file" | sed 's/^/    ↳ /'
      else
        echo "  ❌ Missing $file"
      fi
    done
  else
    echo "  ❌ App folder $app not found"
  fi
  echo ""
done
