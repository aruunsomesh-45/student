from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for handling Google OAuth user data extraction and role assignment.
    """
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # Populate names from Google profile
        if not user.first_name:
            user.first_name = data.get('first_name') or data.get('given_name', '')
        if not user.last_name:
            user.last_name = data.get('last_name') or data.get('family_name', '')
            
        # Role assignment based on session intent or default
        signup_role = request.session.get('oauth_signup_role')
        if signup_role in ['STUDENT', 'TEACHER']:
            user.role = signup_role
        else:
            user.role = 'STUDENT'
            
        signup_tier = request.session.get('oauth_signup_tier')
        if signup_tier:
            user.academic_tier = signup_tier
            
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Clear temporary session flags
        request.session.pop('oauth_signup_role', None)
        request.session.pop('oauth_signup_tier', None)
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse('accounts:dispatch')
