from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListCreateAPIView, get_object_or_404

from .models import GatePass, Student
from .serializers import GatePassSerializer, UserSerializer


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({'token': token.key, 'user': user_data})


class GatePassListCreateAPIView(ListCreateAPIView):
    serializer_class = GatePassSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            # student's own gatepasses
            return GatePass.objects.filter(student=user.student_profile).order_by('-created_at')
        elif user.role == 'warden':
            if user.gender:
                # CRITICAL: Gender-based filtering - wardens see ONLY requests from students matching their gender
                # Male wardens see ONLY male student requests, Female wardens see ONLY female student requests
                # Students without gender set will NOT appear
                return GatePass.objects.filter(
                    student__user__gender__iexact=user.gender
                ).exclude(
                    student__user__gender__isnull=True
                ).exclude(
                    student__user__gender=''
                ).order_by('-created_at')
            else:
                # If warden gender is not set, return empty queryset (safety measure)
                return GatePass.objects.none()
        # security/superadmin: return all gatepasses
        return GatePass.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        # expect student_id in payload (PrimaryKey of Student)
        serializer.save()


class WardenApproveAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
        user = request.user
        if user.role != 'warden':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        gp = get_object_or_404(GatePass, pk=pk)
        
        # CRITICAL: Enforce gender matching - prevent cross-gender approvals via API
        # Male wardens can ONLY approve male student requests
        # Female wardens can ONLY approve female student requests
        # If either gender is missing, block the approval
        if not user.gender or not gp.student.user.gender:
            return Response(
                {'detail': 'Gender information is required for both warden and student to process this request.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.gender != gp.student.user.gender:
            return Response(
                {'detail': 'You can only approve gatepass requests from students of your gender.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        gp.status = 'warden_approved'
        gp.warden_approval = user
        gp.save()
        return Response({'detail': 'Warden approval recorded'})


class SecurityApproveAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
        user = request.user
        if user.role != 'security':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        gp = get_object_or_404(GatePass, pk=pk)
        gp.status = 'security_approved'
        gp.security_approval = user
        gp.save()
        return Response({'detail': 'Security approval recorded'})
