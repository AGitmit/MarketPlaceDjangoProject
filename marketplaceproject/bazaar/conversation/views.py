from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from item.models import Item
from .models import Conversation, ConversationMessage
from .forms import ConversationMessageForm


@login_required
def new_conversation(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    # if item owner - do not give access to create conversation with self.
    if item.created_by == request.user:
        return redirect('dashboard:index')

    conversations = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])

    if conversations:
        return redirect('conversation:detail', pk=conversations.first().id)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation = Conversation.objects.create(item=item)
            conversation.members.add(request.user)
            conversation.members.add(item.created_by)
            conversation.save()

            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('item:detail', pk=item_pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/new.html', {
        'form': form
    })


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])
    conversations_messages = [ConversationMessage.objects.filter(conversation=conv.id) for conv in conversations]

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations,
        'conversations_messages': conversations_messages,
    })


@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == "POST":
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversations_message = form.save(commit=False)
            conversations_message.conversation = conversation
            conversations_message.created_by = request.user
            conversations_message.save()

            return redirect('conversation:detail', pk=pk)

    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/conversation.html', {
        'conversation': conversation,
        'form': form
    })
