from rest_framework.views import Request, Response, APIView, status
from .models import Pet
from django.forms import model_to_dict

class PetView(APIView):
    def post(self, req: Request) -> Response:
        pet = Pet.objects.create(**req.data)
        pet_dict = model_to_dict(pet)
        return Response(pet_dict, status.HTTP_201_CREATED)
    
    def get(self, req: Request) -> Response:
        pets = Pet.object.all()
        pets_dict = []
        for current_pet in pets:
            pets_dict.append(model_to_dict(current_pet))
        return Response(pets_dict, status.HTTP_200_OK)
