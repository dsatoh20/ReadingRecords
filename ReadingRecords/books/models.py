from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Developer(models.Model): # 開発者のモデルクラス
    name = models.CharField(max_length=100)
    mail = models.EmailField(max_length=100)
    gender = models.BooleanField()
    # age = models.IntegerField(default=0)
    birthday = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return '<Friend:id=' + str(self.id) + ',' + \
            self.name + '>'


class BookRecord(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,\
        related_name='message_owner')
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    title = models.TextField(max_length=100)
    first_author =models.TextField(max_length=100)
    pub_year = models.IntegerField(default=0)
    genre = models.TextField(max_length=100)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    summary = models.TextField(max_length=500)
    report = models.TextField(max_length=5000)
    good_count = models.IntegerField(default=0)
    chat_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.title) + '/' + str(self.first_author)
    class Meta:
        ordering = ('-pub_date',)
        
class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, \
        related_name='group_owner')
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return '<' + self.title + '(' + str(self.owner) + ')>'
    
class Friend(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, \
        related_name='friend_owner')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user) + '(group:"' + str(self.group) + '")'

class Good(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, \
        related_name='good_owner')
    bookrecord = models.ForeignKey(BookRecord, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'good for "' + str(self.bookrecord) + '" (by ' + \
            str(self.owner) + ')'

class Chat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_owner')
    bookrecord = models.ForeignKey(BookRecord, on_delete=models.CASCADE)
    comment = models.TextField(max_length=140)
    pub_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "chat about " + str(self.bookrecord) 
    class Meta:
        ordering = ('pub_date',)

# class NewsRecord(models.Model):
# class CinemaRecord(models.Model):
# class PaperRecord(models.Model):
# class RakugoRecord(models.Model):
# class MusicRecord(models.Model):