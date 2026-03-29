from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path

from finance_app.admin_site import finance_admin_site
from .static_views import serve_static

urlpatterns = [
    path('admin/', finance_admin_site.urls),
    path('', include('finance_app.urls', namespace='finance_app')),
]

if settings.DEBUG:
    urlpatterns.insert(0, re_path(r"^static/(?P<path>.*)$", serve_static))
    urlpatterns += staticfiles_urlpatterns()
