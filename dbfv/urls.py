# Django
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path

# Third Party
from django_email_verification import urls as email_urls


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'dbfv.views.home', name='home'),
    # url(r'^dbfv/', include('dbfv.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #path('admin/', include(admin.site.urls)),

    # The submission application
    path('core/', include(('core.urls', 'core'), namespace='core')),
    path('', include('submission.urls')),
    path('email-verification/', include(email_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
