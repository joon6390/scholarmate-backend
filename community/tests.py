from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Conversation, DirectMessage


class ConversationUnreadCountTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="reader", password="testpass")
        self.partner = user_model.objects.create_user(username="sender", password="testpass")
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user, self.partner)
        self.client.force_authenticate(user=self.user)

    def test_list_counts_each_unread_message_once(self):
        DirectMessage.objects.bulk_create(
            [
                DirectMessage(
                    conversation=self.conversation,
                    sender=self.partner,
                    content=f"unread-{index}",
                )
                for index in range(3)
            ]
        )
        DirectMessage.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="my-unread-message",
        )
        DirectMessage.objects.create(
            conversation=self.conversation,
            sender=self.partner,
            content="already-read",
            is_read=True,
        )

        response = self.client.get(reverse("community-conv-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["unread_count"], 3)
        self.assertEqual(response.data[0]["participant_count"], 2)
