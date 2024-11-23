from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from accounts.models import Profile
from calmseek import settings
from .models import Contact, Message
from urllib.parse import urlencode

User = get_user_model()


@login_required
def messaging_view(request):
    section = request.GET.get("section", "chat")
    role = request.GET.get("role", "provider")
    page_number = request.GET.get("page", 1)
    chat_partner_id = request.GET.get("chat_partner")
    search_query = request.GET.get("search_query", "")  # Add search query filter
    chat_partner = None
    messages = []

    if section == "chat" and chat_partner_id:
        chat_partner = get_object_or_404(User, id=chat_partner_id)
        messages = Message.objects.filter(
            (
                models.Q(sender=request.user, receiver=chat_partner)
                | models.Q(sender=chat_partner, receiver=request.user)
            )
        ).order_by("timestamp")

    friends = Contact.objects.filter(user=request.user, is_friend=True)
    friend_requests = Contact.objects.filter(friend=request.user, is_friend=False)

    if role == "provider":
        filtered_users = Profile.objects.filter(role="Provider").exclude(
            id=request.user.id
        )
    else:  # Default to "user" role
        filtered_users = Profile.objects.filter(role="User").exclude(id=request.user.id)

    search_users = ""
    # Search users by username
    if search_query:
        search_users = Profile.objects.filter(username=search_query)

    paginator = Paginator(filtered_users, 12)  # Show 12 users per page
    paginated_users = paginator.get_page(page_number)

    return render(
        request,
        "messaging/messaging.html",
        {
            "section": section,
            "role": role,
            "chat_partner": chat_partner,
            "messages": messages,
            "friends": friends,
            "friend_requests": friend_requests,
            "paginated_users": paginated_users,
            "search_query": search_query,
            "search_users": search_users,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


@login_required
def add_friend(request):
    if request.method == "POST":
        try:
            friend_id = request.POST.get("friend_id")
            friend = get_object_or_404(User, id=friend_id)

            # Check if the user is already friends with the selected friend
            existing_friendship1 = Contact.objects.filter(
                user_id=request.user.id, friend_id=friend_id, is_friend=True
            ).exists()

            existing_friendship2 = Contact.objects.filter(
                user_id=friend_id, friend_id=request.user.id, is_friend=True
            ).exists()

            if existing_friendship1 or existing_friendship2:
                # If already friends, return an instruction
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"You are already friends with {friend.username}.",
                    }
                )

            # Create a new friend request if not already friends
            Contact.objects.get_or_create(
                user=request.user, friend=friend, is_friend=False
            )
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Friend request sent to {friend.username}.",
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "An error occurred while adding the friend. Error: "
                    + str(e),
                }
            )
    return JsonResponse({"status": "error", "message": "Invalid request method."})


@login_required
def confirm_request(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        contact = get_object_or_404(Contact, id=request_id, friend=request.user)
        contact.is_friend = True
        contact.save()

        Contact.objects.get_or_create(
            user=request.user, friend=contact.user, is_friend=True
        )

        base_url = reverse("messaging:messaging")
        query_string = urlencode({"section": "contacts"})
        return redirect(f"{base_url}?{query_string}")


@login_required
def delete_friend(request):
    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        friend_contact = get_object_or_404(
            Contact, user=request.user, friend_id=friend_id, is_friend=True
        )
        friend_contact.delete()

        # Delete the reverse contact
        reverse_contact = Contact.objects.filter(
            user=friend_id, friend=request.user, is_friend=True
        ).first()
        if reverse_contact:
            reverse_contact.delete()

        base_url = reverse("messaging:messaging")
        query_string = urlencode({"section": "contacts"})
        return redirect(f"{base_url}?{query_string}")


@login_required
def send_message(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        content = request.POST.get("content")
        receiver = get_object_or_404(User, id=receiver_id)

        Message.objects.create(sender=request.user, receiver=receiver, content=content)

        base_url = reverse("messaging:messaging")
        query_string = urlencode({"section": "chat", "chat_partner": receiver.id})
        return redirect(f"{base_url}?{query_string}")
