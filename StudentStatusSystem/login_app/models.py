from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Choices

class Sex(models.TextChoices):
    M = "M", 'Male'
    F = "F", 'Female'

class DegreeProgram(models.TextChoices):
    ComputerScience = "BS COMPUTER SCIENCE", 'BS Computer Science'
    Biochemistry = "BS BIOCHEMISTRY", 'BS Biochemistry'
    AppliedPhysics = "BS APPLIED PHYSICS", 'BS Applied Physics'

class Completion(models.TextChoices):
    Passed = "PASSED", 'Passed'
    Incomplete = "INCOMPLETE", 'Incomplete'
    Failed = "FAILED", 'Failed'
    Conditional = "CONDITIONAL", 'Conditional'

GRADE = [
    (1, '1.0'),
    (1.25, '1.25'),
    (1.5, '1.5'),
    (1.75, '1.75'),
    (2.0, '2.0'),
    (2.25, '2.25'),
    (2.5, '2.5'),
    (2.75, '2.75'),
    (3, '3.0'),
    (4, '4.0'),
    (5, '5.0'),
    (0, 'INC')
]

# Models (Tables)

class Term(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    current_term = models.BooleanField()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STAFF = "STAFF", 'Staff'
        TADVISOR = "THESIS ADVISOR", 'Thesis Advisor'
        PADVISOR = "PROGRAM ADVISOR", 'Program Advisor'
        NONADVISOR = "FACULTY", 'Faculty'

    role = models.CharField(max_length=50, choices=Role.choices)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)
    sex = models.CharField(max_length=200, choices=Sex.choices)
    department = models.CharField(max_length=200)
    birthday = models.DateField(default=timezone.now)
    contact_number = models.CharField(max_length=15)
    staff_id = models.CharField(max_length=9)


class Student(models.Model):
    student_number = models.CharField(max_length=10)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200)

    email = models.EmailField(max_length=50)
    sex = models.CharField(max_length=200, choices=Sex.choices)
    contact_number = models.CharField(max_length=200)
    birthday = models.DateField(default=timezone.now)
    
    class Grad_status(models.TextChoices):
        GRADUATED = "GRADUATED", 'Graduated'
        ONGOING = "ONGOING", 'Ongoing'

    class Enrollment(models.TextChoices):
        ENROLLED = "ENROLLED", 'Registered'
        UNENROLLED = "UNENROLLED", 'Not Registered'
        LEAVEOFABSENCE = "LEAVE OF ABSENCE", 'Leave of Absence'

    years = models.IntegerField(default=0) # years since first enrollment to program
    completed_units = models.IntegerField(default=0) # add for each Registration that is completed 
    required_units = models.IntegerField(default=158) # based on program enrolled 
    total_grade = models.FloatField(default=0) # total weighted grade = sum of grade x unit of subject
    gwa = models.FloatField(default=0)

    graduate = models.CharField(max_length=200, choices=Grad_status.choices)
    program = models.CharField(max_length=200, choices=DegreeProgram.choices)
    enrollment = models.CharField(max_length=200, choices=Enrollment.choices) # current enrollment status 

    first_enrollment = models.ForeignKey(Term, on_delete=models.SET_NULL, blank=True, null=True,  related_name='first_term') # maybe replace the on_delete
    last_enrollment = models.ForeignKey(Term, on_delete=models.SET_NULL, blank=True, null=True, related_name='recent_term') # if enrolled
    advisor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True)

# List of all subjects offered for keeping track of what subjects can be added for the term
class OfferedSubject(models.Model):
    subject_name = models.CharField(max_length=200)
    subject_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    units = models.IntegerField(default=3) 
    class_code = models.CharField(max_length=25)
    # non graded classes (PE) will have 0 units

    lecture = models.BooleanField(default=True)
    lab = models.BooleanField(default=False)

# List of available for enrollment - per term 
class Subject(models.Model):
    term = models.ForeignKey(Term, on_delete=models.PROTECT)
    subject_offered = models.ForeignKey(OfferedSubject, on_delete=models.PROTECT)
    
    professor = models.ForeignKey(UserProfile, on_delete=models.PROTECT, blank=True, null=True)
    section = models.CharField(max_length=200)

    slots = models.IntegerField(default=25)
    enrolled = models.IntegerField(default=0)

# Enrollment of a student to a subject
class Registration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT) 

    # determined based on grade
    completion = models.CharField(max_length=200, choices=Completion.choices, blank=True)
    grade = models.FloatField(choices=GRADE, default=0)
    
