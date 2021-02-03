from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser
from users.serializers import UserSerializer, SignupSerializer


class UserView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class FileUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file = request.data['file']
            if file.content_type == 'image/png' or file.content_type == 'image/jpeg':
                user = request.user
                # removing previously saved file
                user.profile_pic.delete()
                user.profile_pic = file
                user.save()
                return Response(UserSerializer(user).data, status=status.HTTP_202_ACCEPTED)
            else:
                raise UnsupportedMediaType(file.content_type)
        except KeyError:
            return Response("file missing.", status=status.HTTP_404_NOT_FOUND)


class LoginView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SignupView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = serializer.save()
            user.set_password(user.password)
            user.save()
            return JsonResponse(UserSerializer(user).data, status=status.HTTP_201_CREATED)
