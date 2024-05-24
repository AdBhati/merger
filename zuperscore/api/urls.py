from django.urls import path

# Create your urls here.

from zuperscore.api.views.authentication import (
    SignInEndpoint,
    SignUpEndpoint,
    SignOutEndpoint,
    RefreshAccessToken,
)
from .views.library import FileAssetEndpoint
from zuperscore.api.views.people import (
    PeopleView,
    TargetTestDateViewSet,
    UserViewSet,
    UserCustomFieldViewSet,
    SchoolViewSet,
    CommentViewSet,
    AllocateManagerViewSet,
    AllocateCounselorViewSet,
    FilterPeopleViewSet,
)

from zuperscore.api.views.assessments import (
    AssessmentViewSet,
    ChildNodesEndpoint,
    GenerateQuestionForSection,
    OneLevelChildNodesEndpoint,
    OptionViewSet,
    QuestionNodeViewset,
    QuestionViewSet,
    SearchQuestionEndpoint,
    SectionViewSet,
    SectionQuestionViewSet,
    UserAssessmentSessionViewSet,
    GenerateAssessmentSessionView,
    RenderAssessmentSessionView,
    UserAssessmentSessionSectionQuestionsView,
    UserAllocatedAssessmentsEndpoint,
    UserAllocatedAssessmentsDashboardEndpoint,
    UserAllocatedAssessmentCheckEndpoint,
    UserAllocatedAssessmentMistakesEndpoint,
    UserAssessmentSessionByDateEndpoint,
    UserAssessmentsEndpoint,
    ComputeScaledScoreEndpoint,
    UserAssessmentAttemptEndpoint,
    UserAssessmentAttemptViewSet,
    AllAssessmentSessionEndpoint,
    CreateUserAttemptBulk,
    CreateUserAttemptBulkAsync,
    MistakeAnalyserEndpoint,
    AssessmentSessionCSCDownloadEndpoint,
    StudentMyPerformanceAnalyticsEndpoint,
    UserSessionResultCSVEndpoint,
    GroupViewSet,
    PracticeSetViewSet,
    GroupUserViewSet,
    PracticeSetAssessmentViewSet,
    AssessmentTagsViewSet,
    TestAllocationLoggerViewSet,
    TestAllocationPracticeSetAssessmentViewSet,
    TestAllocationGroupUserViewSet,
    DownloadUserAssessment,
    DownloadAssessmentAnalysis,
    WeeklyProgressViewSet,
    GenerateBulkAssessmentSessionView,
    TestIRTQuestionViewSet,
)

from zuperscore.api.views.subjects import (
    AllSubjectRoots,
    CreateSubjectTree,
    SubjectNodeActions,
    SubjectNodeViewset,
    SubjectTreeByNodeView,
)
from zuperscore.api.views.subjects import (
    ExamViewSet,
    SubjectViewSet,
    ModuleViewSet,
    SessionPlanViewSet,
    StudentSessionViewSet,
    StudentModuleViewSet,
    StudentDomainViewSet,
    StudentTopicViewSet,
    StudentSubTopicViewSet,
    AssignmentViewSet,
    AssignmentQuestionViewSet,
    StudentAssignmentViewSet,
    Create_custom_Link,
    HomeAssignment,
    ListModuleViewSet,
    MoleculeViewSet,
    MotherSessionMoleculeViewSet,
    MegaDomainViewSet,
    DomainViewSet,
    TopicViewSet,
    SubTopicViewSet,
    ReasonForErrorViewSet,
)
from zuperscore.api.views.library import (
    SettingsViewSet,
    TimeZoneViewSet,
    TimeAnalyticsViewSet,
)


