"""
Url configuration

The `urlpatterns` list routes URLs to views. 
"""

# Django
from django.conf.urls import url, include

# Rest framework
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

# Rest framework JWT
from rest_framework_jwt import views as jwt_views

# Custom
from . import views, api_views


# Router url for rest framework
router = DefaultRouter()

router.register(r'notes', api_views.NoteViewSet)
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'users', api_views.NotepikUserViewSet)

# Url patterns for vault page
vault_api_patterns = [
        # Search for notes in vault page
        url(r'^search/$', api_views.SearchVault.as_view(), 
            name="search-vault"),

        # Get encoded vault url
        url(r'^get_vault_url/$', api_views.VaultPage.as_view(), name='get-vault-url' ),

        ]

# url patterns for all api patterns
api_patterns = [
        # For the api docs viewer (swagger)
        url(r'^docs/', include('rest_framework_swagger.urls')),

        # Jwt token authentication
        # Obtain a jwt token with username-password credentials
        url(r'^api-token-auth/', jwt_views.obtain_jwt_token, name='get-token'),
        # Refresh token
        url(r'^api-token-refresh/', jwt_views.refresh_jwt_token, name=
            'refresh-token'),
        # Verify token
        url(r'^api-token-verify/', jwt_views.verify_jwt_token, name=
            'verify-token'),

        # Rest api endpoints

        # Vault page
        url(r'vault/', include(vault_api_patterns)),

        # Router
        url(r'^', include(router.urls)),

        # View all api
        url(r'^$', api_views.APIRoot.as_view(), name='apiroot-list'),
        ]


# api patterns added format_suffix_patterns so we can pick content type we
# want (e.g .json, .api)
urlpatterns = [
        # Four our rest api
        url('^api/', include(api_patterns)),

        # Show vault page
        url(r'^vault/(?P<encoded_url>.+)/$', views.vault, name="vault"),

        # Main urls
        url(r'^$', views.index, name='index'), # root: /
]
