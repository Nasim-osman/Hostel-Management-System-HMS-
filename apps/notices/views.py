from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import Notice
from .forms import NoticeForm


@login_required
def notice_list_view(request):
    notices = Notice.objects.all().order_by('-publish_date')

    # Residents only see published notices targeted to ALL or RESIDENTS
    if request.user.is_resident:
        notices = notices.filter(is_published=True, target_audience__in=['ALL', 'RESIDENTS'])

    category_filter = request.GET.get('category')
    if category_filter:
        notices = notices.filter(category=category_filter)

    return render(request, 'notices/notice_list.html', {
        'notices': notices,
        'category_choices': Notice.Category.choices,
        'selected_category': category_filter,
    })


@login_required
def notice_detail_view(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.user.is_resident and not notice.is_published:
        messages.error(request, "Notice is not published.")
        return redirect('notices:notice_list')
    return render(request, 'notices/notice_detail.html', {'notice': notice})


@login_required
@role_required(['ADMIN', 'WARDEN'])
def notice_create_view(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            messages.success(request, f"Notice '{notice.title}' published.")
            return redirect('notices:notice_list')
    else:
        form = NoticeForm()
    return render(request, 'notices/notice_form.html', {'form': form, 'action': 'Publish Notice'})


@login_required
@role_required(['ADMIN', 'WARDEN'])
def notice_edit_view(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, f"Notice '{notice.title}' updated.")
            return redirect('notices:notice_detail', notice_id=notice.id)
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notices/notice_form.html', {'form': form, 'notice': notice, 'action': 'Edit Notice'})
