from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.accounts.decorators import student_required
from django.utils.decorators import method_decorator
from .models import Question, Submission, Choice
from .services import calculate_and_save_submission
from apps.accounts.models import User

@method_decorator(student_required, name='dispatch')
class TakeQuizView(LoginRequiredMixin, View):
    def get(self, request):
        # Allow student to select or switch tier for testing/taking
        requested_tier = request.GET.get('tier')
        user_tier = getattr(request.user, 'academic_tier', None) or User.AcademicTier.SCHOOL
        
        valid_tiers = [t[0] for t in User.AcademicTier.choices]
        active_tier = requested_tier if requested_tier in valid_tiers else user_tier

        # Fetch active questions for this tier with prefetched choices
        questions = Question.objects.filter(
            tier=active_tier,
            is_active=True
        ).prefetch_related('choices').order_by('order', 'id')

        # Compute tier labels
        tier_display = dict(User.AcademicTier.choices).get(active_tier, active_tier)
        all_tiers = User.AcademicTier.choices

        # Previous submissions if any
        recent_submission = Submission.objects.filter(
            student=request.user
        ).order_by('-submitted_at').first()

        context = {
            'questions': questions,
            'active_tier': active_tier,
            'tier_display': tier_display,
            'all_tiers': all_tiers,
            'total_questions': questions.count(),
            'recent_submission': recent_submission,
        }
        return render(request, 'assessments/take_quiz.html', context)

    def post(self, request):
        tier = request.POST.get('tier') or request.user.academic_tier or User.AcademicTier.SCHOOL
        
        # Verify questions exist
        questions = Question.objects.filter(tier=tier, is_active=True)
        total_questions = questions.count()

        # Validate that all questions were answered
        unanswered = []
        for idx, q in enumerate(questions.order_by('order', 'id'), start=1):
            choice_val = request.POST.get(f'question_{q.id}')
            if not choice_val:
                unanswered.append(f"#{idx}")

        if unanswered:
            messages.error(
                request,
                f"Please answer all {total_questions} questions before submitting. Unanswered questions: {', '.join(unanswered)}"
            )
            return redirect(f"{request.path}?tier={tier}")

        try:
            submission = calculate_and_save_submission(request.user, request.POST, tier=tier)
            messages.success(
                request,
                f"🎉 Assessment completed successfully! Your learning persona is '{submission.persona_title}'."
            )
            return redirect('dashboard:student_results_detail', submission_id=submission.id)
        except Exception as e:
            messages.error(request, f"Error processing submission: {str(e)}")
            return redirect(f"{request.path}?tier={tier}")


from .services import calculate_and_save_submission, generate_student_strategies

@method_decorator(student_required, name='dispatch')
class QuizSuccessView(LoginRequiredMixin, View):
    def get(self, request, submission_id):
        submission = get_object_or_404(
            Submission.objects.select_related('student').prefetch_related('answers__question', 'answers__selected_choice'),
            id=submission_id,
            student=request.user
        )
        scores = {
            'visual_score': submission.visual_score,
            'auditory_score': submission.auditory_score,
            'kinesthetic_score': submission.kinesthetic_score,
            'growth_score': submission.growth_score,
            'stress_score': submission.stress_score,
        }
        strategies = generate_student_strategies(scores, {'title': submission.persona_title}, submission.tier)

        return render(request, 'assessments/quiz_completed.html', {
            'submission': submission,
            'tier_display': dict(User.AcademicTier.choices).get(submission.tier, submission.tier),
            'strategies': strategies,
        })
