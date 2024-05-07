# Generated by Django 3.2.20 on 2023-10-30 07:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0087_alter_sessionplan_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sequence", models.IntegerField(default=0)),
                ("marks", models.IntegerField(default=0)),
                (
                    "type",
                    models.CharField(choices=[("HOME", "HOME"), ("CLASS", "CLASS")], default="CLASS", max_length=255),
                ),
            ],
            options={
                "verbose_name": "Assignment",
                "verbose_name_plural": "Assignments",
                "db_table": "assignment",
            },
        ),
        migrations.CreateModel(
            name="AssignmentQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("passage", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("marks", models.IntegerField(default=0)),
                ("sequence", models.IntegerField(default=0)),
                (
                    "type",
                    models.CharField(
                        choices=[("MCQ", "MCQ"), ("FIB", "FIB"), ("TF", "TF"), ("SPR", "SPR")],
                        default="MCQ",
                        max_length=255,
                    ),
                ),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_questions",
                        to="db.assignment",
                    ),
                ),
            ],
            options={
                "verbose_name": "AssignmentQuestion",
                "verbose_name_plural": "AssignmentQuestions",
                "db_table": "assignment_question",
            },
        ),
        migrations.CreateModel(
            name="QuestionOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_correct", models.BooleanField(default=False)),
                ("sequence", models.IntegerField(default=0)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="question_options",
                        to="db.assignmentquestion",
                    ),
                ),
            ],
            options={
                "verbose_name": "QuestionOption",
                "verbose_name_plural": "QuestionOptions",
                "db_table": "question_option",
            },
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("school_name", models.CharField(blank=True, max_length=255)),
                ("school_city", models.CharField(blank=True, max_length=255)),
                ("school_state", models.CharField(blank=True, max_length=255)),
                ("school_country", models.CharField(blank=True, max_length=255)),
                (
                    "school_curriculum",
                    models.CharField(
                        choices=[
                            ("ib", "IB"),
                            ("gcse", "GSSE"),
                            ("cbse", "CBSE"),
                            ("isc", "ISC"),
                            ("state_board", "State Board"),
                            ("american_curriculum", "American Curriculum"),
                            ("ap_curriculum", "AP Curriculum"),
                            ("level", "Level"),
                        ],
                        default="ib",
                        max_length=255,
                    ),
                ),
                (
                    "school_type",
                    models.CharField(
                        choices=[
                            ("boarding", "Boarding"),
                            ("day_school", "Day School"),
                            ("weekly_boarding", "Weekly Boarding"),
                        ],
                        default="boarding",
                        max_length=255,
                    ),
                ),
            ],
            options={
                "db_table": "db_school",
            },
        ),
        migrations.CreateModel(
            name="StudentAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("marks", models.IntegerField(default=0)),
                (
                    "type",
                    models.CharField(choices=[("HOME", "HOME"), ("CLASS", "CLASS")], default="CLASS", max_length=255),
                ),
                (
                    "assignment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_assignments",
                        to="db.assignment",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentAssignment",
                "verbose_name_plural": "StudentAssignments",
                "db_table": "student_assignment",
            },
        ),
        migrations.CreateModel(
            name="StudentAssignmentQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("passage", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("marks", models.IntegerField(default=0)),
                ("sequence", models.IntegerField(default=0)),
                (
                    "type",
                    models.CharField(
                        choices=[("MCQ", "MCQ"), ("FIB", "FIB"), ("TF", "TF"), ("SPR", "SPR")],
                        default="MCQ",
                        max_length=255,
                    ),
                ),
                (
                    "assignment_question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_assignment_questions",
                        to="db.assignmentquestion",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentAssignmentQuestion",
                "verbose_name_plural": "StudentAssignmentQuestions",
                "db_table": "student_assignment_question",
            },
        ),
        migrations.CreateModel(
            name="StudentDomain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sequence", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "StudentDomain",
                "verbose_name_plural": "StudentDomains",
                "db_table": "student_domain",
            },
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_address",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_board",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_city",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_country",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_curriculum",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_state",
        ),
        migrations.RemoveField(
            model_name="user",
            name="school_type",
        ),
        migrations.AddField(
            model_name="domain",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="megadomain",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="module",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="module",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="module",
            name="session_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modules",
                to="db.sessionplan",
            ),
        ),
        migrations.AddField(
            model_name="sessionplan",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="sessionplan",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="subtopic",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="subtopic",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="topic",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="topic",
            name="sequence",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="counselors",
            field=models.ManyToManyField(
                blank=True, related_name="_db_user_counselors_+", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="parents",
            field=models.ManyToManyField(blank=True, related_name="_db_user_parents_+", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="domain",
            name="mega_domain",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="domains", to="db.megadomain"
            ),
        ),
        migrations.AlterField(
            model_name="megadomain",
            name="subject",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mega_domains",
                to="db.subject",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("user", "User"),
                    ("tutor", "Tutor"),
                    ("typist", "Typist"),
                    ("manager", "Manager"),
                    ("prep_manager", "Prep Manager"),
                    ("sso_manager", "SSO Manager"),
                    ("parent", "Parent"),
                    ("counselor", "Counselor"),
                ],
                default="user",
                max_length=64,
            ),
        ),
        migrations.CreateModel(
            name="StudentTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sequence", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_topic",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student_domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_topic",
                        to="db.studentdomain",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_topic",
                        to="db.topic",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentTopic",
                "verbose_name_plural": "StudentTopics",
                "db_table": "student_topic",
            },
        ),
        migrations.CreateModel(
            name="StudentSubTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("sequence", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_extra", models.BooleanField(default=False)),
                ("time", models.CharField(default="15", max_length=20)),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_subtopic",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student_topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_subtopic",
                        to="db.studenttopic",
                    ),
                ),
                (
                    "sub_topic",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_subtopic",
                        to="db.subtopic",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentSubTopic",
                "verbose_name_plural": "StudentSubTopics",
                "db_table": "student_subtopic",
            },
        ),
        migrations.CreateModel(
            name="StudentSessionPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "category",
                    models.CharField(choices=[("r", "R"), ("s", "S"), ("t", "T")], default="r", max_length=20),
                ),
                (
                    "mega_domain",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_session_plan",
                        to="db.megadomain",
                    ),
                ),
                (
                    "session_plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_session_plan",
                        to="db.sessionplan",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_session_plan",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_session_plan",
                        to="db.subject",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentSession",
                "verbose_name_plural": "StudentSessions",
                "db_table": "student_session",
            },
        ),
        migrations.CreateModel(
            name="StudentQuestionOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_correct", models.BooleanField(default=False)),
                ("sequence", models.IntegerField(default=0)),
                (
                    "question_option",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_question_options",
                        to="db.questionoption",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_question_options",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student_assignment_question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_question_options",
                        to="db.studentassignmentquestion",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentQuestionOption",
                "verbose_name_plural": "StudentQuestionOptions",
                "db_table": "student_question_option",
            },
        ),
        migrations.CreateModel(
            name="StudentModule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sequence", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_module",
                        to="db.module",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_module",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student_session",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_module",
                        to="db.studentsessionplan",
                    ),
                ),
            ],
            options={
                "verbose_name": "StudentModule",
                "verbose_name_plural": "StudentModules",
                "db_table": "student_module",
            },
        ),
        migrations.AddField(
            model_name="studentdomain",
            name="domain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_domain",
                to="db.domain",
            ),
        ),
        migrations.AddField(
            model_name="studentdomain",
            name="student",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_domain",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="studentdomain",
            name="student_module",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_domain",
                to="db.studentmodule",
            ),
        ),
        migrations.AddField(
            model_name="studentassignmentquestion",
            name="student",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_assignment_questions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="studentassignmentquestion",
            name="student_assignment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_assignment_questions",
                to="db.studentassignment",
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="domain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.domain"
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="megadomain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.megadomain"
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="module",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.module"
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="student",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_assignments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.subject"
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="subtopic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.subtopic"
            ),
        ),
        migrations.AddField(
            model_name="studentassignment",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="student_assignments", to="db.topic"
            ),
        ),
        migrations.CreateModel(
            name="ReasonForError",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="reason_for_error", to="db.topic"
                    ),
                ),
            ],
            options={
                "verbose_name": "ReasonForError",
                "verbose_name_plural": "ReasonForErrors",
                "db_table": "reason_for_errors",
            },
        ),
        migrations.AddField(
            model_name="assignment",
            name="domain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.domain",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="megadomain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.megadomain",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="module",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.module",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="subject",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.subject",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="subtopic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.subtopic",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="topic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="db.topic",
            ),
        ),
    ]
