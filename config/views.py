from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def eu(request):
    u = request.user
    return Response({
        "id": u.id,
        "nome": u.get_full_name() or u.username,
        "email": u.email,
        "matricula": u.username,
    })