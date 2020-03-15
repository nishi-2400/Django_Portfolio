from django import forms
from django.contrib.auth.models import User
from .models import Restaurant, Meal

# ユーザーアカウント作成
class UserSignupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'
    
    email = forms.EmailField(label='メールアドレス', max_length=100, required=True)
    password = forms.CharField(label='パスワード  ***”test1234”のように他サイトで使い回しているパスワードは避けてください。', widget=forms.PasswordInput(), max_length=10, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


# ユーザーアカウント編集
class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'
        
    email = forms.EmailField(label='メールアドレス', max_length=100, required=True)
    # password = forms.CharField(label='パスワード', widget=forms.PasswordInput(), max_length=10, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


# レストランアカウント作成
class RestaurantSignupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label != 'ロゴ':
                field.widget.attrs['placeholder'] = field.label
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-custom'
                
    class Meta:
        model = Restaurant
        fields = ('name', 'phone', 'address', 'logo')
        labels = {
            'name': 'レストラン名',
            'phone': '電話番号',
            'address': '住所',
            'logo': 'ロゴ',
        }


# 料理データ追加
class ResraurantMealForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label != '画像':
                field.widget.attrs['placeholder'] = field.label
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-custom'

    class Meta:
        model = Meal
        fields = ('name', 'short_description', 'image', 'price')
        labels = {
            'name': '料理名',
            'short_description': '詳細',
            'image': '画像',
            'price': '価格',
        }