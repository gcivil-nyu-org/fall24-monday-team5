from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from accounts.models import Profile
from calmseek import settings
from .models import Group, GroupMessage, Invitation


@login_required
def group_list_view(request):
    groups = Group.objects.filter(members=request.user)
    invitations = Invitation.objects.filter(user=request.user, status="pending")
    return render(
        request,
        "groups/group_list.html",
        {"groups": groups, "invitations": invitations},
    )


@login_required
def group_detail_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    messages = group.messages.all().order_by("timestamp")
    return render(
        request,
        "groups/group_detail.html",
        {
            "group": group,
            "messages": messages,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        group = Group.objects.create(
            name=name, description=description, created_by=request.user
        )
        group.members.add(request.user)
        return redirect("groups:group_list")
    return render(request, "groups/create_group.html")


@login_required
def send_group_message(request, group_id):
    if request.method == "POST":
        group = get_object_or_404(Group, id=group_id, members=request.user)
        content = request.POST.get("content")
        GroupMessage.objects.create(group=group, sender=request.user, content=content)
        return redirect("groups:group_detail", group_id=group.id)
    return JsonResponse({"status": "error", "message": "Invalid request method."})


@login_required
def invite_users(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)

    available_users = Profile.objects.exclude(
        id__in=group.members.all().values_list("id", flat=True)
    ).exclude(role__in=["Provider", "Admin"])

    paginator = Paginator(available_users, 10)  # Show 10 users per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        user_ids = request.POST.getlist("users")
        for user_id in user_ids:
            user = get_object_or_404(Profile, id=user_id)
            group.members.add(user)

        return redirect("groups:group_detail", group_id=group.id)

    return render(
        request, "groups/invite_users.html", {"group": group, "page_obj": page_obj}
    )


@login_required
def send_invitation(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)

    if request.method == "POST":
        user_ids = request.POST.getlist("users")
        response_messages = []

        for user_id in user_ids:
            user = get_object_or_404(Profile, id=user_id)

            # Check if the user is not already a member
            if user in group.members.all():
                response_messages.append(
                    {
                        "user": user.username,
                        "status": "error",
                        "message": "User is already a member.",
                    }
                )
                continue

            invitation, created = Invitation.objects.get_or_create(
                group=group, user=user, status="pending"
            )

            if created:
                response_messages.append(
                    {
                        "user": user.username,
                        "status": "success",
                        "message": f"Invitation sent to {user.username}.",
                    }
                )
            else:
                response_messages.append(
                    {
                        "user": user.username,
                        "status": "error",
                        "message": "Invitation already sent.",
                    }
                )

        return redirect("groups:group_detail", group_id=group.id)

    return JsonResponse({"status": "error", "message": "Invalid request method."})


@login_required
def respond_to_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, user=request.user)

    if request.method == "POST":
        response = request.POST.get("response")

        if response == "accept":
            invitation.group.members.add(request.user)
            invitation.status = "accepted"
            invitation.save()
            return redirect("groups:group_list")

        elif response == "decline":
            invitation.status = "declined"
            invitation.save()
            return redirect("groups:group_list")

    return JsonResponse({"status": "error", "message": "Invalid response."})


@login_required
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    if request.method == "POST":
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect("groups:group_list")
    else:
        messages.error(request, "Invalid request.")
        return redirect("groups:group_list")


@login_required
def quit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Ensure only members can quit
    if request.user in group.members.all():
        group.members.remove(request.user)

    return redirect("groups:group_list")
