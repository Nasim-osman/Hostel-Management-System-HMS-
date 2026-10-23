from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('rooms/', include('apps.rooms.urls', namespace='rooms')),
    path('residents/', include('apps.residents.urls', namespace='residents')),
    path('allocations/', include('apps.allocations.urls', namespace='allocations')),
    path('finance/', include('apps.finance.urls', namespace='finance')),
    path('complaints/', include('apps.complaints.urls', namespace='complaints')),
    path('dining/', include('apps.dining.urls', namespace='dining')),
    path('visitors/', include('apps.visitors.urls', namespace='visitors')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('notices/', include('apps.notices.urls', namespace='notices')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('abtesting/', include('apps.abtesting.urls', namespace='abtesting')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "HMS Administration"
admin.site.site_title = "HMS Portal"
admin.site.index_title = "Hostel Operations & Management"
