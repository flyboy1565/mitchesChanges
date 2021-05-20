from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse, HttpResponseNotFound

from .models import StreamUsers, CommandUse

# Create your views here.
def rankedCommands(requests,user, command=None):
    if command is None:
        results = CommandUse.objects.all().values('user__username').annotate(count=Count('user__username')).order_by('-count')
    else:
        results = CommandUse.objects.filter(command=command).values('user__username').annotate(count=Count('user__username')).order_by('-count')
    values = [i['user__username'] for i in results]
    rank = values.index(user) + 1
    return JsonResponse({'rank': rank, 'user_count': len(values)})
    
    
