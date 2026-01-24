#!/bin/bash

echo "🔍 FULL DJANGO PROJECT AUDIT"
echo ""

# Check INSTALLED_APPS in settings.py
echo "=============================="
echo "Checking INSTALLED_APPS in settings.py..."
echo "=============================="
if [ -f "lms_backend/settings.py" ]; then
  grep -n "INSTALLED_APPS" -A 30 lms_backend/settings.py | egrep "courses|assignments|grades" || echo "  ❌ Apps not found in INSTALLED_APPS"
else
  echo "  ❌ settings.py not found"
fi
echo ""

# Loop through apps
for app in courses assignments grades; do
  echo "=============================="
  echo "App: $app"
  echo "=============================="

  # models.py
  if [ -f "$app/models.py" ]; then
    echo "📄 models.py classes:"
    grep -n "class " "$app/models.py" || echo "    ❌ No models defined"
  else
    echo "  ❌ Missing models.py"
  fi

  # serializers.py
  if [ -f "$app/serializers.py" ]; then
    echo "📄 serializers.py imports:"
    grep -n "from .models" "$app/serializers.py" || echo "    ❌ No model import found"
    echo "📄 serializers.py classes:"
    grep -n "class " "$app/serializers.py" || echo "    ❌ No serializers defined"
  else
    echo "  ❌ Missing serializers.py"
  fi

  # views.py
  if [ -f "$app/views.py" ]; then
    echo "📄 views.py imports:"
    grep -n "from .models" "$app/views.py" || echo "    ❌ No model import found"
    grep -n "from .serializers" "$app/views.py" || echo "    ❌ No serializer import found"
    echo "📄 views.py classes:"
    grep -n "class " "$app/views.py" || echo "    ❌ No views defined"
  else
    echo "  ❌ Missing views.py"
  fi

  # urls.py
  if [ -f "$app/urls.py" ]; then
    echo "📄 urls.py imports:"
    grep -n "from .views" "$app/urls.py" || echo "    ❌ No views import found"
    echo "📄 urls.py patterns:"
    grep -n "path(" "$app/urls.py" || echo "    ❌ No URL patterns defined"
  else
    echo "  ❌ Missing urls.py"
  fi

  echo ""
done
