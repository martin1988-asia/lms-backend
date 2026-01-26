from rest_framework.response import Response

def success_response(data=None, status=200):
    return Response({
        "success": True,
        "data": data,
        "errors": None
    }, status=status)

def error_response(errors, status=400):
    return Response({
        "success": False,
        "data": None,
        "errors": errors
    }, status=status)
