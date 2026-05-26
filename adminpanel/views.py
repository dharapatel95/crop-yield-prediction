from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from predict.models import Prediction
from django.db.models import Count

@staff_member_required
def admin_dashboard(request):
    total_predictions = Prediction.objects.count()
    total_users = User.objects.count()

    top_crops = (
        Prediction.objects
        .values('crop')
        .annotate(count=Count('crop'))
        .order_by('-count')[:5]
    )

    recent = Prediction.objects.select_related('user').order_by('-id')[:10]

    return render(request, 'admin_dashboard.html', {
        'total_predictions': total_predictions,
        'total_users': total_users,
        'top_crops': top_crops,
        'recent': recent
    })