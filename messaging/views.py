from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from .models import Contact, Message
from urllib.parse import urlencode

User = get_user_model()

@login_required
def messaging_view(request):
    section = request.GET.get("section", "chat")
    chat_partner_id = request.GET.get("chat_partner")
    chat_partner = None
    messages = []

    if section == "chat" and chat_partner_id:
        chat_partner = get_object_or_404(User, id=chat_partner_id)
        messages = Message.objects.filter(
            (models.Q(sender=request.user, receiver=chat_partner) |
             models.Q(sender=chat_partner, receiver=request.user))
        ).order_by("timestamp")

    friends = Contact.objects.filter(user=request.user, is_friend=True)
    friend_requests = Contact.objects.filter(friend=request.user, is_friend=False)
    all_users = User.objects.exclude(id=request.user.id)  # Exclude the current user

    return render(request, "messaging/messaging.html", {
        "section": section,
        "chat_partner": chat_partner,
        "messages": messages,
        "friends": friends,
        "friend_requests": friend_requests,
        "all_users": all_users,  # Pass all users to the template
    })

@login_required
def add_friend(request):
    if request.method == "POST":
        try:
            friend_id = request.POST.get("friend_id")
            friend = get_object_or_404(User, id=friend_id)
            Contact.objects.get_or_create(user=request.user, friend=friend, is_friend=False)
            return redirect('messaging:messaging')  # Redirect back to the messaging view
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Invalid request."})
    return JsonResponse({"status": "error", "message": "Invalid request method."})

@login_required
def confirm_request(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        contact = get_object_or_404(Contact, id=request_id, friend=request.user)
        contact.is_friend = True
        contact.save()

        Contact.objects.get_or_create(
            user=request.user,
            friend=contact.user,
            is_friend=True
        )

        base_url = reverse("messaging:messaging")
        query_string = urlencode({"section": "contacts"})
        return redirect(f"{base_url}?{query_string}")

@login_required
def delete_friend(request):
    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        friend_contact = get_object_or_404(Contact, user=request.user, friend_id=friend_id, is_friend=True)
        friend_contact.delete()

        # Delete the reverse contact
        reverse_contact = Contact.objects.filter(user=friend_id, friend=request.user, is_friend=True).first()
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