from django import forms
from.models import BookRecord, Group, Friend, Good, Chat
from django.contrib.auth.models import User

class BookRecordForm(forms.ModelForm):
    class Meta:
        model = BookRecord
        fields = ['group', 'title', 'first_author', 'pub_year', 'genre', 'score', 'summary', 'report']
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['owner', 'title']
        
class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['owner', 'user', 'group']
        
class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['owner', 'bookrecord']

        
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.MultipleChoiceField(
            choices=[(item.title, item.title) for item in \
                Group.objects.filter(owner__in=[user, public])],
            widget=forms.CheckboxSelectMultiple(),
        )

class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title) \
                for item in Group.objects.filter(owner=user)],\
            widget=forms.Select(attrs={'class':'form-control'}),
        )
        
class FriendsForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(\
            choices=[(item.user, item.user) for item in friends], \
                widget=forms.CheckboxSelectMultiple(), \
                    initial=vals,
        )

class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=50, \
        widget=forms.TextInput(attrs={'class': 'form-control'}))

class PostForm(forms.Form):
    title = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': 1,
                                     'placeholder': "俺か、俺以外か　ローランドという生き方"}))
    first_author = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':1,
                                     'placeholder': "ROLAND"}))
    pub_year = forms.IntegerField(max_value=3000, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':1,
                                     'placeholder': "2019"}))
    genre = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':1,
                                     'placeholder': '自己啓発'}))
    score = forms.IntegerField(max_value=10, min_value=1, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':1,
                                     'placeholder': "1~10の10段階評価"}))
    summary = forms.CharField(max_length=500, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':4,
                                     'placeholder': "500字以内で入力してください。"}))
    report = forms.CharField(max_length=5000, \
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows':10,
                                     'placeholder': "5000字以内で入力してください。"}))
    
    
    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['group'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title)\
                for item in Group.objects.filter(owner__in=[user, public])],
            widget=forms.Select(attrs={'class':'form-control'}),
        )
        
        
class ChatForm(forms.Form):
    comment = forms.CharField(max_length=140, min_length=0,
                               widget=forms.Textarea(attrs={'class':'form-control',
                                                            'row':2,
                                                            'placeholder': '140字以内で入力してください。'}))