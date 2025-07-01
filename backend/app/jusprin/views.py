from rest_framework.views import APIView
import os
import json
from functools import wraps
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from langfuse.decorators import langfuse_context, observe
from langfuse.openai import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Dict
import instructor
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.shortcuts import render
from enum import Enum
import sentry_sdk
from django.core.mail import EmailMessage

from api.authentication import CsrfExemptSessionAuthentication
from .serializers import JusPrinChatSerializer
from .models import JusPrinChat
from .llm_chain import run_chain_on_chat
from .plate_analysis_llm_module.analyse_plate_step import analyse_plate_step
from .ai_credits import consume_credit_for_pipeline
from django.conf import settings


def require_ai_credits(view_func):
    """Decorator to check and consume AI credits before pipeline execution."""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        credit_result = consume_credit_for_pipeline(request.user.id)
        if not credit_result['success']:
            return Response({
                'error': credit_result['message'],
                'credits_info': {
                    'used_credits': credit_result['used_credits'],
                    'monthly_limit': credit_result['monthly_limit']
                }
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # Execute the view function
        response = view_func(self, request, *args, **kwargs)

        if isinstance(response.data, dict):
            response.data['jusprint_credits'] = {
                'used_credits': credit_result['used_credits'],
                'monthly_limit': credit_result['monthly_limit']
            }

        return response
    return wrapper

class JusPrinPlateAnalysisViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)

    @require_ai_credits
    @observe(capture_input=False, capture_output=True)
    def create(self, request):
        api_key = os.environ.get('OPENAI_API_KEY')
        openai_client = OpenAI(api_key=api_key)
        langfuse_context.update_current_trace(
            input=request.data.get('messages'),
            user_id=str(request.user.id),
            session_id=request.data.get('chat_id')
        )
        chat = request.data
        response = analyse_plate_step(chat, openai_client)

        return Response(response, status=status.HTTP_201_CREATED)

class JusPrinChatViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = JusPrinChatSerializer

    def get_queryset(self):
        return JusPrinChat.objects.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    @require_ai_credits
    @observe(capture_input=False, capture_output=True)
    def messages(self, request):
        api_key = os.environ.get('OPENAI_API_KEY')
        openai_client = OpenAI(api_key=api_key)
        langfuse_context.update_current_trace(
            input=request.data.get('messages'),
            user_id=str(request.user.id),
            session_id=request.data.get('chat_id')
        )

        chat = request.data
        response = run_chain_on_chat(chat, openai_client)

        return Response(response, status=200)

class JusPrinContactSupportRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for handling JusPrin support requests.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)

    def create(self, request):
        """
        Send a support request email.
        """
        user = request.user
        message = request.data.get('message', '')

        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send email to support
        subject = f"JusPrin Support Request from {user.email}"
        email_body = f"User: {user.email}\n\nMessage:\n{message}"

        try:
            email = EmailMessage(
                subject=subject,
                body=email_body,
                to=['support@obico.io'],
                from_email=os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@obico.io'),
            )
            email.send()

            return Response(
                {'message': 'Support request sent successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {'error': 'Failed to send support request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def embedded_chat_v10(request):
    return render(request, 'jusprin/v1.0/embedded_chat.html')
