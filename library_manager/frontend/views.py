from django.shortcuts import render

# Create your views here.
def front (request, *args, **kwargs):
    # return render(request, 'new.html')
    return render(request, 'startpage.html') # Changed template name here
