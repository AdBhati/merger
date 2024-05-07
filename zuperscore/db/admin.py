from django.contrib import admin

# Register your models here.
from zuperscore.db.models.library import Topic, MegaDomain, Domain, SubTopic, Exam, Subject, Settings, ReasonForError
from zuperscore.db.models.assessments import AssessmentTags
from zuperscore.db.models.base import School


class MegaDomainAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "exam")
    list_filter = ("subject__name",)

    def subject(self, obj):
        return obj.subject.name

    def exam(self, obj):
        return obj.subject.exam.name


class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "mega_domain", "subject", "exam")
    list_filter = (
        "domain__name",
        "domain__mega_domain__name",
        "domain__mega_domain__subject__name",
        "domain__mega_domain__subject__exam__name",
    )

    def mega_domain(self, obj):
        return obj.domain.mega_domain.name

    def subject(self, obj):
        return obj.domain.mega_domain.subject.name

    def exam(self, obj):
        return obj.domain.mega_domain.subject.exam.name


class DomainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "mega_domain",
        "subject",
        "exam",
    )
    list_filter = ("mega_domain__name", "mega_domain__subject__name", "mega_domain__subject__exam__name")

    def subject(self, obj):
        return obj.mega_domain.subject.name

    def exam(self, obj):
        return obj.mega_domain.subject.exam.name


class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "mega_domain", "domain", "subject", "exam")
    list_filter = (
        "topic__name",
        "topic__domain__name",
        "topic__domain__mega_domain__name",
        "topic__domain__mega_domain__subject__name",
        "topic__domain__mega_domain__subject__exam__name",
    )

    def mega_domain(self, obj):
        return obj.topic.domain.mega_domain.name

    def domain(self, obj):
        return obj.topic.domain.name

    def subject(self, obj):
        return obj.topic.domain.mega_domain.subject.name

    def exam(self, obj):
        return obj.topic.domain.mega_domain.subject.exam.name


class TempDomainAdmin(admin.ModelAdmin):
    list_display = ("name",)


class TempTopicAdmin(admin.ModelAdmin):
    list_display = ("name",)


class TempSupTopicAdmin(admin.ModelAdmin):
    list_display = ("name",)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "exam")
    list_filter = ("exam__name",)


class ExamAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)

class ReasonForErrorAdmin(admin.ModelAdmin):
    list_display = ("name", "topic",)
    list_filter = ("topic__name",)

    def topic(self,obj):
        return obj.topic.name

class SettingsAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AssessmentTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("is_active",)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ("school_name",)
    list_filter = (
        "school_state",
        "school_country",
    )


admin.site.register(Topic, TempTopicAdmin)
admin.site.register(MegaDomain, MegaDomainAdmin)
admin.site.register(Domain, TempDomainAdmin)
admin.site.register(SubTopic, TempSupTopicAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(AssessmentTags, AssessmentTagAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(ReasonForError, ReasonForErrorAdmin)
