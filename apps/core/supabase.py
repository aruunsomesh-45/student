import os
from django.conf import settings
from supabase import create_client, Client

_client: Client = None
_admin_client: Client = None

def get_supabase_client() -> Client:
    """
    Returns an initialized Supabase Client with the public Anon Key.
    """
    global _client
    if _client is None:
        url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL', ''))
        key = getattr(settings, 'SUPABASE_KEY', os.getenv('SUPABASE_KEY', ''))
        if url and key:
            _client = create_client(url, key)
    return _client

def get_supabase_admin_client() -> Client:
    """
    Returns an initialized Supabase Client with the Service Role Secret Key (admin privileges).
    """
    global _admin_client
    if _admin_client is None:
        url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL', ''))
        service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''))
        if url and service_key:
            _admin_client = create_client(url, service_key)
    return _admin_client
