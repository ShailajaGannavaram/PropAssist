from django.contrib import admin
from .models import Conversation, Message, Lead

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content', 'created_at']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'interest', 'created_at']
    search_fields = ['name', 'phone']
    readonly_fields = ['created_at']
