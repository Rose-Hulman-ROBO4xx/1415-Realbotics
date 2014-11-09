from django.shortcuts import render, redirect
from django.http import HttpResponse
from urllib2 import Request, urlopen, URLError

from deviceServer import server

def deviceList(request):
    return render(request, 'devicelist.html', {'devices': server.clients.keys(), 'history': server.history.get()})

def device(request, deviceId):
    message = request.POST.get('message')
    server.clients[deviceId].send(message)

    print request.META
    server.history.register(request.META['REMOTE_ADDR'], deviceId, message)

    return redirect('/')
