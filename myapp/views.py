from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages 
import json
import psycopg2
from datetime import datetime
from fitparse import FitFile
from myapp.models import Document
from myapp.forms import DocumentForm
from myapp.forms import SignUpForm
import numpy as np
import os
import smtplib
from django.contrib.auth.models import User
from django import forms

def home(request):
	return render(request, 'index.html')

def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        fitfile = FitFile('/home/michael/Documents/cornfield_2/'+filename)
        fileLocation = '/home/michael/Documents/cornfield_2/'+filename
        speed_data = []
        distance_data = []
        time_data = []
        elevation_data = [] 
        count = 0
        for record in fitfile.get_messages('record'):
            for record_data in record:
                if record_data.name == 'enhanced_altitude':
                    elevation_data.append([count, record_data.value])
                    count += 1
                if record_data.name == 'speed':
                    speed_data.append(record_data.value)
                if record_data.name == 'distance':
                    distance_data.append(record_data.value)
                if record_data.name == 'timestamp':
                    time_data.append(record_data.value)
        meters_per_sec = np.mean(speed_data)
        ride_time = np.max(time_data) - np.min(time_data)
        end_time = np.max(time_data)
        end_time = str(end_time)
        end_time = str(end_time[0:10])
        elevation_gain = 0
        link_id = 0
        previous_point_elevation = 0
        for point in elevation_data:
            if point[0] == link_id:         
                if point[1] > previous_point_elevation:
                    elevation_gain+= point[1] - previous_point_elevation
            link_id = point[0]
        uploaded_file_url = fs.url(filename)
        os.remove(fileLocation)
        climbing_density = (elevation_gain*3.28084)//(np.max(distance_data)*0.000621371)
        average_speed = str(round(meters_per_sec*2.23694,2))
        max_speed = str(round(np.max(speed_data)*2.23694,2))
        adjusted_max_speed = str(round((np.max(speed_data)*2.23694)-(climbing_density*0.75)+10,2))
        total_distance = str(round(np.max(distance_data)*0.000621371,2))
        elevation_gain = round(elevation_gain*3.28084,0)
        username = str(request.user)
        gmail_user = 'tourdecornfield@gmail.com'  
        gmail_password = 'whatwhat3'
        sent_from = gmail_user  
        to = [request.user.email]  
        subject = 'OMG Super Important Message'  
        body = 'Hi '+request.user.first_name+',\n\nYour ride on '+end_time+' has been successfully uploaded! Have a good day! \n\n- Kernel Cob'
        
        if username != None:
            conn = psycopg2.connect("host=postgresql.csrxtcqureoz.us-east-2.rds.amazonaws.com dbname=tour_de_cornfield user=postgres password=P0stgr3s")
            cursor = conn.cursor()
            cur = conn.cursor()
            cur.execute("SELECT * FROM ride_data WHERE username = '"+username+"' AND total_elevation_gain = '"+str(elevation_gain)+"';")
            oldRide = cur.fetchone()
            conn.commit()
            cursor.close()
            conn.close()            
        if oldRide == None:
            conn = psycopg2.connect("host=postgresql.csrxtcqureoz.us-east-2.rds.amazonaws.com dbname=tour_de_cornfield user=postgres password=P0stgr3s")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ride_data (username, total_distance, total_time, average_speed, adjusted_max_speed, max_speed, total_elevation_gain, adjusted_elevation_gain, ride_date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, total_distance, ride_time, average_speed, adjusted_max_speed, max_speed, elevation_gain, climbing_density, end_time))
            conn.commit()
            cursor.close()
            conn.close()
            try:  
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, to, body)
                server.close()
                print 'Email sent!'
            except:  
                print 'Something went wrong...'	 
            return render(request, 'ride_stats.html', {                
                'average_speed': str(round(meters_per_sec*2.23694,2)),
                'max_speed': str(round(np.max(speed_data)*2.23694,2)),
                'adjusted_max_speed': str(round((np.max(speed_data)*2.23694)-(climbing_density*0.75)+10,2)),
                'total_distance': str(round(np.max(distance_data)*0.000621371,2)),
                'ride_time': ride_time,
                'elevation_gain': str(elevation_gain),
                'climbing_density': str((elevation_gain*3.28084)//(np.max(distance_data)*0.000621371))
            })
        else:
            date_dict = {'duplicate': 'true'}
            return render(request, 'upload.html', context=date_dict)

    return render(request, 'upload.html')
def rides(request):
        user = str(request.user)
        conn = psycopg2.connect("host=postgresql.csrxtcqureoz.us-east-2.rds.amazonaws.com dbname=tour_de_cornfield user=postgres password=P0stgr3s")
        cursor = conn.cursor()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ride_data WHERE username = '"+user+"';")
        rides = cur.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        print rides
        return render(request, 'rides.html', {                
                    'rides': rides
            })

def ride_stats(request):
		return render(request, 'ride_stats.html')

def terms_and_agreement(request):
		return render(request, 'agreement.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
        	secret_key = form.cleaned_data.get('secret_key')
	        if secret_key == 'corncob-37464':
	            form.save()
	            username = form.cleaned_data.get('username')
	            raw_password = form.cleaned_data.get('password1')
	            user = authenticate(username=username, password=raw_password)
	            login(request, user)
                username = 'hi'
                if username != "":
                    gmail_user = 'tourdecornfield@gmail.com'  
                    gmail_password = 'whatwhat3'
                    sent_from = gmail_user  
                    to = 'michaelkeller03@gmail.com' 
                    subject = 'OMG Super Important Message'  
                    body = 'Hi Michael,\n\nA new user has signed up for Tour De Cornfield! \n\nHave a good day! \n\n- Kernel Cob'
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, to, body)
                    server.close()
	            return redirect('home')
	        else:
	            return render(request, 'register.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})