from zuperscore.api.views.conduct import (
    AllotGroupClassBaseViewSet,
    AppointmentAgendaViewSet,
    AppointmentAssignemntViewset,
    AssignCategoryViewSet,
    AssignGroupClassesBaseViewSet,
    CalculateStudentAvailabilityViewSet,
    CheckStudentGroupBaseViewSet,
    CompletedClassViewSet,
    CpeaBaseViewSet,
    CpeaOverRideViewSet,
    CpeaReportBaseViewSet,
    GroupClassesBaseViewSet,
    LastClassAgendaViewSet,
    LastClassViewSet,
    SsoStudentBaseViewSet,
    StudentCategoryViewSet,
    AppointmentViewSet,
    StudentAvailabilityViewSet,
    StudentDashBoardViewSet,
    StudentGroupEventBaseViewSet,
    StudentRelatedTeacherViewSet,
    # StudentJourneyViewSet,
    TeacherAppointmentFeedbackViewSet,
    TeacherAppointmentViewSet,
    TutorDashBoradViewSet,
    # UserRoleProfileViewSet,
    # TeacherAppointmentFeedbackViewSet,
    ReportClassesViewSet,
    UnattendedClassesViewSet,
    UnattendedCounterClassesViewSet,
    UsersTeamViewSet,
)

from zuperscore.api.views.library import SettingsViewSet

