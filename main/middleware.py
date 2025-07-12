# myapp/middleware.py

from django.shortcuts import render

class HandleExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log the error if needed
            print(f"Exception caught: {e}")
            # Redirect or render your custom error page
            return render(request, '500.html', status=500)
        return response
