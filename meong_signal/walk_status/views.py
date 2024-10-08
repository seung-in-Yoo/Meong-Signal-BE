from rest_framework import generics, serializers, status
from rest_framework.response import Response
from .models import *
from .serializers import WalkRoomSerializer, LocationSerializer
from rest_framework.exceptions import ValidationError
from django.http import Http404
from django.http import JsonResponse
from django.conf import settings


# 사용자 정의 예외 클래스, 예외 발생 시 즉각적인 HTTP 응답을 위해 사용됩니다.
class ImmediateResponseException(Exception):
    # 예외 인스턴스를 생성할 때 HTTP 응답 객체를 받습니다.
    def __init__(self, response):
        self.response = response

# 산책방 목록 조회 및 생성을 위한 뷰 클래스로, DRF의 generics.ListCreateAPIView를 상속받습니다.
class WalkRoomListCreateView(generics.ListCreateAPIView):
    # 이 뷰에서 사용할 시리얼라이저를 지정합니다.
    serializer_class = WalkRoomSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드입니다.
    def get_queryset(self):
        try:
            # 요청의 쿼리 파라미터에서 'id' 값을 가져옵니다. 없다면 None을 반환합니다.
            user_id = self.request.query_params.get('id', None)

            # 이메일 파라미터가 없으면 ValidationError 예외를 발생시킵니다.
            if not user_id:
                raise ValidationError('Id 파라미터가 필요합니다.')

            # 산책방 객체를 필터링하여, 해당 이메일을 가진 사용자가 속한 채팅방을 찾습니다.
            return WalkRoom.objects.filter(
                owner__owner_id = user_id
            ) | WalkRoom.objects.filter(
                walk_user__walk_user_id = user_id
            )
        except ValidationError as e:
            # ValidationError 발생 시, 상태 코드 400과 함께 에러 상세 정보를 반환합니다.
            content = {'detail': e.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 다른 종류의 예외 발생 시, 상태 코드 400과 함께 에러 상세 정보를 반환합니다.
            # 여기에서 예외 정보를 로깅할 수 있습니다.
            content = {'detail': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 시리얼라이저의 컨텍스트를 설정하는 메소드입니다.
    def get_serializer_context(self):
        # 부모 클래스의 컨텍스트 가져오기 메소드를 호출합니다.
        context = super(WalkRoomListCreateView, self).get_serializer_context()
        # 컨텍스트에 현재의 요청 객체를 추가합니다.
        context['request'] = self.request
        return context

    # POST 요청을 처리하여 새로운 리소스를 생성하는 메소드입니다.
    def create(self, request, *args, **kwargs):
        # 요청 데이터로부터 시리얼라이저를 생성합니다.
        serializer = self.get_serializer(data=request.data)
        # 시리얼라이저의 유효성 검사를 수행합니다. 유효하지 않을 경우 예외가 발생합니다.
        serializer.is_valid(raise_exception=True)
        try:
            # 시리얼라이저를 통해 데이터 저장을 수행합니다.
            self.perform_create(serializer)
        except ImmediateResponseException as e:
            # 즉각적인 응답이 필요할 경우 예외를 통해 응답을 반환합니다.
            return e.response
        # 성공 헤더를 생성합니다.
        headers = self.get_success_headers(serializer.data)
        # 상태 코드 201를 반환하며 새로 생성된 데이터를 응답합니다.
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 시리얼라이저를 통해 데이터베이스에 객체를 저장하는 메소드입니다.
    def perform_create(self, serializer):
        # 요청 데이터에서 owner_id과 walk_user_id을 가져옵니다.
        owner_id = self.request.data.get('owner_id')
        walk_user_id = self.request.data.get('walk_user_id')

        # 해당 이메일로 Owner와 WalkUser를 가져오거나 없으면 생성합니다.
        owner, _ = Owner.objects.get_or_create(owner_id=owner_id)
        walk_user, _ = WalkUser.objects.get_or_create(walk_user_id=walk_user_id)
        
        # 동일한 owner과 walk_user을 가진 채팅방이 이미 있는지 확인합니다.
        existing_walkroom = WalkRoom.objects.filter(owner__owner_id=owner_id, walk_user__walk_user_id=walk_user_id).first()

        # 이미 존재하는 채팅방이 있다면 해당 채팅방의 정보를 시리얼라이즈하여 응답합니다.
        if existing_walkroom:
            serializer = WalkRoomSerializer(existing_walkroom, context={'request': self.request})
            raise ImmediateResponseException(Response(serializer.data, status=status.HTTP_200_OK))

        # 새 채팅방 객체를 저장합니다.
        serializer.save(owner=owner, walk_user=walk_user)

# 전송된 위치 목록을 조회하는 뷰 클래스로, DRF의 generics.ListAPIView를 상속받습니다.
class LocationListView(generics.ListAPIView):
    # 이 뷰에서 사용할 시리얼라이저를 지정합니다.
    serializer_class = LocationSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드입니다.
    def get_queryset(self):
        # URL 파라미터에서 'room_id' 값을 가져옵니다.
        room_id = self.kwargs.get('room_id')
        
        # room_id가 제공되지 않았을 경우 에러 메시지와 함께 400 상태 코드 응답을 반환합니다.
        if not room_id:
            content = {'detail': 'room_id 파라미터가 필요합니다.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # room_id에 해당하는 메시지 객체들을 쿼리셋으로 가져옵니다.
        queryset = Location.objects.filter(room_id=room_id)
        
        # 해당 room_id의 메시지가 존재하지 않을 경우 404 Not Found 예외를 발생시킵니다.
        if not queryset.exists():
            raise Http404('해당 room_id로 위치 정보를 찾을 수 없습니다.')

        # 쿼리셋을 반환합니다.
        return queryset