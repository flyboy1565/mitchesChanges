from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse, HttpResponseNotFound
from django.utils import timezone

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
    

def followAge(requests, user):
    user = StreamUsers.objects.filter(username=user)
    if user.count() == 1:
        return JsonResponse({'followTime': user[0].followed_at})
 

def follow(requests, user_id):
    user = StreamUsers.objects.get(user_id=user_id)
    user.following = True
    user.followed_at = timezone.now()
    user.save()
    return JsonResponse({'following': True})