urlpatterns = [
    path("auth/refresh-token/", RefreshAccessToken.as_view()),
    path("sign-in/", SignInEndpoint.as_view()),
    path("enroll-user/", SignUpEndpoint.as_view()),
    path("sign-out/", SignOutEndpoint.as_view()),
    path("people-view/", PeopleView.as_view()),
    path("filter-people-view/", FilterPeopleViewSet.as_view()),
    # path("users/<int:pk>/", PeopleView.as_view()),
    path("schools/", SchoolViewSet.as_view({"get": "list", "post": "create"})),
    path("users-without-pagination/", UserCustomFieldViewSet.as_view({"get": "list"})),
    path("assessments/", AssessmentViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "assessments/irt/<int:pk>/",
        TestIRTQuestionViewSet.as_view({"get": "get", "post": "post"}),
    ),
    path(
        "assessments/<int:pk>/",
        AssessmentViewSet.as_view(
            {"get": "get_assessment", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "assessments/<int:pk>/sections/",
        AssessmentViewSet.as_view({"get": "with_sections", "post": "create_section"}),
    ),
    path(
        "assessments/<int:pk>/users/",
        AssessmentViewSet.as_view({"get": "user_assessments_allots"}),
    ),
    path(
        "assessments/<int:pk>/users/list/",
        AssessmentViewSet.as_view({"get": "user_list"}),
    ),
    # change this to cancelled state
    path(
        "assessments/<int:pk>/users/<int:user_id>/",
        AssessmentViewSet.as_view({"get": "user_assessment_bool"}),
    ),
    ## Assessment Sections
    path("sections/", SectionViewSet.as_view({"get": "list"})),
    path(
        "sections/<int:pk>/",
        SectionViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "sections/<int:pk>/questions/",
        SectionViewSet.as_view({"get": "with_questions", "post": "create_question"}),
    ),
    ## Assessment Questions
    path("questions/", QuestionViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "questions/<int:pk>/",
        QuestionViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path("options/", OptionViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "options/<int:pk>/",
        OptionViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "sections/questions/",
        SectionQuestionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "sections/questions/<int:pk>/",
        SectionQuestionViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "subjects/tree/",
        SubjectNodeActions.as_view(),
        name="forms",
    ),
    path(
        "subjects/tree/<int:node_id>/",
        SubjectTreeByNodeView.as_view(),
        name="tree-node",
    ),
    path(
        "subjects/tree/create/",
        CreateSubjectTree.as_view(),
        name="tree-node",
    ),
    path(
        "subjects-nodes/<int:pk>/",
        SubjectNodeViewset.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path("subjects/", AllSubjectRoots.as_view(), name="resources"),
    path("files/", FileAssetEndpoint.as_view(), name="files"),
    #! Colleges
    #! QB
    #! Subjects
    # tags and subjects and questions
    path(
        "questions/<int:question_id>/nodes/",
        QuestionNodeViewset.as_view({"post": "create"}),
        name="questions-tags",
    ),
    path(
        "questions/<int:question_id>/nodes/<int:node_id>/",
        QuestionNodeViewset.as_view({"delete": "destroy", "put": "partial_update"}),
        name="questions-tags",
    ),
    path(
        "subnodes/<int:node_id>/",
        QuestionNodeViewset.as_view({"get": "question_list"}),
        name="questions-tags",
    ),
    path(
        "generate-for-sections/",
        GenerateQuestionForSection.as_view(),
        name="generate-questions-sections",
    ),
    path(
        "search-questions/",
        SearchQuestionEndpoint.as_view(),
        name="search-questions-sections",
    ),
    path("child-nodes/<int:pk>/", ChildNodesEndpoint.as_view(), name="child-nodes"),
    path(
        "onelevel-childnodes/<int:pk>/",
        OneLevelChildNodesEndpoint.as_view(),
        name="onelevel-nodes",
    ),
    path(
        "users/<int:pk>/",
        UserViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
        name="users",
    ),
    path(
        "users/<int:pk>/allocate-managers/",
        AllocateManagerViewSet.as_view({"put": "partial_update"}),
    ),
    path(
        "users/tutors-list",
        UserViewSet.as_view({"get": "get_subject_tutors"}),
    ),
    path(
        "users/<int:pk>/setpassword/",
        UserViewSet.as_view({"post": "set_password"}),
        name="users",
    ),
    path("users/sso-students", UserViewSet.as_view({"get": "get_sso_students"})),
    path(
        "users/assessments-sessions/",
        UserAssessmentSessionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "users/download-assessment-sessions/",
        DownloadUserAssessment.as_view({"get": "list"}),
    ),
    path(
        "users/assessments-sessions/<int:pk>/",
        UserAssessmentSessionViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "users/assessments-sessions/generate/",
        GenerateAssessmentSessionView.as_view(),
        name="generate-assessment-session",
    ),
    path(
        "users/<int:pk>/generate-bulk-sessions/",
        GenerateBulkAssessmentSessionView.as_view(),
    ),
    path(
        "users/assessments-sessions/render/",
        RenderAssessmentSessionView.as_view(),
        name="generate-assessment-session",
    ),
    path("questions-by-ids/", QuestionViewSet.as_view({"post": "questions_by_ids"})),
    path(
        "users/assessments-sessions/sections/",
        UserAssessmentSessionSectionQuestionsView.as_view(),
        name="generate-assessment-session",
    ),
    path("users/<int:pk>/assessments/", UserAllocatedAssessmentsEndpoint.as_view()),
    path(
        "users/assessments/dashboard/",
        UserAllocatedAssessmentsDashboardEndpoint.as_view(),
    ),
    path("users/assessments/check/", UserAllocatedAssessmentCheckEndpoint.as_view()),
    path(
        "users/assessments/mistakeanalysis/",
        UserAllocatedAssessmentMistakesEndpoint.as_view(),
    ),
    path("users/assessments/bydate/", UserAssessmentSessionByDateEndpoint.as_view()),
    path("users/assessments/", UserAssessmentsEndpoint.as_view()),
    # exams, subjects, mega-domain, domain, topic, sub-topic, reason-for-error
    path(
        "tags/exam/",
        ExamViewSet.as_view(
            {
                "get": "list",
            }
        ),
    ),
    path(
        "tags/subject/",
        SubjectViewSet.as_view(
            {
                "get": "list",
            }
        ),
    ),
    path(
        "tags/subject/<int:pk>/",
        SubjectViewSet.as_view(
            {
                "get": "get_subject",
            }
        ),
    ),
    path(
        "tags/mega-domain/",
        MegaDomainViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "tags/mega-domain/<int:pk>/",
        MegaDomainViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path("tags/domain/", DomainViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "tags/domain/<int:pk>/",
        DomainViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path("tags/topic/", TopicViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "tags/topic/<int:pk>/",
        TopicViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path("tags/sub-topic/", SubTopicViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "tags/sub-topic/<int:pk>/",
        SubTopicViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path(
        "tags/sub-topicId/<int:topic_id>/",
        SubTopicViewSet.as_view({"get": "get_by_topicId"}),
    ),
    path(
        "tags/session-plan/",
        SessionPlanViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "tags/session-plan/<int:pk>/",
        SessionPlanViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path(
        "tags/session-plan/tree/",
        SessionPlanViewSet.as_view({"get": "get_session_tree"}),
    ),
    path(
        "tags/session-plan/tree/<int:pk>/",
        SessionPlanViewSet.as_view({"get": "get_session_tree_by_id"}),
    ),
    path("tags/reason-for-error/", ReasonForErrorViewSet.as_view({"get": "list"})),
    path(
        "tags/reason-for-error/<int:pk>/",
        ReasonForErrorViewSet.as_view({"get": "retrieve"}),
    ),
    path(
        "compute-scaled-score/",
        ComputeScaledScoreEndpoint.as_view(),
        name="compute-scaled-score",
    ),
    path(
        "users/sessions/<int:pk>/attempts/",
        UserAssessmentAttemptEndpoint.as_view({"get": "list", "post": "create"}),
        name="user-assessment-attempts",
    ),
    path(
        "users/assessments-attempts/",
        UserAssessmentAttemptViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "users/assessments-attempts/<int:pk>/",
        UserAssessmentAttemptViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    ## migrations
    path(
        "all-sessions/",
        AllAssessmentSessionEndpoint.as_view(),
        name="assessment-migration",
    ),
    path("create-bulk/", CreateUserAttemptBulk.as_view(), name="assessment-migration"),
    path(
        "create-bulk-async/",
        CreateUserAttemptBulkAsync.as_view(),
        name="assessment-migration",
    ),
    path(
        "mistakes-analyser/", MistakeAnalyserEndpoint.as_view(), name="mistake-analyzer"
    ),
    ## assessment sessions csv download
    path(
        "sessions-csv-download/",
        AssessmentSessionCSCDownloadEndpoint.as_view(),
        name="assessment-session-csv-download",
    ),
    path(
        "student-my-performance-analytics/",
        StudentMyPerformanceAnalyticsEndpoint.as_view(),
        name="student-performance-analysis",
    ),
    path(
        "session-csv-result-download/",
        UserSessionResultCSVEndpoint.as_view(),
        name="session-csv-result-download",
    ),
    path("settings/", SettingsViewSet.as_view({"get": "list"}), name="settings"),
    # group and set
    path("groups/", GroupViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "groups/<int:pk>/",
        GroupViewSet.as_view(
            {
                "get": "get_group_users",
                "put": "update_group_users",
                "delete": "delete_group",
            }
        ),
    ),
    path("group-user/", GroupUserViewSet.as_view({"post": "create_group_users"})),
    path(
        "practice-sets/", PracticeSetViewSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "practice-sets/<int:pk>/",
        PracticeSetViewSet.as_view(
            {
                "get": "get_set_assessment",
                "put": "update_set_assessments",
                "delete": "delete_set",
            }
        ),
    ),
    path(
        "practice-set-assessment/",
        PracticeSetAssessmentViewSet.as_view({"post": "create_set_assessments"}),
    ),
    # assessment tag
    path("assessment-tags/", AssessmentTagsViewSet.as_view({"get": "list"})),
    # test allocation logger
    path(
        "test-allocation/",
        TestAllocationLoggerViewSet.as_view(
            {"get": "list", "post": "create_test_logger"}
        ),
    ),
    path(
        "test-allocation/<int:pk>/",
        TestAllocationLoggerViewSet.as_view(
            {"get": "retrieve", "put": "update_logger", "delete": "destroy"}
        ),
    ),
    # download assessment csv
    path(
        "download-assessment-analysis/",
        DownloadAssessmentAnalysis.as_view({"get": "download_assessment_analysis"}),
    ),
    # weekly progress
    path(
        "weekly-progress/<int:pk>",
        WeeklyProgressViewSet.as_view(
            {
                "get": "list",
                "post": "create_weekly_progress",
                "put": "update_weekly_progress",
            }
        ),
    ),
    # conduct url's
    # student session plan
    path("conduct/students/category/", StudentCategoryViewSet.as_view({"get": "list"})),
    path(
        "conduct/students/session-plan/",
        StudentSessionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "conduct/students/session-plan/<int:pk>/",
        StudentSessionViewSet.as_view({"get": "get_by_student_id"}),
    ),
    path(
        "conduct/students/session-plan/modules/",
        StudentModuleViewSet.as_view({"get": "list"}),
    ),
    path(
        "conduct/students/session-plan/domains/",
        StudentDomainViewSet.as_view({"get": "list"}),
    ),
    path(
        "conduct/students/session-plan/topics/",
        StudentTopicViewSet.as_view({"get": "list"}),
    ),
    path(
        "conduct/students/session-plan/sub-topics/",
        StudentSubTopicViewSet.as_view(
            {"get": "list", "post": "add_student_sub_topic"}
        ),
    ),
    path(
        "conduct/students/session-plan/sub-topics/<int:pk>/",
        StudentSubTopicViewSet.as_view({"put": "update"}),
    ),
    # assignments
    path("assignments/", AssignmentViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "assignments/<int:pk>/",
        AssignmentViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    path(
        "assignments/completed-all/<int:user_id>/",
        AssignmentViewSet.as_view({"get": "get_completed_assignments"}),
    ),
    path(
        "assignments/questions/",
        AssignmentQuestionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "assignments/questions/<int:pk>/",
        AssignmentQuestionViewSet.as_view(
            {"get": "get_by_id", "put": "update", "delete": "delete"}
        ),
    ),
    path(
        "assignments/student-assignments/<int:pk>/",
        StudentAssignmentViewSet.as_view({"get": "get_by_student_id"}),
    ),
    # class appointments
    path(
        "conduct/appointments/teachers-appointments/",
        TeacherAppointmentViewSet.as_view({"get": "get_teachers_appointments"}),
    ),
    path(
        "conduct/appointments/student-molecules-assignment/<int:student_id>/<int:appointment_id>/",
        AppointmentAssignemntViewset.as_view({"get": "get_student_class_assignment"}),
    ),
    path(
        "conduct/appointments/student-molecules-home-assignment/<int:student_id>/<int:appointment_id>/",
        AppointmentAssignemntViewset.as_view({"get": "get_student_home_assignment"}),
    ),
    path(
        "conduct/appointments/student-assignment-question/<int:student_assignment_id>/",
        AppointmentAssignemntViewset.as_view(
            {"get": "get_student_assignment_question"}
        ),
    ),
    path(
        "conduct/appointments/validate-answers/<int:student_id>/",
        AppointmentAssignemntViewset.as_view({"post": "correct_answer_for_questions"}),
    ),
    path(
        "conduct/appointments/update-student-assignment-question/",
        AppointmentAssignemntViewset.as_view(
            {"post": "update_student_assignment_question"}
        ),
    ),
    path(
        "conduct/appointments/other-covered-agenda/<int:student_id>",
        AppointmentAgendaViewSet.as_view({"get": "get_other_covered_agenda"}),
    ),
    path(
        "conduct/appointments/appointments-molecule/<int:student_id>/<int:tutor_id>",
        AppointmentAgendaViewSet.as_view({"get": "get_appointment_molecule"}),
    ),
    path(
        "conduct/appointments/",
        AppointmentViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "conduct/appointments/<int:pk>/",
        AppointmentViewSet.as_view(
            {"get": "get_appointment", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    # path("conduct/appointments/create-zoom-session/", AppointmentViewSet.as_view({"post": "create_zoom_session"})),
    path(
        "conduct/appointments/admin-appointments/",
        AppointmentViewSet.as_view({"get": "get_all_appointments"}), #admin
    ),
    path(
        "conduct/appointments/update-appointments-molecule/<int:appointment_id>",
        AppointmentViewSet.as_view(
            {"put": "updateMolecule"}
        ),  # implemented but not used ( need to restrict for admin )
    ),
    path(
        "conduct/appointments/day-scheduler-resources/",
        AppointmentViewSet.as_view(
            {"get": "get_dayScheduler_resources"}
        ),  # not used (need to restrict for admin)
    ),
    path(
        "conduct/appointments/view-appointments/",
        AppointmentViewSet.as_view(
            {"get": "get_appointments"}
        ),  # not used (need to restrict for admin)
    ),
    path(
        "conduct/appointments/view-available-appointments/<str:pk>/",  # admin, tutor, ops_manager
        AppointmentViewSet.as_view({"get": "get_available_appointments"}),
    ),
    path(
        "conduct/appointments/child/<int:id>/",
        AppointmentViewSet.as_view({"get": "get_child"}),  # admin, tutor, ops_manager
    ),
    path(
        "conduct/appointments/get_student_teachers/<int:pk>/",
        AppointmentViewSet.as_view({"get": "get_student_teachers"}),  # students
    ),
    path(
        "conduct/appointments/slot-booking/<str:type>/",
        AppointmentViewSet.as_view({"post": "slot_booking"}),  # admin, student
    ),
    path(
        "conduct/appointments/get-comming-classes/<int:invitee_id>/",
        AppointmentViewSet.as_view({"get": "get_coming_classes"}),  # admin, student
    ),
    path(
        "conduct/appointments/student-related-teacher/",
        StudentRelatedTeacherViewSet.as_view({"get": "students_related_teacher"}),
    ),
    path(
        "conduct/appointments/get-last-classes/<int:student_id>/",
        LastClassViewSet.as_view({"get": "get_last_classes"}),
    ),
    path(
        "conduct/appointments/get-completed-classes/<int:student_id>/",
        CompletedClassViewSet.as_view({"get": "get_completed_classes"}),
    ),
    path(
        "conduct/appointments/get-all-users/",
        AppointmentViewSet.as_view({"get": "get_all_users"}),  # not used
    ),
    path(
        "molecule/createAppMolecule/",
        AppointmentAgendaViewSet.as_view({"post": "createAppointmentMolecules"}),
    ),
    path(
        "molecule/update-appointment-molecule-feedback/",
        AppointmentAgendaViewSet.as_view(
            {"post": "update_appointment_molecules_and_feedback"}
        ),
    ),
    path(
        "conduct/appointments/create/",
        Create_custom_Link.as_view({"get": "get_custom_link_data"}),
    ),
    path(
        "conduct/appointments/last-classes-agenda/",
        LastClassAgendaViewSet.as_view({"get": "get_last_classes_agenda"}),
    ),
    path("home/assignment", HomeAssignment.as_view({"get": "get_homeassignment"})),
    path(
        "module/all_list", ListModuleViewSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "module/all_list/<int:pk>/",
        ListModuleViewSet.as_view({"get": "get_by_id", "put": "update"}),
    ),
    # MoleculeViewSet
    path("molecules/", MoleculeViewSet.as_view({"get": "list", "post": "create"})),
    path("molecules/<int:pk>/", MoleculeViewSet.as_view({"get": "get_by_id", "put": "update"})),
    path("molecules/delete_subtopic_molecules/<int:molecule_id>/<int:subtopic_id>", MoleculeViewSet.as_view({"delete": "delete_subtopic_molecules"})),
    
    path("mother_session_molecules/", MotherSessionMoleculeViewSet.as_view({"get": "list", "post": "create"})),

    path("student-availability/",StudentAvailabilityViewSet.as_view({"get": "list"})),
    path("student-availability/<int:pk>",StudentAvailabilityViewSet.as_view({"get": "get_by_id","delete":"destroy","post":"create"})),
    path("calculate-availability/<int:student_id>",CalculateStudentAvailabilityViewSet.as_view({"get": "calculate_availability"})),
    path("assign-category/<int:student_id>",AssignCategoryViewSet.as_view({"post": "assign_category"})),
    path("student-team/",UsersTeamViewSet.as_view({"post": "create_student_team","get": "user_list"})),
    path("remove-student-team/<int:student_id>/<int:user_id>/",UsersTeamViewSet.as_view({"delete":"delete_student_team"})),
    path("student-team/<int:user_id>",UsersTeamViewSet.as_view({"get": "get_user_teams"})),
    path("student-availability/update/<int:student_id>",StudentAvailabilityViewSet.as_view({"put": "update_days"})),
    path("comment/create",CommentViewSet.as_view({"post":"create"})),
    path("comment/get-by-id/<int:user_id>",CommentViewSet.as_view({"get":"get_by_id"})),
    path("dashboard/tutor-dashboard/",TutorDashBoradViewSet.as_view({"get":"tutor_dashboard"})),
    path('tutor/appointment/feedback/<int:appointment_id>/', TeacherAppointmentFeedbackViewSet.as_view({"get":"list"})),
    path('student/dashboard/progress-bar/<int:student_id>/', StudentDashBoardViewSet.as_view({"get":"calculate_student_progress"})),
    path('date/target-test-date/', TargetTestDateViewSet.as_view({"get":"get_target_test_dates"})),
    path('conduct/cpea-assignment/<str:mega_domain>', CpeaBaseViewSet.as_view({"get":"get_cpea_assignment"})),
    path('conduct/cpea-assignment-report/<int:student_id>/<int:tutor_id>/', CpeaBaseViewSet.as_view({"post":"post_cpea_assignment_report"})),
    path('conduct/student-cpea-report/<int:student_id>/',CpeaBaseViewSet.as_view({"get":"get_student_cpea_report"})),
    path('conduct/student-cpea-report/<int:student_id>/<int:appointment_id>',CpeaReportBaseViewSet.as_view({"put":"update_student_cpea_report"})),
    path('conduct/reading-student-cpea-report/',CpeaReportBaseViewSet.as_view({"post":"create_reading_cpea_report"})),
    path('conduct/student-cpea-report/<int:student_id>/',CpeaReportBaseViewSet.as_view({"get":"get_student_cpea_report"})),



    path('conduct/student-cpea-questions/<str:mega_domain_name>',CpeaBaseViewSet.as_view({"get":"get_cpea_questions"})),
    path("conduct/appointments/day-scheduler-group-events/<int:student_id>", GroupClassesBaseViewSet.as_view({"get":"get_dayScheduler_group_events"})),
    path("conduct/appointments/group-class-events/<int:deptHead_id>/", AssignGroupClassesBaseViewSet.as_view({"post":"assign_group_classes"})),
    path("conduct/appointments/allot-group-class/", AllotGroupClassBaseViewSet.as_view({"post":"allot_group_classes"})),
    path("conduct/group-events/", StudentGroupEventBaseViewSet.as_view({"get":"get_student_group_events"})),
    path("conduct/student-class-stats/<int:student_id>", CheckStudentGroupBaseViewSet.as_view({"get":"check_student_group_assignment"})),
    path("conduct/list-grouped-students/<uuid:group_id>", SsoStudentBaseViewSet.as_view({"get":"get_sso_students_by_group_id"})),
    path("conduct/appointment-report/<int:appointment_id>", ReportClassesViewSet.as_view({"post":"create"})),
    # path("report/student-journey/<int:student_id>",StudentJourneyViewSet.as_view({"get":"create_student_journey"})),
    path(
        "timezone/user-timezone", TimeZoneViewSet.as_view({"post": "convert_time_zone"})
    ),
    path(
        "users/time-analytics/",
        TimeAnalyticsViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "users/time-analytics/<int:pk>/",
        TimeAnalyticsViewSet.as_view(
            {"get": "retrieve", "put": "partial_update", "delete": "destroy"}
        ),
    ),
    path("users/sso-managers", UserViewSet.as_view({"get": "get_all_sso_managers"})),
    # path("tutor-availablity/<int:tutor_id>/", TutorAvailabilityViewSet.as_view({"post": "post"})),
    # counselors
    path(
        "allocate-counselor/<int:pk>/",
        AllocateCounselorViewSet.as_view({"get": "get", "put": "partial_update"}),
    ),
    path(
        "allocate-counselor/<int:pk>/<int:user>/",
        AllocateCounselorViewSet.as_view({"delete": "delete"}),
    ),
    path("cpea/override/<int:student_id>/<str:mega_domains>", CpeaOverRideViewSet.as_view({"put": "cpea_override"})),  # added after merger
    path("conduct/unatteneded/classes/", UnattendedClassesViewSet.as_view({"get": "list"})),
    path("conduct/unatteneded/counters_classes/", UnattendedCounterClassesViewSet.as_view({"get": "counters_of_all_classes"}))

]
