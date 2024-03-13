from rest_framework.views import APIView, status, Request, Response
from .models import Group
from .serializers import GroupSerializer

class GroupView(APIView):
    def post(self, req: Request) -> Response:
        return Response({"message": "post group sucess."})