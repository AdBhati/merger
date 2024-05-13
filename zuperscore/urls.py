"""zuperscore URL Configuration

"""

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls import include, url
# from django.conf.urls.static import static
from zuperscore.api.views.authentication import ForgotPasswordView, ResetPasswordView, SendMobileOtpView, VerifyMobileOtpView
from zuperscore.web.views import TestQuestionsIrtEndpoint, TestQuestionsSessionsEndpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('api/', include('zuperscore.api.urls')),
    path('', include('zuperscore.web.urls')),
    path(
        "forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot-password",
    ),
    path(
        "reset-password/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "send-mobile-otp/",
        SendMobileOtpView.as_view(),
        name="send-password-reset",
    ),
    path(
        "verify-mobile-otp/",
        VerifyMobileOtpView.as_view(),
        name="verify-mobile-otp",
    ),
    # path("test-irt/<int:pk>/", TestQuestionsIrtEndpoint.as_view(), name="tenants_irt_detail"),
    path("test-session/<int:session_id>/", TestQuestionsSessionsEndpoint.as_view(), name="tenants_session_detail"),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
