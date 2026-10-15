# Third Party
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

# Django
from django.urls import path

# dbfv
from api.licenses import LicenseLookupView, ValidLicensesView
from api.submissions import (
    CapabilitiesView,
    GymSubmissionCreateView,
    InternationalSubmissionCreateView,
    JudgeSubmissionCreateView,
    StarterSubmissionCreateView,
    SubmissionOptionsView,
)
from api.views import VIEWSETS

router = DefaultRouter()
for slug, viewset in VIEWSETS.items():
    router.register(slug, viewset, basename=slug)

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('licenses/valid/', ValidLicensesView.as_view(), name='licenses-valid'),
    path('licenses/lookup/', LicenseLookupView.as_view(), name='licenses-lookup'),
    path('capabilities/', CapabilitiesView.as_view(), name='api-capabilities'),
    path('submissions/options/', SubmissionOptionsView.as_view(), name='submission-options'),
    path('submissions/starter/', StarterSubmissionCreateView.as_view(), name='submission-starter-create'),
    path(
        'submissions/international/',
        InternationalSubmissionCreateView.as_view(),
        name='submission-international-create',
    ),
    path('submissions/gym/', GymSubmissionCreateView.as_view(), name='submission-gym-create'),
    path('submissions/judge/', JudgeSubmissionCreateView.as_view(), name='submission-judge-create'),
    *router.urls,
]
