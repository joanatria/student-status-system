import logging
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import ProtectedError, Count
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from collections import Counter

from login_app.forms import ExtendedUserChangeForm, ExtendedUserCreationForm, OfferingCreationForm, RegistrationCreationForm, StudentCreationForm, SubjectChoiceField, SubjectCreationForm, SubjectForm, TermCreationForm, UserProfileForm, TermForm, AdvisorDropdown, UserProfileChangeForm
from login_app.models import OfferedSubject, Registration, Student, Subject, Term, UserProfile

from django.contrib import messages
import csv

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def render_login(request):
    response = redirect('/accounts/login/')
    return response

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['x'] = UserProfile.objects.get(user=user_id)

    return render(request, "dashboard.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def landing_page(request):
    user_id = request.user.id
    profile = UserProfile.objects.filter(user=user_id)
    if profile.exists():
        user_role = profile[0].role
        print("Role retrieved:"+user_role)
        if user_role == 'ADMIN':
            return HttpResponseRedirect(reverse("admin_dashboard"))
        else:
            return dashboard(request)
    else:
        return HttpResponseRedirect(reverse("manage_tables"))

def perform_login(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            return HttpResponseRedirect("/")
        
        user_obj = authenticate(request, username=username, password=password)
        if user_obj is not None:
            login(request, user_obj)
            return HttpResponseRedirect(reverse("dashboard"))
        else:
            return HttpResponseRedirect("/")
        
# https://www.youtube.com/watch?v=Tja4I_rgspI

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_user(request):
    context={}
    user = None
    profile_form = None
    form_errors = {}
    profile_errors = {}

    if request.method == "POST":
        form = ExtendedUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            context['message'] = 'User saved!'
            # Redirect or perform any necessary action upon successful form submission
            # Replace '/success/' with your desired success URL
        else:
            form_errors = form.errors.as_json()
            profile_errors = profile_form.errors.as_json()
            context['message'] = 'User failed to save!'
            # Here you might add additional handling, logging, or error messages
            # depending on your specific needs

    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()

    context['form'] = form
    context['profile_form'] = profile_form
    context['form_errors'] = form_errors
    context['profile_errors'] = profile_errors

    return render(request, 'create_user.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_user(request, id):
    user_profile = get_object_or_404(UserProfile, id=id)
    obj = get_object_or_404(User, pk=user_profile.user_id)
    try:
        if request.method == 'POST':
            obj.delete()
            return landing_page(request)
    except ProtectedError as e:
        messages.error(request, 'Cannot Delete, protected by referencing key!')
        return redirect(request.META['HTTP_REFERER'])
    
@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_subject(request, id):
    obj = get_object_or_404(Subject, pk=id)
    try:
        if request.method == 'POST':
            obj.delete()
            return redirect(request.META['HTTP_REFERER'])
    except ProtectedError as e:
        messages.error(request, 'Cannot Delete, protected by referencing key!')
        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_term(request, id):
    obj = get_object_or_404(Term, pk=id)
    try:
        if request.method == 'POST':
            obj.delete()
            return academic_term_page(request)
    except ProtectedError as e:
        messages.error(request, 'Cannot Delete, protected by referencing key!')
        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    userprofile = UserProfile.objects.get(user=user.id)

    if request.method == 'POST':
        form = ExtendedUserChangeForm(request.POST, instance=user)
        profile_form = UserProfileChangeForm(request.POST, instance=userprofile)
        print(form.is_valid())
        print(profile_form.is_valid())
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
        else:
            print(profile_form.errors.as_data())

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_password(request, user_id):
    userprofile = UserProfile.objects.get(pk=user_id)
    user = User.objects.get(pk=userprofile.user.id)

    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=userprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()

            return landing_page(request)
        else:
            print(form.errors.as_data())
    
    userprofile = UserProfile.objects.get(pk=user_id)
    user = User.objects.get(pk=userprofile.user.id)

    context ={}
    context['user_profile'] = userprofile
    context['form'] = ExtendedUserCreationForm(instance=user)
    context['profile_form'] = UserProfileForm(instance=userprofile)
    context['x'] = userprofile

    # Render the edit profile form with the user's current information
    return render(request, 'update_password.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
def update_profile(request, user_id):
    userprofile = UserProfile.objects.get(pk=user_id)
    user = User.objects.get(pk=userprofile.user.id)

    if request.method == 'POST':
        form = ExtendedUserChangeForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=userprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()

            return landing_page(request)
        else:
            print(form.errors.as_data())
    
    userprofile = UserProfile.objects.get(pk=user_id)
    user = User.objects.get(pk=userprofile.user.id)

    context ={}
    context['user_profile'] = userprofile
    context['form'] = ExtendedUserChangeForm(instance=user)
    context['profile_form'] = UserProfileForm(instance=userprofile)
    context['x'] = userprofile

    # Render the edit profile form with the user's current information
    return render(request, 'update_profile.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def grade_csv(request):
    subject_pk = request.POST.get('subject')
    print(subject_pk)
    try: 
        csv_file = request.FILES.get("csv_file")
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not a valid CSV type')
            return landing_page(request)
        
        file_data = csv_file.read().decode("utf-8")
        lines = file_data.split("\n")

        for line in lines:
            fields = line.split(",")
            
            # Check if there are enough fields in the line
            if len(fields) >= 3:
                student_number = fields[1].strip()
                new_grade = fields[2].strip()

                try:
                    studentToUpdate = Student.objects.get(student_number=student_number)
                    registration = Registration.objects.get(student=studentToUpdate, subject__id=subject_pk)

                    old_weighted_grade = registration.subject.subject_offered.units * registration.grade
                    print('old weighted_grade = ' + str(old_weighted_grade))

                    try:
                        # Convert the grade to a float
                        grade_value = float(new_grade)
                    except ValueError:
                        messages.error(request, f"Invalid grade value: {new_grade}")
                        continue  # Skip the current line if the grade is not a valid number

                    registration.grade = grade_value

                    old_completion = registration.completion

                    if new_grade == '0':
                        registration.completion = 'INCOMPLETE'
                    elif new_grade == '5':
                        registration.completion = 'FAILED'
                    elif new_grade == '4':
                        registration.completion = 'CONDITIONAL'
                    else:
                        registration.completion = 'PASSED'

                    if registration.subject.subject_offered.units != 0:
                        weighted_grade = registration.subject.subject_offered.units * registration.grade
                        print('weighted_grade = ' + str(weighted_grade))

                        if old_completion == 'INCOMPLETE' and registration.completion != 'INCOMPLETE':
                            studentToUpdate.completed_units += registration.subject.subject_offered.units
                            studentToUpdate.total_grade += weighted_grade
                        elif old_completion != 'INCOMPLETE' and registration.completion == 'INCOMPLETE':
                            studentToUpdate.completed_units -= registration.subject.subject_offered.units
                            studentToUpdate.total_grade -= old_weighted_grade
                        else:  # not INC to not INC
                            studentToUpdate.total_grade -= old_weighted_grade
                            studentToUpdate.total_grade += weighted_grade

                        print('total grade = ' + str(studentToUpdate.total_grade))
                        if studentToUpdate.completed_units != 0:
                            studentToUpdate.gwa = (studentToUpdate.total_grade) / studentToUpdate.completed_units
                        else:
                            studentToUpdate.gwa = 0

                        studentToUpdate.save(update_fields=['completed_units', 'gwa', 'total_grade'])    
                    registration.save(update_fields=['grade', 'completion'])

                except ObjectDoesNotExist as e:
                    messages.error(request, f"Object not found: {repr(e)}")
                except MultipleObjectsReturned as e:
                    messages.error(request, f"Multiple objects returned for student number {student_number}: {repr(e)}")
                except Exception as e:
                    logging.getLogger("error_logger").error(f"Error processing line: {line}. {repr(e)}")
                    messages.error(request, f"Error processing line: {line}. {repr(e)}")

    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. " + repr(e))
        messages.error(request, "Unable to upload file. " + repr(e))

    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def download_template(request):
    subject_pk = request.POST.get('subject')
    subjectToFetch = Subject.objects.get(pk=subject_pk)
    registrationOfSubject = Registration.objects.filter(subject=subjectToFetch).order_by('student__last_name')
    filename = subjectToFetch.section +'_'+ subjectToFetch.subject_offered.subject_name
    filename = filename.replace(' ', '')

    response = HttpResponse(content_type='text/csv')  
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'  
    writer = csv.writer(response)  

    for registration in registrationOfSubject:
        writer.writerow([registration.student.last_name,registration.student.student_number,registration.grade])
    return response  

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_student(request):
    context = {
        'student_form': StudentCreationForm(),  # Add the form to the context
    }
    
    if request.method == "POST":
        try:
            student_form = StudentCreationForm(request.POST)

            if student_form.is_valid():
                student = student_form.save(commit=False)
                current_term = Term.objects.get(current_term=1)

                print('form is valid')

                # required_units based on program
                program_units_dict = {
                    'BS COMPUTER SCIENCE': 155,
                    'BS BIOCHEMISTRY': 155,
                    'BS APPLIED PHYSICS': 155,
                }
                
                student.required_units = program_units_dict[student.program]
                student.first_enrollment = current_term
                student.last_enrollment = current_term
                student.save()

                context['message'] = 'Student saved!'
                return render(request, 'create_student.html', context)
            
        except Exception:
                
                context['message'] = 'Student failed to save!'
                return render(request, 'create_student.html', context)
    
    return render(request, 'create_student.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_student(request, student_id):
    
    try:
        if request.method == "POST":
            student_to_delete = get_object_or_404(Student, pk=student_id)
            deleted_student = Student.objects.get(id=0)
            registrations = Registration.objects.filter(student=student_to_delete)
            for registration in registrations:
                registration.student = deleted_student
                registration.save(update_fields=['student'])
            student_to_delete.delete()
    except ProtectedError as e:
        messages.error(request, 'Cannot Delete, protected by referencing key!')
        return redirect(request.META['HTTP_REFERER'])

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_student(request, student_id):
    student = Student.objects.get(id=student_id)        
    context = {
        'student_form': StudentCreationForm(instance=student),  # Add the form to the context
        'student': student,
        'advisors' : UserProfile.objects.filter(role__in = ('PROGRAM ADVISOR', 'THESIS ADVISOR')),
    }

    if request.method == "POST":
        student_form = StudentCreationForm(request.POST, instance=student)

        if student_form.is_valid():
            student_update = student_form.save(commit=False)
            current_term = Term.objects.get(current_term=1)

            # required_units based on program
            program_units_dict = {
                'BS COMPUTER SCIENCE': 158,
                'BS BIOCHEMISTRY': 158,
                'BS APPLIED PHYSICS': 158,
            }

            student_update.required_units = program_units_dict[student.program]
            
            if student.enrollment != 'ENROLLED' and student_update.enrollment == 'ENROLLED':
                student_update.last_enrollment = current_term

            student_update.save()
            return redirect(request.META['HTTP_REFERER'])
    
    return render(request, 'edit_student.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_student(request):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['student_form'] =  StudentCreationForm()

    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'term' not in request.POST:
        term_filter = ''
    else:
        term_filter = request.POST.get('term')

    terms_filtered = Term.objects.filter(title__contains=term_filter)

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(program='BS COMPUTER SCIENCE', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(program='BS BIOCHEMISTRY', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(program='BS APPLIED PHYSICS', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)

    context['term_filter'] = term_filter
    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter
    context['programs'] = ["BSCS","BSBC","BSAP"]

    return render(request, 'manage_student.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_registration(request):

    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        registered = request.POST.get('registered')
        print(registered)

        student = Student.objects.get(id=student_id)

        if registered == 'true':
            # register student
            student.enrollment = 'ENROLLED'
            current_term = Term.objects.get(current_term=1)
            student.last_enrollment = current_term

            student.save(update_fields=['enrollment', 'last_enrollment'])

        else:
            # unregister student
            student.enrollment = 'UNENROLLED'
            student.save(update_fields=['enrollment'])

    
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_registration(request):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['student_form'] =  StudentCreationForm()

    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'term' not in request.POST:
        term_filter = ''
    else:
        term_filter = request.POST.get('term')

    terms_filtered = Term.objects.filter(title__contains=term_filter)

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(program='BS COMPUTER SCIENCE', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(program='BS BIOCHEMISTRY', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(program='BS APPLIED PHYSICS', first_enrollment__in=terms_filtered, last_name__contains=last_name_filter, student_number__contains=student_number_filter)

    context['term_filter'] = term_filter
    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter
    context['programs'] = ["BSCS","BSBC","BSAP"]

    return render(request, 'manage_registration.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registration(request):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    
    if 'name' not in request.POST:
        search=''
    else:
        search = request.POST.get('name')

    context['students'] = Student.objects.filter(enrollment='ENROLLED', last_name__contains=search)
    context['search'] = search

    return render(request, 'registration.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def graduate_all(request, term_id):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    
    context['term'] = Term.objects.get(id=term_id)

    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')
        print(student_number_filter)

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name') 
        print(last_name_filter)

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(program='BS COMPUTER SCIENCE', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(program='BS BIOCHEMISTRY', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(program='BS APPLIED PHYSICS', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)

    if request.method == 'POST':
        students = context['students']
        for student in students:
            registrations = Registration.objects.filter(student=student)
            effective_units = student.completed_units
            for registration in registrations:
                if registration.grade > 3:
                    effective_units -= registration.subject.subject_offered.units
            if effective_units >= student.required_units:
                student.graduate = 'GRADUATED'
                student.save(update_fields=['graduate'])
            
    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter
    context['programs'] = ["BSCS","BSBC","BSAP"]
             
    return render(request, "manage_graduation.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_graduation_status(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        graduate = request.POST.get('graduate')
        print(graduate)

        student = Student.objects.get(id=student_id)

        if graduate == 'true':
            student.graduate = 'GRADUATED'
            student.save(update_fields=['graduate'])
        else:
            student.graduate = 'ONGOING'
            student.save(update_fields=['graduate'])

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_graduation(request, term_id):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    
    context['term'] = Term.objects.get(id=term_id)
    
    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(program='BS COMPUTER SCIENCE', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(program='BS BIOCHEMISTRY', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(program='BS APPLIED PHYSICS', first_enrollment=term_id, last_name__contains=last_name_filter, student_number__contains=student_number_filter)

    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter
    context['programs'] = ["BSCS","BSBC","BSAP"]

    return render(request, "manage_graduation.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def graduation_select_term(request):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role

    if 'title' not in request.POST:
        context['terms'] = Term.objects.all()
        context['search'] = ''
    else:
        search = request.POST.get('title')
        context['search'] = search
        print(search)
        context['terms'] = Term.objects.filter(title__contains=search)

    return render(request, 'graduation_select_term.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_term(request):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['term_form'] = TermCreationForm()

    if request.method == "POST":
        term_form = TermCreationForm(request.POST)
        if term_form.is_valid():
            term = term_form.save(commit=False)
            term.current_term = False
            term.save()
            context['message'] = 'Term created'
        else:
            context['message'] = 'Term failed to save'
    
    return render(request, 'add_term.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_offering(request):
    offering_form = OfferingCreationForm()  # Instantiate an instance of the form
    context = {
        'offering_form': offering_form,  # Add the form to the context
    }
    if request.method == "POST":
        offering_form = OfferingCreationForm(request.POST)
        if offering_form.is_valid():
            offering = offering_form.save()
            context['message'] = 'Course offering created'
        else:
            context['message'] = 'Course offering failed to save'
    
    return render(request, 'create_offering.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_offering(request, offering_id):
    try:
        if request.method == "POST":
            offering_to_delete = get_object_or_404(OfferedSubject, pk=offering_id)
            offering_to_delete.delete()
    except ProtectedError as e:
        messages.error(request, 'Cannot Delete, protected by referencing key!')
        return redirect(request.META['HTTP_REFERER'])

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_offering(request, offering_id):
    context={}
    offering_to_edit = OfferedSubject.objects.get(id=offering_id)
    
    if request.method == "POST":
        offering_form = OfferingCreationForm(request.POST, instance=offering_to_edit)
        if offering_form.is_valid():
            offering = offering_form.save()

    offering_to_edit = OfferedSubject.objects.get(id=offering_id)
    offering_form = OfferingCreationForm(instance=offering_to_edit)  # Instantiate an instance of the form
    context['offering_form'] = offering_form
    context['offering'] = offering_to_edit

    return render(request, 'edit_offering.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def course_offerings(request):
    context = {
        'offerings' : OfferedSubject.objects.all(),
    }

    if 'search' not in request.POST:
        context['search'] = ''
    else:
        search = request.POST.get('search')
        context['offerings'] = OfferedSubject.objects.filter(subject_name__contains=search)
        context['search'] = search

    return render(request, 'courses_offered.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subject(request, subject_id):
    context ={}
    edit_subject = Subject.objects.get(id=subject_id)
    
    if request.method == "POST":
        subject_form = SubjectCreationForm(request.POST, instance=edit_subject)

        if subject_form.is_valid():
            subject = subject_form.save()
    
    edit_subject = Subject.objects.get(id=subject_id)
    currentTerm = Term.objects.get(current_term=1)
    context['subjects'] = Subject.objects.filter(term=currentTerm)
    context['subject_form'] = SubjectCreationForm(instance=edit_subject)
    context['subject'] = edit_subject
    context['term'] = edit_subject.term

    return render(request, 'edit_subject.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_subject(request, term_id):
    context ={}

    if request.method == "POST":
        subject_form = SubjectCreationForm(request.POST)

        if subject_form.is_valid():
            subject = subject_form.save()
            context['message'] = 'Course saved!'
        else:
            context['message'] = 'Course failed to save!'

    addforterm = Term.objects.get(id=term_id)

    
    currentTerm = Term.objects.get(current_term=1)
    context['subjects'] = Subject.objects.filter(term=currentTerm)
    context['subject_form'] = SubjectCreationForm(initial={'term':addforterm})
    context['term'] = addforterm
    
    return render(request, 'create_subject.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_registration(request):
    if request.method == "POST":
        registration_form = RegistrationCreationForm(request.POST)

        if registration_form.is_valid():
            registration = registration_form.save()
            subject = Subject.objects.get(pk=registration.subject_id)
            subject.enrolled += 1
            subject.save(update_fields=["enrolled"])

    return landing_page(request)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def set_current_term(request, term_id):

    if request.method == "POST":
        old_current = Term.objects.get(current_term=1)
        new_current = Term.objects.get(id=term_id)

        old_current.current_term = False
        new_current.current_term = True

        old_current.save()
        new_current.save()

        enrolled = Student.objects.filter(enrollment='ENROLLED')
        for student in enrolled:
            student.enrollment = 'UNENROLLED'
            student.save(update_fields=["enrollment"])

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_term(request, term_id):
    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['users'] = User.objects.exclude(id=user_id)
    context['term'] = Term.objects.get(id=term_id)

    if 'name' not in request.POST:
        search = ''
    else:
        search = request.POST.get('name')

    if 'professor' not in request.POST:
        professor_filter = ''
    else:
        professor_filter = request.POST.get('professor')

    context['search'] = search
    context['professor_filter'] = professor_filter

    context['subjects'] = Subject.objects.filter(term__id=term_id, subject_offered__subject_name__contains=search, professor__last_name__contains=professor_filter)
    

    if not context['subjects']:
         context['no_subjects'] = 'No subjects found'


    return render(request, 'view_term.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def academic_term_page(request):
    # user_id = request.user.id
    # profile = UserProfile.objects.get(user=user_id)
    # user_role = profile.role
    # if user_role != 'ADMIN':
    #     # Invalid access, update to send message
    #     return landing_page(request)

    context ={}
    currentTerm = Term.objects.get(current_term=1)
    context['term'] = currentTerm
    context['subjects'] = Subject.objects.filter(term=currentTerm)
    context['subject_form'] = SubjectCreationForm()
    
    if 'term' not in request.POST:
        term_filter = ''
    else:
        term_filter = request.POST.get('term')

    context['terms'] = Term.objects.filter(title__contains=term_filter)
    context['search'] = term_filter

    return render(request, 'academic_term.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_tables(request):
    context ={}
    context['form'] = ExtendedUserCreationForm()
    context['profile_form'] = UserProfileForm()
    context['student_form'] = StudentCreationForm()
    context['term_form'] = TermCreationForm()
    context['offering_form'] = OfferingCreationForm()
    context['subject_form'] = SubjectCreationForm()
    context['registration_form'] = RegistrationCreationForm()

    user_id = request.user.id
    context['profile'] = UserProfile.objects.filter(user=user_id) 
    context['users'] = User.objects.exclude(id=user_id)
    context['userprofiles'] = UserProfile.objects.exclude(user=user_id)
    context['subjects'] = Subject.objects.all()

    context['chooseSubject'] = SubjectForm()
    context['chooseTerm'] = TermForm()

    return render(request, "tables.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    context ={}
    list(messages.get_messages(request))

    user_id = request.user.id
    context['profile'] = UserProfile.objects.filter(user=user_id) 
    context['users'] = User.objects.exclude(id=user_id)
    context['userprofiles'] = UserProfile.objects.exclude(user=user_id)

    if 'staff_id' not in request.POST:
        staff_id_filter = ''
    else:
        staff_id_filter = request.POST.get('staff_id')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'role' not in request.POST:
        context['role_filter'] = 'None'
        context['userprofiles'] = UserProfile.objects.filter(last_name__contains=last_name_filter, staff_id__contains=staff_id_filter).exclude(user=user_id)
    else:
        role_filter = request.POST.get('role')
        context['role_filter'] = role_filter
        if role_filter == 'None':
            context['userprofiles'] = UserProfile.objects.filter(last_name__contains=last_name_filter, staff_id__contains=staff_id_filter).exclude(user=user_id)
        else:
            context['userprofiles'] = UserProfile.objects.filter(role=role_filter, last_name__contains=last_name_filter, staff_id__contains=staff_id_filter).exclude(user=user_id)
        
    context['last_name_filter'] = last_name_filter
    context['staff_id_filter'] = staff_id_filter
    context['roles'] = ["ADMIN","STAFF","THESIS ADVISOR", "PROGRAM ADVISOR", "FACULTY"]

    return render(request, "admin_dashboard.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def thesis_advisor_dashboard(request):
    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['x'] = UserProfile.objects.get(user=user_id)

    return render(request, "dashboard.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def program_advisor_dashboard(request):
    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['x'] = UserProfile.objects.get(user=user_id)

    return render(request, "dashboard.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def faculty_dashboard(request):
    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['x'] = UserProfile.objects.get(user=user_id)

    return render(request, "dashboard.html", context)

def perform_logout(request):
    request.session.flush()
    logout(request)
    return HttpResponseRedirect("/accounts/login")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def grades_student(request):
    context ={}

    user_id = request.user.id
    context['profile'] = UserProfile.objects.filter(user=user_id) 
    context['users'] = User.objects.exclude(id=user_id)
    context['userprofiles'] = UserProfile.objects.exclude(user=user_id)

    return render(request, "grades_student.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def grades_course(request):
    context ={}

    user_id = request.user.id
    profile = UserProfile.objects.get(user=user_id) 
    currentTerm = Term.objects.get(current_term=1)
    context['user_role'] = UserProfile.objects.get(user=user_id).role

    if context['user_role'] == 'STAFF':
        if 'name' not in request.POST:
            context['subjects'] = Subject.objects.filter(term=currentTerm)
            context['search'] = ''
        else:
            search = request.POST.get('name')
            context['search'] = search
            print(search)
            offerings = OfferedSubject.objects.filter(subject_name__contains=search)
            context['subjects'] = Subject.objects.filter(term=currentTerm, subject_offered__in=offerings)
    else:
        if 'name' not in request.POST:
            context['subjects'] = Subject.objects.filter(professor=profile, term=currentTerm)
            context['search'] = ''
        else:
            search = request.POST.get('name')
            context['search'] = search
            print(search)
            offerings = OfferedSubject.objects.filter(subject_name__contains=search)
            context['subjects'] = Subject.objects.filter(professor=profile, term=currentTerm, subject_offered__in=offerings)

    
    if not context['subjects']:
         context['no_subjects'] = 'No subjects found'

    return render(request, "courses.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_student_grades(request):
    context ={}

    user_id = request.user.id
    context['profile'] = UserProfile.objects.filter(user=user_id) 
    context['users'] = User.objects.exclude(id=user_id)
    context['userprofiles'] = UserProfile.objects.exclude(user=user_id)

    return render(request, "edit_student_grades.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_grade(request, registration_id):
    registration = Registration.objects.get(id=registration_id)

    old_weighted_grade = registration.subject.subject_offered.units * registration.grade
    print('old weighted_grade = ' + str(old_weighted_grade))

    new_grade = request.POST.get('grade')
    registration.grade = float(new_grade)

    old_completion = registration.completion

    if new_grade == '0':
        registration.completion = 'INCOMPLETE'
    elif new_grade == '5':
        registration.completion = 'FAILED'
    elif new_grade == '4':
        registration.completion = 'CONDITIONAL'
    else:
        registration.completion = 'PASSED'

    student_pk = registration.student.id
    studentToUpdate = Student.objects.get(id=student_pk)

    # does not affect GWA or total_grade
    if registration.subject.subject_offered.units != 0:
        weighted_grade = registration.subject.subject_offered.units * registration.grade
        print('weighted_grade = ' + str(weighted_grade))

        if old_completion == 'INCOMPLETE' and registration.completion != 'INCOMPLETE':
            studentToUpdate.completed_units += registration.subject.subject_offered.units
            studentToUpdate.total_grade += weighted_grade
        elif old_completion != 'INCOMPLETE' and registration.completion == 'INCOMPLETE':
            studentToUpdate.completed_units -= registration.subject.subject_offered.units
            studentToUpdate.total_grade -= old_weighted_grade
        else: # not INC to not INC
            studentToUpdate.total_grade -= old_weighted_grade
            studentToUpdate.total_grade += weighted_grade

        print('total grade = ' + str(studentToUpdate.total_grade))
        if studentToUpdate.completed_units != 0:
            studentToUpdate.gwa = (studentToUpdate.total_grade)/studentToUpdate.completed_units
        else:
            studentToUpdate.gwa = 0

        studentToUpdate.save(update_fields=['completed_units', 'gwa', 'total_grade'])

    registration.save(update_fields=['grade', 'completion'])
    
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subject_grades(request):
    context ={}

    user_id = request.user.id
    context['profile'] = UserProfile.objects.filter(user=user_id) 
    context['users'] = User.objects.exclude(id=user_id)
    context['userprofiles'] = UserProfile.objects.exclude(user=user_id)

    return render(request, "edit_subject_grades.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def advisor_view(request):
    context ={}

    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    profile = UserProfile.objects.get(user=user_id) 

    if 'last_name' not in request.POST:
        context['students'] = Student.objects.filter(advisor=profile.id).order_by('last_name')
        context['search'] = ''
    else:
        search = request.POST.get('last_name')
        context['search'] = search
        print(search)
        context['students'] = Student.objects.filter(advisor=profile.id, last_name__contains=search).order_by('last_name')
    

    return render(request, "advisor.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def report_select(request):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    
    if 'title' not in request.POST:
        context['terms'] = Term.objects.all()
        context['search'] = ''
    else:
        search = request.POST.get('title')
        context['search'] = search
        print(search)
        context['terms'] = Term.objects.filter(title__contains=search)

    return render(request, "reports.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def render_report(request, term_id):
    context = {}
    repeats = []

    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    
    context['term'] = Term.objects.get(id=term_id)
    context['students'] = Student.objects.filter(first_enrollment=term_id)

    students = context['students']
    highlight = {}
    for s in students:
        most_repeats = 0
        registrations = Registration.objects.filter(student=s).values_list("subject__subject_offered", flat=True)
        print(registrations)
        count = Counter(registrations)
        most_frequent = count.most_common(1)
        print("The most frequent element in the list is:", most_frequent)
        for item in most_frequent:
            most_repeats = item[1]
        if most_repeats >= 3:
            repeats.append(s.id)           

    print(repeats)
    context['repeats'] = repeats
    return render(request, "render_report.html", context)


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff_dashboard(request):

    context ={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['x'] = UserProfile.objects.get(user=user_id)

    return render(request, "dashboard.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enrollment(request):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    currentTerm = Term.objects.get(current_term=1)
    context['term'] = currentTerm

    if 'class_code' not in request.POST:
        class_code_filter = ''
    else:
        class_code_filter = request.POST.get('class_code')

    context['class_code_filter'] = class_code_filter

    # all subjects of current term 
    if 'name' not in request.POST:
        context['subjects'] = Subject.objects.filter(term=currentTerm.id, subject_offered__class_code__contains=class_code_filter)
        context['search'] = ''
    else:
        search = request.POST.get('name')
        subject_offerings = OfferedSubject.objects.filter(subject_name__contains=search)
        context['subjects'] = Subject.objects.filter(term=currentTerm.id, subject_offered__in=subject_offerings, subject_offered__class_code__contains=class_code_filter)
        context['search'] = search

    return render(request, "enrollment.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_course_students(request, course_id):
    context={}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['course_id'] = course_id

    context['students'] = Student.objects.filter(enrollment='ENROLLED')
    context['programs'] = ["BSCS","BSBC","BSAP"]

    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(enrollment='ENROLLED', last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(enrollment='ENROLLED', last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(enrollment='ENROLLED', program='BS COMPUTER SCIENCE', last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(enrollment='ENROLLED', program='BS BIOCHEMISTRY', last_name__contains=last_name_filter, student_number__contains=student_number_filter)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(enrollment='ENROLLED', program='BS APPLIED PHYSICS', last_name__contains=last_name_filter, student_number__contains=student_number_filter)
    
    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter

    context['registrations'] = Registration.objects.filter(subject=course_id)

    return render(request, "add_course_students.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_enrollment(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_id = request.POST.get('student_id')

        enrolled = request.POST.get('enrolled')
        print(enrolled)

        reg_student = Student.objects.get(id=student_id)
        reg_course = Subject.objects.get(id=course_id)

        if enrolled == 'true':
            # enroll student
            reg_course.enrolled += 1
            registration = Registration.objects.create(
                student=reg_student,
                subject=reg_course,
                completion='INCOMPLETE',
                grade=0,
            )
            registration.save()
        else:
            # unenroll student
            reg_course.enrolled -= 1
            registration = Registration.objects.get(student=reg_student, subject=reg_course)
            old_weighted_grade = registration.subject.subject_offered.units * registration.grade
            if registration.completion != 'INCOMPLETE':
                reg_student.completed_units -= reg_course.subject_offered.units
                reg_student.total_grade -= old_weighted_grade
                if reg_student.completed_units != 0:
                    reg_student.gwa = (reg_student.total_grade)/reg_student.completed_units
                else:
                    reg_student.gwa = 0
            reg_student.save(update_fields=['completed_units', 'total_grade'])
            registration.delete()

    reg_course.save(update_fields=['enrolled'])
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_advisor(request, student_id):
    new_advisor_id = request.POST.get('advisor')
    new_advisor = UserProfile.objects.get(id=new_advisor_id)
    print(new_advisor)

    student = Student.objects.get(id=student_id)
    
    student.advisor = new_advisor
    student.save(update_fields=['advisor'])
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adviser_assignments(request):
    response = redirect('/advisor_assignments')
    return response

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def advisor_assignments(request):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role

    userprofile = UserProfile.objects.get(user=user_id)
    
    # students who are not graduated - ongoing 
    # filter by course and first enrollment
    # can search by last name 

    if 'student_number' not in request.POST:
        student_number_filter = ''
    else:
        student_number_filter = request.POST.get('student_number')

    if 'last_name' not in request.POST:
        last_name_filter = ''
    else:
        last_name_filter = request.POST.get('last_name')

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
        context['students'] = Student.objects.filter(graduate='ONGOING', last_name__contains=last_name_filter, student_number__contains=student_number_filter).exclude(id=0)
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter
        if program_filter == 'None':
            context['students'] = Student.objects.filter(graduate='ONGOING', last_name__contains=last_name_filter, student_number__contains=student_number_filter).exclude(id=0)
        elif program_filter == 'BSCS':
            context['students'] = Student.objects.filter(graduate='ONGOING', program='BS COMPUTER SCIENCE', last_name__contains=last_name_filter, student_number__contains=student_number_filter).exclude(id=0)
        elif program_filter == 'BSBC':
            context['students'] = Student.objects.filter(graduate='ONGOING', program='BS BIOCHEMISTRY', last_name__contains=last_name_filter, student_number__contains=student_number_filter).exclude(id=0)
        elif program_filter == 'BSAP':
            context['students'] = Student.objects.filter(graduate='ONGOING', program='BS APPLIED PHYSICS', last_name__contains=last_name_filter, student_number__contains=student_number_filter).exclude(id=0)
    
    context['last_name_filter'] = last_name_filter
    context['student_number_filter'] = student_number_filter

    context['programs'] = ["BSCS","BSBC","BSAP"]
    context['profile'] = userprofile
    context['advisors'] = UserProfile.objects.filter(role__in = ('PROGRAM ADVISOR', 'THESIS ADVISOR'))
    print(context['advisors'])

    return render(request, "adviser_assignments.html", context)


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff_grades(request):
    response = redirect('/courses/')
    return response

    context ={}

    user_id = request.user.id
    context['students'] = Student.objects.all()
    context['registrations'] = Registration.objects.all()
    context['subjects'] = Subject.objects.all()
    context['grade_choices'] = [0, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 5]

    return render(request, "staff_grades.html", context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_course(request, course_id):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role
    context['subject'] = Subject.objects.get(id=course_id)
    context['registrations'] = Registration.objects.filter(subject=course_id).order_by('student__last_name')
    context['grade_choices'] = [0, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 4, 5]

    return render(request, 'view_course.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_student(request, student_id):
    context={}
    relevant_term_ids = set()

    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role

    context['student'] = Student.objects.get(id=student_id)

    # all student's registrations
    context['registrations'] = Registration.objects.filter(student=student_id)
    for r in context['registrations']:
        relevant_term_ids.add(r.subject.term.id)

    #terms in which student has a registration
    context['terms'] = Term.objects.filter(id__in=relevant_term_ids)

    return render(request, 'view_student.html', context)

@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def curriculum_guide(request):
    context = {}
    user_id = request.user.id
    context['user_role'] = UserProfile.objects.get(user=user_id).role

    if 'program' not in request.POST:
        context['program_filter'] = 'None'
    else:
        program_filter = request.POST.get('program')
        context['program_filter'] = program_filter

    if 'year' not in request.POST:
        context['year_filter'] = 'None'
    else:
        year_filter = request.POST.get('year')
        context['year_filter'] = year_filter

    context['programs'] = ["BSCS","BSBC","BSAP"]
    context['years'] = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

    return render(request, 'curriculum_guide.html', context)