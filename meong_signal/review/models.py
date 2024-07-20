from django.db import models
from account.models import User
from dog.models import Dog
from django.core.validators import MinValueValidator, MaxValueValidator
from walk.models import Walk

class UserReview(models.Model):
    walk_id = models.OneToOneField(Walk, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.CharField(max_length=50)

    @property
    def user(self): # user: 산책 한 장본인 -> 리뷰 받은 사람
        return self.walk_id.user_id
    
    @property
    def owner(self): # owner: 강아지 빌려준 견주 -> 리뷰 남긴 사람
        return self.walk_id.owner_id
    
    @property
    def dog(self): # 같이 산책한 강아지
        return self.walk_id.dog_id

    def __str__(self):
        r = f'리뷰 : 견주 id {self.owner} -> 산책자 id {self.owner}'
        return r

class WalkingReview(models.Model):
    walk_id = models.OneToOneField(Walk, on_delete=models.CASCADE)
    content = models.CharField(max_length=50)

    @property
    def user(self): # user: 산책 한 장본인 -> 리뷰 남긴 사람
        return self.walk_id.user_id
    
    @property
    def owner(self): # owner: 강아지 빌려준 견주 -> 리뷰 받은 사람
        return self.walk_id.owner_id
    
    @property
    def dog(self): # 같이 산책한 강아지
        return self.walk_id.dog_id

    def __str__(self):
        r = f'산책 리뷰 : 산책자 id {self.user} -> 견주 id {self.owner}'
        return r


class ReviewTag(models.Model):
    review_id = models.ForeignKey(WalkingReview, on_delete=models.CASCADE)
    number = models.IntegerField()

    @property
    def owner(self): # owner: 강아지 빌려준 견주
        return self.review_id.owner
    
    @property
    def dog(self): # 같이 산책한 강아지
        return self.review_id.dog
    
    def __str__(self):
        r = f'강아지 id {self.dog} -> 태그 번호 {self.number}'
        return r