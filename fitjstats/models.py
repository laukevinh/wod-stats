from django.db import models

class Workout(mondels.Model):
    title = models.CharField(default="")
    description = models.CharField()
    tags = models.CharField(default="")

class Post(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created = models.DateField()
    url = models.URLField()
    num_comments = models.IntegerField(default=0)

class Comment(models.Model):
    RX = "rx"
    SCALE = "scale"
    SCALE_CHOICES = (
        (None, "n/a"),
        (RX, "rx"),
        (SCALE, "scale")
    )
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"
    GENDER_CHOICES = (
        (None, "n/a"),
        (MALE, "male"),
        (FEMALE, "female"),
        (OTHER, "other")
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    commenter = models.ForeignKey(Commenter, on_delete=models.SET_NULL)
    comment_text = models.CharField()
    scale = models.CharField(choices=SCALE_CHOICES)
    gender = models.CharField(choices=GENDER_CHOICES)
    raw_score = models.CharField(default="")
    score = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    age = models.IntegerField(null=True)

class Commenter(models.Model):
    first_name = models.CharField(default="") 
    last_name = models.CharField(default="") 
    picture_url = models.URLField()
    created = models.DateField()
