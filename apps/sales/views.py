from django.http import HttpResponse

def order_list(request):
    return HttpResponse("Sales → Order List")

def order_detail(request, pk):
    return HttpResponse(f"Sales → Order Detail {pk}")