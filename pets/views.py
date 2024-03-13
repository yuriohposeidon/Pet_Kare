from rest_framework.views import Request, Response, APIView, status
from .models import Pet
from django.forms import model_to_dict
from .serializers import PetSerializer
from traits.models import Trait
from groups.models import Group
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

class PetView(APIView, PageNumberPagination):
    def post(self, req: Request) -> Response:
        serializer = PetSerializer(data=req.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        traits_data = serializer.validated_data.pop("traits")
        group_data= serializer.validated_data.pop("group")
        group = Group.objects.filter(scientific_name = group_data["scientific_name"]).first()
        if not group:
            group = Group.objects.create(**group_data)
        pet = Pet.objects.create(**serializer.validated_data, group=group)
    
        trait_list = []
        for trait in traits_data:
            trait_object = Trait.objects.filter(name__iexact=trait["name"]).first()
            if not trait_object:          
                trait_object = Trait.objects.create(**trait)
            trait_list.append(trait_object)

        pet.traits.set(trait_list)
        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)
    
    def get(self, req: Request) -> Response:
        trait_param = req.query_params.get("trait")
        if trait_param:
            pets = Pet.objects.filter(traits__name__iexact = trait_param)
        else:
            pets = Pet.objects.all().order_by("id") 
        result = self.paginate_queryset(pets, req, view=self)
        serializer = PetSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)
    
    
class PetDetailView(APIView):
    def get(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"message": "Pet not found"}, status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(found_pet)
        return Response(serializer.data)
    
    def delete(self, req: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(data=req.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        if "group" in req.data:
            group_data= serializer.validated_data.pop("group")
            group = Group.objects.filter(scientific_name = group_data["scientific_name"]).first()
            if not group:
                group = Group.objects.create(**group_data)
            found_pet.group = group
            
        if "traits" in req.data:    
            trait_list = []
            traits_data = serializer.validated_data.pop("traits")
            for trait in traits_data:
                trait_object = Trait.objects.filter(name__iexact=trait["name"]).first()
                if not trait_object:          
                    trait_object = Trait.objects.create(**trait)
                trait_list.append(trait_object)

            found_pet.traits.set(trait_list)

        for key, value in serializer.validated_data.items():
            setattr(found_pet, key, value)
        found_pet.save()

        serializer = PetSerializer(found_pet)

        return Response(serializer.data)