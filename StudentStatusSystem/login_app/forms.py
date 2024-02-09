from django import forms
from django.contrib.auth.forms import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import OfferedSubject, Registration, Student, Subject, Term, UserProfile
from .validators import validate_email

class DateInput(forms.DateInput):
    input_type = 'date'

class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, validators = [validate_email])
    #first_name = forms.CharField(max_length=50)
    #last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        #user.first_name = self.cleaned_data['first_name']
        #user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user

class ExtendedUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(ExtendedUserChangeForm, self).__init__(*args, **kwargs)
        del self.fields['password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('role', 'first_name', 'middle_name', 'last_name', 'sex', 'contact_number', 'staff_id', 'department', 'birthday')
        widgets = {
            'birthday' : DateInput()
        }

class AdminUserProfileChangeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('role', 'first_name', 'middle_name', 'last_name', 'sex', 'contact_number', 'staff_id', 'department', 'birthday')
        widgets = {
            'birthday' : DateInput()
        }

class UserProfileChangeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'middle_name', 'last_name', 'contact_number', 'staff_id', 'department', 'birthday')
        widgets = {
            'birthday' : DateInput()
        }

class UserChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s %s" % (obj.first_name, obj.last_name)

class StudentCreationForm(forms.ModelForm):
    advisor = UserChoiceField(queryset=UserProfile.objects.filter(role__in=('PROGRAM ADVISOR', 'THESIS ADVISOR')))
    class Meta:
        model = Student
        fields = ('student_number', 'first_name', 'middle_name', 'last_name', 'email', 'sex', 'contact_number', 
                  'birthday', 'graduate', 'program', 'enrollment', 'advisor')
        widgets = {
            'birthday' : DateInput()
        }

class TermCreationForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ('title', 'start_date', 'end_date')
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'title' : forms.fields.TextInput(attrs={'placeholder': 'A.Y. YYYY-YYYY, [Semester/Midyear]'}),
        }

class OfferingCreationForm(forms.ModelForm):
    class Meta:
        model = OfferedSubject
        fields = ('subject_name', 'subject_title', 'units', 'department', 'class_code', 'lecture', 'lab')

class OfferingChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.subject_name)

class TermChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.title)

class SubjectCreationForm(forms.ModelForm):
    term = TermChoiceField(queryset=Term.objects.all())
    subject_offered = OfferingChoiceField(queryset=OfferedSubject.objects.all())
    professor = UserChoiceField(queryset=UserProfile.objects.filter(role__in = ('PROGRAM ADVISOR', 'THESIS ADVISOR', 'FACULTY'))) 
    class Meta: 
        model = Subject
        fields = ('term', 'subject_offered', 'professor','section', 'slots')

class SubjectChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        subject = obj.subject_offered
        item = OfferedSubject.objects.get(id=subject.id)
        return "%s" % (item.subject_name)

class RegistrationCreationForm(forms.ModelForm):
    student = UserChoiceField(queryset=Student.objects.all()) # temporary
    subject = SubjectChoiceField(queryset=Subject.objects.all())
    class Meta:
        model = Registration
        fields = ('student','subject', 'completion', 'grade')

class SubjectForm(forms.ModelForm):
    subject =  SubjectChoiceField(queryset=Subject.objects.all())

    class Meta:
        model = Subject
        fields = ['subject']

class TermForm(forms.ModelForm):
    term = TermChoiceField(queryset=Term.objects.all())

    class Meta:
        model = Term
        fields = ['term']

class AdvisorDropdown(forms.ModelForm):
    advisor = UserChoiceField(queryset=UserProfile.objects.filter(role__in = ('PROGRAM ADVISOR', 'THESIS ADVISOR')))

    class Meta:
        model = UserProfile
        fields = ['advisor']

    def __init__(self, *args, **kwargs):
        super(AdvisorDropdown, self).__init__(*args, **kwargs)
        self.fields['advisor'].label = ""