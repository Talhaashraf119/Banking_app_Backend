from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from .models import UserInfo
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import json
import random
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
# Create your views here.

def get_token_for_user(user):
     refresh=RefreshToken.for_user(user)
     return{
          'refresh':str(refresh),
          'access':str(refresh.access_token)
     }

@api_view(['POST'])
def login_user(request):
    if request.method=='POST':
        try:
            data=json.loads(request.body)
            username=data.get('username')
            password=data.get('password')

            user=authenticate(username=username,password=password)
            print(username)
            print(password)

            if user is not None:
                token=get_token_for_user(user)
                return JsonResponse({'message':'User authenticated Successfully','token':token,'data':username},status=status.HTTP_200_OK)
            else:
                return JsonResponse({'message':'Invalid User'},status=status.HTTP_401_UNAUTHORIZED)

        except json.JSONDecodeError:
                return JsonResponse({'message':'Invalid Json Format'},status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'message':'Invalid Request Method'},status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def register_user(request):
    first_name=request.data.get('first_name')
    last_name=request.data.get('last_name')
    username=request.data.get('username')
    email=request.data.get('email')
    phone=request.data.get('phone')
    password=request.data.get('password')

    if UserInfo.objects.filter(email=email).exists():
        return JsonResponse({'message':'This email are already register!!'},status=status.HTTP_404_NOT_FOUND)
    
    UserInfo.objects.create(username=username,password=make_password(password),email=email,first_name=first_name,last_name=last_name, phone=phone)

    return JsonResponse({'message':f'{username} is register Successfully'},status=status.HTTP_200_OK)

def generate_random_number():
    return str(random.randint(1000,9999))
@api_view(['POST'])
def otp_send(request):
     email=request.data.get('email')        

     user=UserInfo.objects.filter(email=email).first()

     if user :
          gerernated_number=generate_random_number()
          otp_created_time=datetime.datetime.now().strftime("%H:%M:%S")
          request.session['otp']=gerernated_number
          request.session['time_created']=otp_created_time
          request.session['email']=email
          request.session.save()
          print("Session Key (OTP Send):", request.session.session_key)
          print('session data= >',dict(request.session))

          send_mail(
               "Your OTP Code",
                    f"Your OTP is: {gerernated_number}. It will expire in {otp_created_time} minutes.",
                    "talhaashraf119@gmail.com",
                    [email],
                    fail_silently=False,
          )
          return JsonResponse({"message": "OTP sent successfully",'session_data':request.session.get('otp')}, status=200)
     else:return JsonResponse({"message": "Email not registered"}, status=400)

@api_view(['POST'])
def verify_otp(request):
    otp=request.data.get('otp')
    session_id=request.session.get('session_key')
    send_otp=request.session.get('otp')
    time_session=request.session.get('time_created')
    print("Session Key (OTP Verify):", session_id)
    print('session data in verify otp=>',dict(request.session))

    if not send_otp or time_session is None:
          return JsonResponse({'message':'Expire Otp or Invalid Otp'},status=status.HTTP_404_NOT_FOUND)
     
    current_time=datetime.datetime.now().strftime("%H:%M:%S")
    time_difference=(current_time-time_session) / 60

    Otp_expire_time=5

    if time_difference > Otp_expire_time:
        request.session.pop('otp',None)
        request.session.pop('time_created',None)
        request.session.pop('email',None)
        return JsonResponse({'message':'OTP are expired (time )'},status=status.HTTP_404_NOT_FOUND)
     
    if otp == send_otp:
          request.session.pop('otp',None)
          return JsonResponse({'message':'Otp are verifed Successfully'},status=status.HTTP_200_OK)
    else:
          return JsonResponse({'message':'Technical Issue....... Try again'},status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def change_pass(request):
     Entered_pass=request.data.get('password')
     email=request.data.get('email')
     username=request.data.get('username')

     user = UserInfo.objects.filter(Q(username=username) | Q(email=email)).first()

     if user:
            user.password = make_password(Entered_pass)
            user.save()
            return JsonResponse({'message':'Password change Successfully'},status=status.HTTP_202_ACCEPTED)
     else:
          return JsonResponse({'message':'User are not registered Try again'},status=status.HTTP_404_NOT_FOUND)
     
          

