from django.db import models
from users.models import BaseModel, Users

class Conversation(BaseModel):
    user1 = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="conversations_as_user1"
    )
    user2 = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="conversations_as_user2"
    )

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Conversation: {self.user1.username} ↔ {self.user2.username}"


class Message(BaseModel):
    MESSAGE_STATUS = [
        ('pending','Pending'),
        ('sent','Sent'),
        ('delivered','Delivered'),
        ('read','Read')
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="received_messages"
    )
    message_text = models.TextField(blank=True, null=True)
    message_photo_url = models.URLField(max_length=500, blank=True, null=True)  # store URL here
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS, default='pending')

    class Meta:
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        content_preview = self.message_text[:20] + '...' if self.message_text else "Photo"
        return f"Message from {self.sender.username} to {self.receiver.username}: {content_preview}"
