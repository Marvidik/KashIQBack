# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .service import get_ai_response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    question = request.data.get('question')
    if not question:
        return Response({"error": "Question is required"}, status=400)

    answer = get_ai_response(request.user, question)
    return Response({"answer": answer})
