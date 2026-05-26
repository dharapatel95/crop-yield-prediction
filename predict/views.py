# Create your views here.
'''from django.http import HttpResponse

def Welcome(request):
    return HttpResponse('<h1>Jay ganesh.. Jay yogeshwer.. jay mataji</h1>')'''
from django.shortcuts import render
import pickle
import numpy as np
from .models import Prediction
from django.contrib.auth.decorators import login_required
model = pickle.load(open('best_model.pkl', 'rb'))
from django.contrib.auth.decorators import login_required

import pandas as pd

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

# REGISTER
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'registration/register.html', {'error': 'User already exists'})

        user = User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'registration/register.html')

# LOGIN
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})

    return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
# after prediction
#prediction_value = prediction[0]
#@login_required

from django.http import JsonResponse
from django.http import JsonResponse




def get_suggestions(temp, rainfall, humidity, fert, pest):
    suggestions = []

    if rainfall > 1400:
        suggestions.append("⚠ Very high rainfall → drainage needed")
    elif rainfall < 400:
        suggestions.append("🌵 Low rainfall → irrigation needed")

    if temp > 35:
        suggestions.append("🔥 High temp → increase water")
    elif temp < 15:
        suggestions.append("❄ Low temp → slow growth")

    if humidity > 85:
        suggestions.append("💧 fungal risk")
    elif humidity < 40:
        suggestions.append("🏜 dry condition")

    if fert < 3:
        suggestions.append("🧪 increase fertilizer")
    if pest < 1:
        suggestions.append("🪲 pest risk")

    if len(suggestions) == 0:
        suggestions.append("✅ Good conditions")

    return suggestions



####

@login_required(login_url='login')
def home(request):
    if request.method == "POST":
        try:
            data = {

                'crop': request.POST['crop'].strip().lower(),
                'season': request.POST['season'].strip().lower(),
                'state': request.POST['state'].strip().lower(),
                'area': float(request.POST['area']),
                'fertilizer': float(request.POST['fertilizer']),
                'pesticide': float(request.POST['pesticide']),

                'avg_temp_c': float(request.POST['avg_temp']),
                'total_rainfall_mm': float(request.POST['rainfall']),
                'avg_humidity_percent': float(request.POST['humidity']),

               
            }

            columns = [
                'crop', 'season', 'state',
                'area',  'fertilizer', 'pesticide',
                'avg_temp_c', 'total_rainfall_mm', 'avg_humidity_percent'
            ]

            input_df = pd.DataFrame([[data[col] for col in columns]], columns=columns)

            prediction = model.predict(input_df)
            prediction_value = float(prediction[0])

            # ✅ generate realistic harvest pattern (low → high → low)
            x = np.linspace(0, 1, 5)
            harvest_pattern = np.exp(-((x - 0.5) ** 2) / 0.08)

# normalize (so sum = 1)
            harvest_pattern = (harvest_pattern / harvest_pattern.sum()).tolist()


            suggestions = get_suggestions(
                data['avg_temp_c'],
                data['total_rainfall_mm'],
                data['avg_humidity_percent'],
                data['fertilizer'],
                data['pesticide']
            )

            print("Saving for user:", request.user)
            print("Current user:", request.user)

            # ✅ SAVE TO DATABASE
            Prediction.objects.create(
                user=request.user,   # ⭐ ADD THIS LINE
                crop=data['crop'],
                season=data['season'],
                state=data['state'],
                area=data['area'],
                #production=data['production'],
                fertilizer=data['fertilizer'],
                pesticide=data['pesticide'],
                avg_temp_c=data['avg_temp_c'],
                total_rainfall_mm=data['total_rainfall_mm'],
                avg_humidity_percent=data['avg_humidity_percent'],
                result=prediction_value
            )

            return JsonResponse({
    'result': prediction_value,
    'suggestions': suggestions,
    "harvest_pattern": harvest_pattern

})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'dashboard.html')

def history(request):
    data = Prediction.objects.filter(user=request.user)
    return render(request, 'history.html', {'data': data})

@login_required(login_url='login')
def help_page(request):
    return render(request, 'help.html')




import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv(os.path.join(BASE_DIR, "india.csv"))





#df = pd.read_csv("weather_data.csv")
@login_required(login_url='login')
def get_hybrid_weather(request):
    state = request.GET.get("state")
    season = request.GET.get("season")
    current_year = int(request.GET.get("year", 2025))
    if df is None:
        return JsonResponse({"error": "Weather dataset not loaded"}, status=500)
    # ----------------------------
    # 1. Historical (all years except current)
    # ----------------------------
    hist = df[
        (df["state"] == state) &
        (df["season"] == season) &
        (df["year"] < current_year)
    ]

    # ----------------------------
    # 2. Current year data
    # ----------------------------
    curr = df[
        (df["state"] == state) &
        (df["season"] == season) &
        (df["year"] == current_year)
    ]
    print(curr)
    print(hist)

    # ----------------------------
    # 3. Averages
    # ----------------------------
    hist_avg = hist.mean(numeric_only=True)
    curr_avg = curr.mean(numeric_only=True)

    # fallback if current year missing
    if curr.empty:
        curr_avg = hist_avg

    # ----------------------------
    # 4. Hybrid formula
    # ----------------------------
    result = {
        "rainfall": round(hist_avg["rainfall"] * 0.7 + curr_avg["rainfall"] * 0.3, 2),
        "temperature": round(hist_avg["temperature"] * 0.7 + curr_avg["temperature"] * 0.3, 2),
        "humidity": round(hist_avg["humidity"] * 0.7 + curr_avg["humidity"] * 0.3, 2),
    }

    return JsonResponse(result)

@login_required(login_url='login')
def generate_harvest_pattern():
    x = np.linspace(0, 1, 6)

    # bell curve
    pattern = np.exp(-((x - 0.5)**2) / 0.08)

    # add randomness
    pattern = pattern * (0.8 + np.random.rand(len(pattern)) * 0.4)

    # normalize
    pattern = pattern / pattern.sum()

    return pattern.tolist()



def harvest_planner(request):
    return render(request, "harvest_planner.html")