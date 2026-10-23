from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.accounts.decorators import role_required, warden_or_admin_only
from .models import Room, Bed, HostelBlock, Amenity
from .forms import RoomForm, BedForm, AmenityUpdateForm


@login_required
def room_list_view(request):
    rooms = Room.objects.select_related('block').prefetch_related('beds').all()
    blocks = HostelBlock.objects.all()

    # Filters
    block_id = request.GET.get('block')
    room_type = request.GET.get('type')
    availability = request.GET.get('availability')
    search_q = request.GET.get('q')

    if block_id:
        rooms = rooms.filter(block_id=block_id)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if availability == 'vacant':
        rooms = rooms.filter(beds__is_occupied=False).distinct()
    elif availability == 'occupied':
        rooms = rooms.filter(beds__is_occupied=True).distinct()

    if search_q:
        rooms = rooms.filter(
            Q(room_number__icontains=search_q) |
            Q(block__name__icontains=search_q)
        )

    # Summary metrics
    total_rooms = Room.objects.count()
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    vacant_beds = total_beds - occupied_beds

    context = {
        'rooms': rooms,
        'blocks': blocks,
        'selected_block': block_id,
        'selected_type': room_type,
        'selected_availability': availability,
        'search_q': search_q,
        'room_types': Room.RoomType.choices,
        'total_rooms': total_rooms,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'vacant_beds': vacant_beds,
    }
    return render(request, 'rooms/room_list.html', context)


@login_required
def room_detail_view(request, room_id):
    room = get_object_or_404(Room.objects.select_related('block').prefetch_related('beds'), id=room_id)
    # Check occupants
    beds_with_occupants = []
    for bed in room.beds.all():
        occupant = getattr(bed, 'current_allocation', None)
        beds_with_occupants.append({'bed': bed, 'occupant': occupant})

    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'beds_with_occupants': beds_with_occupants,
    })


@login_required
@warden_or_admin_only
def room_create_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            # Auto-generate beds according to capacity
            for i in range(1, room.capacity + 1):
                bed_label = chr(64 + i) if room.capacity <= 26 else str(i)
                Bed.objects.create(room=room, bed_number=f"Bed-{bed_label}")
            messages.success(request, f"Room {room.room_number} created with {room.capacity} beds.")
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'action': 'Add Room'})


@login_required
@warden_or_admin_only
def room_edit_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f"Room {room.room_number} updated.")
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'room': room, 'action': 'Edit Room'})


@login_required
def amenity_list_view(request):
    amenities = Amenity.objects.all()
    return render(request, 'rooms/amenity_list.html', {'amenities': amenities})


@login_required
@role_required(['ADMIN', 'WARDEN', 'MAINTENANCE'])
def amenity_toggle_view(request, amenity_id):
    amenity = get_object_or_404(Amenity, id=amenity_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        description = request.POST.get('description', '')
        if new_status in dict(Amenity.Status.choices):
            amenity.status = new_status
            if description:
                amenity.description = description
            amenity.save()
            messages.success(request, f"Amenity '{amenity.name}' status updated to {amenity.get_status_display()}.")
    return redirect('rooms:amenity_list')
