from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from dog.models import DogTag

class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = '__all__'

class UserReviewInputSerializer(serializers.ModelSerializer):
    meong = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserReview
        fields = ('rating', 'content', 'walk_id', 'meong')

class WalkReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkingReview
        fields = ('content', 'walk_id',)

class ReviewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTag
        fields = ('number',)

class WalkReviewRegisterSerializer(serializers.Serializer):
    review = WalkReviewSerializer()
    tags = ReviewTagSerializer(many=True)
    meong = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        print("validated_data:", validated_data)
        review_data = validated_data['review']
        print("review_data:", review_data)

        walk_id = review_data['walk_id']
        walk = Walk.objects.get(id = walk_id.id)
        owner = walk.owner_id

        review_data['user_id'] = user
        review_data['owner_id'] = owner
        review = WalkingReview.objects.create(**review_data)

        if 'tags' in validated_data:
            tags_data = validated_data['tags']
            for tag_data in tags_data:
                ReviewTag.objects.create(review_id = review, **tag_data)
                
                # DOG_TAG 테이블에도 반영
                try: # 해당 강아지에 대한 동일 태그가 나온 적이 있다면, count만 1로 늘려줌
                    dog_tag = DogTag.objects.get(dog_id = review.dog, number=tag_data['number'])
                    dog_tag.count += 1
                    dog_tag.save()
                except ObjectDoesNotExist: # 나온 적 없다면 만들어줌
                    DogTag.objects.create(dog_id = review.dog, number=tag_data['number'], count=1)
                    
        return review