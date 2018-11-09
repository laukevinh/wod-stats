from django.db import models

class Workout(models.Model):
    title = models.CharField(default="", max_length=200)
    description = models.TextField()
    tags = models.TextField()

class Post(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created = models.DateField()
    url = models.URLField()
    num_comments = models.IntegerField(default=0)
    num_male = models.IntegerField(default=0)
    num_female = models.IntegerField(default=0)
    num_rx = models.IntegerField(default=0)
    num_scale = models.IntegerField(default=0)

class Commenter(models.Model):
    first_name = models.CharField(default="", max_length=200) 
    last_name = models.CharField(default="", max_length=200) 
    picture_url = models.URLField()
    created = models.DateTimeField()

class Comment(models.Model):
    RX = "RX"
    SCALE = "SC"
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
    commenter = models.ForeignKey(Commenter, null=True, on_delete=models.SET_NULL)
    comment_text = models.TextField(default="")
    created = models.DateTimeField()
    scale = models.CharField(choices=SCALE_CHOICES, max_length=2, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=3, null=True)
    raw_score = models.CharField(default="", max_length=200)
    score = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    age = models.IntegerField(null=True)

