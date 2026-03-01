from .models import Member, AssignedHistory
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def assign_workplace(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == 'POST':
        new_workplace = request.POST.get('workplace')

        if new_workplace:
            # Update current workplace
            member.workplace = new_workplace
            member.save()

            # Save history record
            AssignedHistory.objects.create(
                member=member,
                assigned_place=new_workplace
            )

            messages.success(request, "Workplace assigned successfully.")
            return redirect('member_list')

    return render(request, 'members/assign_workplace.html', {'member': member})