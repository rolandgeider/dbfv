from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
