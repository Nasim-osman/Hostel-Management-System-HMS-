from .models import InAppNotification


def notifications_context(request):
    if request.user.is_authenticated:
        unread_count = InAppNotification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifs = InAppNotification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifs,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }
