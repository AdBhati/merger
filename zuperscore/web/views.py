from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect

from zuperscore.db.models.assessments import (
    Assessment,
    AssessmentSection,
    SectionQuestion,
    Question,
    QuestionNode,
    UserAssessmentSession,
)
from zuperscore.db.models import User


# Create your views here.
class TestQuestionsIrtEndpoint(View):
    def get(self, request, pk):
        assessment = Assessment.objects.get(pk=pk)
        assessment_sections = AssessmentSection.objects.filter(assessment_id=pk)
        assessment_questions = []
        for section in assessment_sections:
            section_id = section.id
            if section.type == "STANDARD":
                section_questions = SectionQuestion.objects.filter(
                    section_id=section_id
                )
                for idx, question in enumerate(section_questions):
                    question_id = question.question_id
                    q = Question.objects.filter(pk=question_id)
                    if q:
                        assessment_questions.append(
                            {
                                "section": section_id,
                                "type": section.type,
                                "name": section.name,
                                "question": q[0].id,
                                "irt_a": q[0].irt_a,
                                "irt_b": q[0].irt_b,
                                "irt_c": q[0].irt_c,
                                "no": (
                                    f"MA {idx+1}"
                                    if q[0].subject.id == 1
                                    else f"A {idx+1}"
                                ),
                            }
                        )
            else:
                eng_alpha = ["B", "C"]
                math_alpha = ["MB", "MC"]
                for idx, switch in enumerate(section.switching_route):
                    folder_id = switch["folder_id"]
                    questions = QuestionNode.objects.filter(
                        node_id=folder_id
                    ).values_list("question_id", flat=True)
                    questions = Question.objects.filter(pk__in=questions)
                    for qidx, question in enumerate(questions):
                        if question:
                            assessment_questions.append(
                                {
                                    "section": section_id,
                                    "type": section.type,
                                    "name": section.name,
                                    "question": question.id,
                                    "irt_a": question.irt_a,
                                    "irt_b": question.irt_b,
                                    "irt_c": question.irt_c,
                                    "no": (
                                        math_alpha[idx] + " " + str(qidx + 1)
                                        if q[0].subject.id == 1
                                        else eng_alpha[idx] + " " + str(qidx + 1)
                                    ),
                                }
                            )

        return render(
            request,
            "tests_irt.html",
            {"assessment": assessment, "questions": assessment_questions},
        )

    def post(self, request, pk):
        print('this is post', request.POST)
        for key, value in request.POST.items():
            if key.startswith("irt_"):
                q_key, q_id = key.split("-")
                question = Question.objects.filter(pk=q_id).first()
                if question:
                    setattr(question, q_key, value)
                    question.save()
        english_sigma = request.POST.get("english_sigma", 0)
        english_xbar = request.POST.get("english_xbar", 0)
        math_sigma = request.POST.get("math_sigma", 0)
        math_xbar = request.POST.get("math_xbar", 0)
        Assessment.objects.filter(pk=pk).update(
            english_sigma=english_sigma,
            english_xbar=english_xbar,
            math_sigma=math_sigma,
            math_xbar=math_xbar,
        )
        return redirect(request.path_info)


class TestQuestionsSessionsEndpoint(View):
    def get(self, request, session_id):
        assessment_session = UserAssessmentSession.objects.get(pk=session_id)
        assessment_id = assessment_session.assessment_id
        assessment = Assessment.objects.get(pk=assessment_id)
        user_id = assessment_session.user_id
        user = User.objects.get(pk=user_id)
        high_level_details = {
            "session_id": session_id,
            "user_id": user.id,
            "user_name": user.email,
            "assessment_id": assessment.id,
            "assessment_name": assessment.name,
        }
        return render(
            request,
            "tests_scaled_score.html",
            {"high_level_details": high_level_details},
        )
