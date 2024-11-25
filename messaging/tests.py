from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile
from .models import Contact, Message

User = get_user_model()


class MessagingAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.user1 = Profile.objects.create_user(
            username="user1", password="password1", email="<EMAIL>", role="User"
        )
        self.user2 = Profile.objects.create_user(
            username="user2", password="password2", email="<EMAIL>", role="Provider"
        )
        self.user3 = Profile.objects.create_user(
            username="user3", password="password3", email="<EMAIL>", role="User"
        )

        # Login as user1
        self.client.login(username="user1", password="password1")

    def test_messaging_view(self):
        url = reverse("messaging:messaging")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/messaging.html")
        self.assertIn("friends", response.context)
        self.assertIn("friend_requests", response.context)

    def test_search_users(self):
        url = reverse("messaging:messaging")
        response = self.client.get(url, {"search_query": "user2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_users"].count(), 1)

    def test_add_friend_notfound(self):
        response = self.client.post({"friend_id": self.user2.id})
        self.assertEqual(response.status_code, 404)

    def test_add_friend(self):
        url = reverse("messaging:add_friend")
        response = self.client.post(url, {"friend_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "status": "success",
                "message": f"Friend request sent to {self.user2.username}.",
            },
        )

    def test_add_friend_already_exists(self):
        # Create an existing friend relationship
        Contact.objects.create(user=self.user1, friend=self.user2, is_friend=True)
        url = reverse("messaging:add_friend")
        response = self.client.post(url, {"friend_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "status": "error",
                "message": f"You are already friends with {self.user2.username}.",
            },
        )

    def test_confirm_request(self):
        request_contact = Contact.objects.create(
            user=self.user2, friend=self.user1, is_friend=False
        )
        url = reverse("messaging:confirm_request")
        response = self.client.post(url, {"request_id": request_contact.id})
        # Check the response status and that the contact is now a friend
        self.assertEqual(response.status_code, 302)
        request_contact.refresh_from_db()
        self.assertTrue(request_contact.is_friend)

    def test_delete_friend(self):
        Contact.objects.create(user=self.user1, friend=self.user2, is_friend=True)
        url = reverse("messaging:delete_friend")
        response = self.client.post(url, {"friend_id": self.user2.id})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertFalse(
            Contact.objects.filter(user=self.user1, friend=self.user2).exists()
        )
        self.assertFalse(
            Contact.objects.filter(user=self.user2, friend=self.user1).exists()
        )

    def test_send_message(self):
        url = reverse("messaging:send_message")
        response = self.client.post(
            url, {"receiver_id": self.user2.id, "content": "Hello, user2!"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Message.objects.filter(
                sender=self.user1, receiver=self.user2, content="Hello, user2!"
            ).exists()
        )

    def test_messaging_view_chat_partner(self):
        # Send a message to create chat context
        Message.objects.create(sender=self.user1, receiver=self.user2, content="Hi!")
        url = reverse("messaging:messaging")
        response = self.client.get(
            url, {"section": "chat", "chat_partner": self.user2.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["chat_partner"], self.user2)
        self.assertEqual(response.context["messages"].count(), 1)
