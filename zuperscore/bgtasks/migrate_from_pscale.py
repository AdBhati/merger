from django_rq import job
from sentry_sdk import capture_exception
from zuperscore.db.models.assessments import UserAttempt
from zuperscore.db.models import Question, AssessmentSection

@job("default")
def migrate_from_pscale(assessment_id, data):
    try:
        print(f"Migrated BG STARTED from PSCALE for assessment_id: {assessment_id}")
        print("length of attempts", len(data))
        UserAttempt.objects.filter(assessment_id=assessment_id, stat="MIGRATED").delete()
        user_attempt_objects = []
        for attempt in data:
            if Question.objects.filter(id=attempt['question']).exists() and AssessmentSection.objects.filter(id=attempt['section']).exists():
                obj = UserAttempt(
                    session_id=attempt['session'],
                    user_id=attempt['user'],
                    section_id=attempt['section'],
                    question_id=attempt['question'],
                    type=attempt['type'],
                    is_bookmark=attempt['is_bookmark'],
                    data=attempt['data'],
                    extra=attempt['extra'],
                    info=attempt['info'],
                    time_taken=attempt['time_taken'],
                    assessment_id=attempt['assessment'],
                    is_visited=attempt['is_visited'],
                    masked_options=attempt['masked_options'],
                    is_answered=attempt['is_answered'],
                    analysis_data=attempt['analysis_data'],
                    stat="MIGRATED",
                )
                user_attempt_objects.append(obj)
        UserAttempt.objects.bulk_create(user_attempt_objects, batch_size=6000)
        print(f"Migrated BG SUCESSFULLY from PSCALE for assessment_id: {assessment_id}")
    except Exception as e:
        print(f"Migrated BG FAILED START from PSCALE for assessment_id: {assessment_id}")
        print(e)
        print(f"Migrated BG FAILED END from PSCALE for assessment_id: {assessment_id}")
        capture_exception(e)
        return