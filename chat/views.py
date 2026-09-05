import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .answer_grasph import KnowledgeGraphUnavailable
from .go_grasph import ChatBotGraph
from .question_classifier import ChatModelUnavailable

logger = logging.getLogger(__name__)


@require_GET
def chatindex(request):
    return render(request, 'chat/chat.html')


@require_POST
def add(request):
    question = request.POST.get('q', '').strip()
    if not question:
        return HttpResponse('请输入问题。', status=400)
    try:
        return HttpResponse(deal_question(question))
    except (ChatModelUnavailable, KnowledgeGraphUnavailable) as exc:
        logger.warning('Chat service unavailable: %s', exc)
        return HttpResponse('问答服务暂不可用，请稍后再试。', status=503)


def deal_question(question):
    handler = ChatBotGraph()
    return handler.chat_main(question)
