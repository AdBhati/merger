from zuperscore.api.views.base import BaseSerializer
from zuperscore.db.models import AssessmentSection, Assessment
from zuperscore.db.models.assessments import UserAssessmentSession


class AssessmentMinimumSerailizer(BaseSerializer):
    class Meta:
        model = Assessment
        fields = ("id", "name", "kind", "assessment_type", "state", "max_attempts")


class UserAssessmentSessionMinimumSerializer(BaseSerializer):
    assessment_detail = AssessmentMinimumSerailizer(read_only=True, source="assessment")

    class Meta:
        model = UserAssessmentSession
        fields = (
            "id",
            "assessment",
            "user",
            "is_submitted",
            "assessment_detail",
            "section_analysis_data",
        )
