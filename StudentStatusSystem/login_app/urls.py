from django.urls import path, include
from login_app import views
from loginsystem import settings

urlpatterns = [
    path("", views.render_login, name="render_login"),
    path("perform_login", views.perform_login, name="perform_login"),
    path("perform_logout", views.perform_logout, name="perform_logout"),

    path("delete_user/<int:id>/", views.delete_user, name="delete_user"),
    path("delete_term/<int:id>/", views.delete_term, name="delete_term"),
    path("delete_subject/<int:id>/", views.delete_subject, name="delete_subject"),
    path("create_term", views.create_term, name="create_term"),
    path("create_registration", views.create_registration, name="create_registration"),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('update_grade/<int:registration_id>/', views.update_grade, name='update_grade'),

    path('curriculum_guide', views.curriculum_guide, name="curriculum_guide"),

    # for general access
    path("dashboard/", views.landing_page, name="dashboard"),
    path("view_course/<int:course_id>/", views.view_course, name="course_view"),
    path("view_student/<int:student_id>/", views.view_student, name="student_view"),

    path("tables/", views.manage_tables, name="manage_tables"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("thesis_advisor_dashboard/", views.thesis_advisor_dashboard, name="thesis_advisor_dashboard"),
    path("program_advisor_dashboard/", views.program_advisor_dashboard, name="program_advisor_dashboard"),
    path("faculty_dashboard/", views.faculty_dashboard, name="faculty_dashboard"),
    path("advisor_view/", views.advisor_view, name="advisor_view"),

    path("reports/", views.report_select, name="reports"),
    path("reports/<int:term_id>/", views.render_report, name="reports table"),
    path("courses/", views.grades_course, name="courses"),

    path("reports/", views.report_select, name="reports"),
    path("reports/<int:term_id>/", views.render_report, name="reports table"),

    path("upload_csv/", views.grade_csv, name="upload_csv"),
    path("download_csv", views.download_template, name="download_csv"),

    #staff pages
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("registration", views.registration, name="registration"),
    path("enrollment", views.enrollment, name="enrollment"),
    path("enrollment/<int:course_id>/", views.add_course_students, name="add_course_students"),
    path("update_enrollment", views.update_enrollment, name="update_enrollment"),

    path("staff_grades", views.staff_grades, name="staff_grades"),
    path("advisor_assignments", views.advisor_assignments, name="advisor_assignments"),
    path("adviser_assignments", views.adviser_assignments, name="adviser_assignments"), #redirect
    path("update_advisor/<int:student_id>/", views.update_advisor, name='update_advisor'),
    path("manage_registration", views.manage_registration, name='manage_registration'),
    path("update_registration", views.update_registration, name='update_registration'),
    path("create_student", views.create_student, name="create_student"),
    path("manage_students", views.manage_student, name="manage_student"),
    path("delete_student/<int:student_id>/", views.delete_student, name="delete_student"),
    path("edit_student/<int:student_id>/", views.edit_student, name="edit_student"),
    path("graduation", views.graduation_select_term, name="graduation_select_term"),
    path("graduation/<int:term_id>/", views.manage_graduation, name="manage_graduation"),
    path("update_graduation", views.update_graduation_status, name="update_graduation_status"),
    path("update_graduation/<int:term_id>/", views.graduate_all, name="graduate_all"),

    #admin pages
    path("academic_terms", views.academic_term_page, name="academic_terms"),
    path("academic_terms/<int:term_id>/", views.view_term, name="view_term"),
    path("current_term/<int:term_id>/", views.set_current_term, name="set_current_term"),
    path("courses_offered", views.course_offerings, name="courses_offered"),
    path("create_user", views.create_user, name="create_user"),
    path('update_profile/<int:user_id>/', views.update_profile, name='update_profile'),
    path('update_password/<int:user_id>/', views.update_password, name='update_password'),
    path("create_subject/<int:term_id>/", views.create_subject, name="create_subject"),
    path("edit_course/<int:subject_id>/", views.edit_subject, name="edit_subject"),
    
    path("create_offering", views.create_offering, name="create_offering"),
    path("delete_offering/<int:offering_id>/", views.delete_offering, name='delete_offering'),
    path("edit_offering/<int:offering_id>/", views.edit_offering, name='edit_offering'),

    #thesis advisor pages
    path("grades_student/", views.grades_student, name="grades_student"),
    path("edit_student_grades/", views.edit_student_grades, name="edit_student_grades"),
    
    path("edit_subject_grades/", views.edit_subject_grades, name="edit_student_grades"),
    
    
]

