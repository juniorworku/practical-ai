"""Cookie sessions for the browser, alongside the existing token API."""
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import AccountSession, EmailIdentity
from .views import AuthThrottle


def csrf_failure(request, reason=''):
    return JsonResponse({'detail':'Your form session expired. Refresh the page and try again.'},status=403)


def device_name(request):
    agent=request.META.get('HTTP_USER_AGENT','')
    browser='Edge' if 'Edg/' in agent else 'Chrome' if 'Chrome/' in agent else 'Firefox' if 'Firefox/' in agent else 'Safari' if 'Safari/' in agent else 'Browser'
    platform='Android' if 'Android' in agent else 'iPhone / iPad' if 'iPhone' in agent or 'iPad' in agent else 'Windows' if 'Windows' in agent else 'Mac' if 'Macintosh' in agent else 'Linux' if 'Linux' in agent else 'device'
    return f'{browser} on {platform}'


def start_session(request,user,remember):
    login(request._request,user,backend='django.contrib.auth.backends.ModelBackend')
    request.session.set_expiry(60*60*24*30 if remember else 0)
    request.session.save()
    AccountSession.objects.update_or_create(session_key=request.session.session_key,defaults={'user':user,'device':device_name(request)})


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def session_status(request):
    response=Response({'authenticated':request.user.is_authenticated,'csrf':get_token(request)})
    response['Cache-Control']='no-store'
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
@csrf_protect
def sign_in(request):
    if not isinstance(request.data,dict):return Response({'detail':'Send a JSON object.'},status=400)
    identifier=request.data.get('username','');password=request.data.get('password','');remember=request.data.get('remember',False)
    if not isinstance(identifier,str) or not isinstance(password,str) or type(remember) is not bool:
        return Response({'detail':'Enter your username or email and password.'},status=400)
    identifier=identifier.strip()
    exact=list(User.objects.filter(username__iexact=identifier)[:2])
    matches=exact if exact else list(User.objects.filter(email__iexact=identifier)[:2])
    username=matches[0].username if len(matches)==1 else identifier
    user=authenticate(request=request._request,username=username,password=password)
    if not user or len(matches)!=1:
        return Response({'detail':'We could not sign you in with those details. If your email is shared by older accounts, use your username.'},status=400)
    start_session(request,user,remember)
    return Response({'username':user.username})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
@csrf_protect
def sign_up(request):
    if not isinstance(request.data,dict):return Response({'detail':'Send a JSON object.'},status=400)
    try:
        username=serializers.RegexField(r'^[\w.@+-]{1,150}$').run_validation(request.data.get('username',''))
        email=serializers.EmailField().run_validation(request.data.get('email','')).strip().casefold()
        display_name=serializers.CharField(max_length=100,allow_blank=True).run_validation(request.data.get('display_name',''))
        password=request.data.get('password','')
        if not isinstance(password,str):raise serializers.ValidationError('Password must be text.')
        if User.objects.filter(username__iexact=username).exists():raise serializers.ValidationError('That username is already in use.')
        if User.objects.filter(email__iexact=email).exists():raise serializers.ValidationError('That email is already in use. Sign in or recover your account.')
        user=User(username=username,email=email,first_name=display_name)
        validate_password(password,user)
        with transaction.atomic():
            user.set_password(password);user.save()
            EmailIdentity.objects.create(user=user,email=email)
    except (ValidationError,serializers.ValidationError) as error:
        return Response({'detail':getattr(error,'messages',str(error))},status=400)
    except IntegrityError:
        return Response({'detail':'That username or email is already in use.'},status=400)
    start_session(request,user,False)
    return Response({'username':user.username},status=201)


@api_view(['POST'])
@csrf_protect
def sign_out(request):
    AccountSession.objects.filter(session_key=request.session.session_key,user=request.user).delete()
    if request.auth:request.auth.delete()
    logout(request._request)
    return Response(status=204)


@api_view(['GET','PUT'])
def account(request):
    user=request.user
    if request.method=='PUT':
        if not isinstance(request.data,dict):return Response({'detail':'Send a JSON object.'},status=400)
        try:
            display=serializers.CharField(max_length=100,allow_blank=True).run_validation(request.data.get('display_name',''))
            # Username and email are stable identifiers. Email changes require a verification workflow.
            user.first_name=display;user.save(update_fields=['first_name'])
        except serializers.ValidationError as error:return Response({'detail':str(error)},status=400)
    return Response({'username':user.username,'display_name':user.first_name,'email':user.email,'joined_at':user.date_joined})


@api_view(['POST'])
def change_password(request):
    if not isinstance(request.data,dict):return Response({'detail':'Send a JSON object.'},status=400)
    current=request.data.get('current_password');new=request.data.get('password')
    if not isinstance(current,str) or not request.user.check_password(current):return Response({'detail':'Your current password is incorrect.'},status=400)
    if not isinstance(new,str):return Response({'detail':'Enter a new password.'},status=400)
    try:validate_password(new,request.user)
    except ValidationError as error:return Response({'detail':error.messages},status=400)
    user=request.user;old_key=request.session.session_key
    user.set_password(new);user.save(update_fields=['password'])
    other_keys=list(AccountSession.objects.filter(user=user).values_list('session_key',flat=True))
    Session.objects.filter(session_key__in=other_keys).delete()
    AccountSession.objects.filter(user=user).delete()
    Token.objects.filter(user=user).delete()
    if old_key:
        update_session_auth_hash(request._request,user)
        request.session.save()
        AccountSession.objects.create(user=user,session_key=request.session.session_key,device=device_name(request))
    return Response({'detail':'Password changed. Other devices and API tokens have been signed out.'})


@api_view(['GET','DELETE'])
def account_sessions(request,pk=None):
    if request.method=='DELETE':
        row=AccountSession.objects.filter(user=request.user,pk=pk).first()
        if row is None:return Response({'detail':'Session not found.'},status=404)
        if row.session_key==request.session.session_key:return Response({'detail':'Use Sign out to end this session.'},status=400)
        Session.objects.filter(session_key=row.session_key).delete();row.delete()
        return Response(status=204)
    live=Session.objects.filter(expire_date__gt=timezone.now(),session_key__in=AccountSession.objects.filter(user=request.user).values('session_key'))
    keys={row.session_key for row in live if row.get_decoded().get('_auth_user_hash')==request.user.get_session_auth_hash()}
    return Response([{'id':row.pk,'device':row.device,'created_at':row.created_at,'current':row.session_key==request.session.session_key} for row in AccountSession.objects.filter(user=request.user,session_key__in=keys).order_by('-created_at')])
