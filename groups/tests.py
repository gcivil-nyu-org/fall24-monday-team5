from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from .models import Group, GroupMessage, Invitation


class GroupsTests(TestCase):
    def setUp(self):
        self.user1 = Profile.objects.create_user(
            username="user1-provider",
            password="password1",
            email="<EMAIL>",
            role="Provider",
        )
        self.user2 = Profile.objects.create_user(
            username="user2-user", password="password2", email="<EMAIL>", role="User"
        )
        self.user3 = Profile.objects.create_user(
            username="user3-user", password="password3", email="<EMAIL>", role="User"
        )
        self.user4 = Profile.objects.create_user(
            username="user4-user", password="password4", email="<EMAIL>", role="User"
        )
        self.group = Group.objects.create(name="Test Group", created_by=self.user1)
        self.group.members.add(self.user1)
        self.group.members.add(self.user2)
        self.invitation = Invitation.objects.create(
            group=self.group, user=self.user3, status="pending"
        )
        self.client.login(username="user1-provider", password="password1")

    # GroupList Tests
    def test_group_list_view_status_code(self):
        response = self.client.get(reverse("groups:group_list"))
        self.assertEqual(response.status_code, 200)

    def test_group_list_view_template_used(self):
        response = self.client.get(reverse("groups:group_list"))
        self.assertTemplateUsed(response, "groups/group_list.html")

    def test_group_list_view_groups_displayed(self):
        self.client.login(username="user2-user", password="password2")
        response = self.client.get(reverse("groups:group_list"))
        self.assertContains(response, "Test Group")

    # GroupDetail Tests
    def test_group_detail_view_status_code(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.get(reverse("groups:group_detail", args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_group_detail_view_status_code_fail(self):
        self.client.login(username="user4-user", password="password4")
        response = self.client.get(reverse("groups:group_detail", args=[self.group.id]))
        self.assertEqual(response.status_code, 404)

    def test_group_detail_view_template_used(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.get(reverse("groups:group_detail", args=[self.group.id]))
        self.assertTemplateUsed(response, "groups/group_detail.html")

    # CreateGroup Tests
    def test_create_group_view_status_code(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.get(reverse("groups:create_group"))
        self.assertEqual(response.status_code, 200)

    def test_create_group_view_post(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.post(
            reverse("groups:create_group"),
            data={"name": "New Group", "description": "A new test group"},
        )
        self.assertRedirects(response, reverse("groups:group_list"))
        new_group = Group.objects.get(name="New Group")
        self.assertEqual(new_group.created_by, self.user1)

    # SendGroupMessage Tests
    def test_send_group_message(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.post(
            reverse("groups:send_message", args=[self.group.id]),
            data={"content": "Hello, Group!"},
        )
        self.assertRedirects(
            response, reverse("groups:group_detail", args=[self.group.id])
        )
        self.assertEqual(GroupMessage.objects.count(), 1)
        self.assertEqual(GroupMessage.objects.first().content, "Hello, Group!")

    # SendInvitation Tests
    def test_send_invitation_post(self):
        self.client.login(username="user1-provider", password="password1")
        new_user = Profile.objects.create_user(
            username="user5-user", password="password5", email="<EMAIL>", role="User"
        )
        response = self.client.post(
            reverse("groups:send_invitation", args=[self.group.id]),
            data={"users": [new_user.id]},
        )
        self.assertRedirects(
            response, reverse("groups:group_detail", args=[self.group.id])
        )
        self.assertEqual(Invitation.objects.first().status, "pending")

    # RespondToInvitation Tests
    def test_accept_invitation(self):
        self.client.login(username="user3-user", password="password3")
        response = self.client.post(
            reverse("groups:respond_to_invitation", args=[self.invitation.id]),
            data={"response": "accept"},
        )
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "accepted")
        self.assertIn(self.user3, self.group.members.all())
        self.assertRedirects(response, reverse("groups:group_list"))

    def test_decline_invitation(self):
        self.client.login(username="user3-user", password="password3")
        response = self.client.post(
            reverse("groups:respond_to_invitation", args=[self.invitation.id]),
            data={"response": "decline"},
        )
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "declined")
        self.assertRedirects(response, reverse("groups:group_list"))

    # QuitGroup Tests
    def test_quit_group(self):
        self.client.login(username="user3-provider", password="password3")
        response = self.client.post(reverse("groups:quit_group", args=[self.group.id]))
        self.assertRedirects(response, reverse("groups:group_list"))
        self.assertNotIn(self.user3, self.group.members.all())

    # DeleteGroup Tests
    def test_delete_group(self):
        self.client.login(username="user1-provider", password="password1")
        response = self.client.post(
            reverse("groups:delete_group", args=[self.group.id])
        )
        self.assertRedirects(response, reverse("groups:group_list"))
        with self.assertRaises(Group.DoesNotExist):
            self.group.refresh_from_db()

    # Test for inviting multiple users
    def test_send_multiple_invitations_post(self):
        self.client.login(username="user1-provider", password="password1")
        new_user1 = Profile.objects.create_user(
            username="user6-user", password="password6", email="<EMAIL>", role="User"
        )
        new_user2 = Profile.objects.create_user(
            username="user7-user", password="password7", email="<EMAIL>", role="User"
        )
        response = self.client.post(
            reverse("groups:send_invitation", args=[self.group.id]),
            data={"users": [new_user1.id, new_user2.id]},
        )
        self.assertRedirects(
            response, reverse("groups:group_detail", args=[self.group.id])
        )
        self.assertEqual(Invitation.objects.filter(status="pending").count(), 3)

    # Test for declining a non-existent invitation
    def test_decline_nonexistent_invitation(self):
        self.client.login(username="user4-user", password="password4")
        response = self.client.post(
            reverse("groups:respond_to_invitation", args=[9999]),
            data={"response": "decline"},
        )
        self.assertEqual(response.status_code, 404)

    # Test for non-member trying to send a group message
    def test_non_member_send_message(self):
        self.client.login(username="user4-user", password="password4")
        response = self.client.post(
            reverse("groups:send_message", args=[self.group.id]),
            data={"content": "Hello!"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(GroupMessage.objects.count(), 0)

    # Test for deleting a group by a non-creator
    def test_delete_group_by_non_creator(self):
        self.client.login(username="user2-user", password="password2")
        response = self.client.post(
            reverse("groups:delete_group", args=[self.group.id])
        )
        self.assertEqual(response.status_code, 404)
        self.group.refresh_from_db()

    # Test for viewing an invite list as a non-creator
    def test_invite_users_view_non_creator(self):
        self.client.login(username="user2-user", password="password2")
        response = self.client.get(reverse("groups:invite_users", args=[self.group.id]))
        self.assertEqual(response.status_code, 404)

    # Test for a member quitting a group
    def test_quit_group_member(self):
        self.client.login(username="user2-user", password="password2")
        response = self.client.post(reverse("groups:quit_group", args=[self.group.id]))
        self.assertRedirects(response, reverse("groups:group_list"))
        self.assertNotIn(self.user2, self.group.members.all())
