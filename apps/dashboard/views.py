from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Avg, Count, Max
from django.http import JsonResponse
from apps.accounts.decorators import teacher_required, student_required
from django.utils.decorators import method_decorator
from apps.assessments.models import Submission
from apps.assessments.services import generate_student_strategies
from apps.accounts.models import User
from .models import TeacherNote
from .forms import TeacherNoteForm
from .ai_services import generate_cohort_ai_strategy, generate_student_ai_playbook

@method_decorator(student_required, name='dispatch')
class StudentDashboardView(LoginRequiredMixin, View):
    """
    Renders the student results portal displaying the psychometric persona,
    5-metric score meters, tailored study habits toolkit, and past assessment history.
    """
    def get(self, request, submission_id=None):
        if submission_id:
            if request.user.role == User.Role.TEACHER:
                submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id)
                student_submissions = Submission.objects.filter(student=submission.student).order_by('-submitted_at')
            else:
                submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id, student=request.user)
                student_submissions = Submission.objects.filter(student=request.user).order_by('-submitted_at')
        else:
            student_submissions = Submission.objects.filter(
                student=request.user
            ).order_by('-submitted_at')
            if not student_submissions.exists():
                return render(request, 'dashboard/student_results.html', {
                    'submission': None,
                    'has_submissions': False,
                    'tier_display': request.user.get_tier_display_label(),
                })
            submission = student_submissions.first()

        scores = {
            'visual_score': submission.visual_score,
            'auditory_score': submission.auditory_score,
            'kinesthetic_score': submission.kinesthetic_score,
            'growth_score': submission.growth_score,
            'stress_score': submission.stress_score,
        }

        persona_dict = {
            'title': submission.persona_title,
            'tagline': submission.persona_tagline,
        }

        strategies = generate_student_strategies(scores, persona_dict, submission.tier)
        tier_display = dict(User.AcademicTier.choices).get(submission.tier, submission.tier)

        context = {
            'submission': submission,
            'has_submissions': True,
            'historical_submissions': student_submissions,
            'total_attempts': student_submissions.count(),
            'strategies': strategies,
            'tier_display': tier_display,
            'is_latest': (submission.id == student_submissions.first().id),
        }
        return render(request, 'dashboard/student_results.html', context)


@method_decorator(teacher_required, name='dispatch')
class TeacherOverviewView(LoginRequiredMixin, View):
    """
    Teacher Command Center:
    Aggregates classroom cohort metrics, multi-criteria filtering & search,
    student roster cards with 5-score previews, and AI copilot integration.
    """
    def get(self, request):
        submissions_qs = Submission.objects.select_related('student').order_by('-submitted_at')

        # Overall Cohort Metrics
        all_subs = Submission.objects.all()
        total_tested = all_subs.values('student').distinct().count() or all_subs.count()

        if all_subs.exists():
            avg_stats = all_subs.aggregate(
                avg_visual=Avg('visual_score'),
                avg_auditory=Avg('auditory_score'),
                avg_kinesthetic=Avg('kinesthetic_score'),
                avg_growth=Avg('growth_score'),
                avg_stress=Avg('stress_score')
            )
            v_avg = round(avg_stats['avg_visual'] or 0)
            a_avg = round(avg_stats['avg_auditory'] or 0)
            k_avg = round(avg_stats['avg_kinesthetic'] or 0)
            g_avg = round(avg_stats['avg_growth'] or 0)
            s_avg = round(avg_stats['avg_stress'] or 0)

            modality_total = max(v_avg + a_avg + k_avg, 1)
            v_pct = round((v_avg / modality_total) * 100)
            a_pct = round((a_avg / modality_total) * 100)
            k_pct = round((k_avg / modality_total) * 100)

            if k_pct >= v_pct and k_pct >= a_pct:
                dominant_modality = 'Kinesthetic'
            elif v_pct >= a_pct:
                dominant_modality = 'Visual'
            else:
                dominant_modality = 'Auditory'

            stress_watchlist_count = all_subs.filter(stress_score__gte=65).count()
            growth_champions_count = all_subs.filter(growth_score__gte=75).count()
        else:
            v_avg = a_avg = k_avg = g_avg = s_avg = 0
            v_pct = a_pct = k_pct = 0
            dominant_modality = 'Not Evaluated'
            stress_watchlist_count = 0
            growth_champions_count = 0

        cohort_stats = {
            'total_students': total_tested,
            'avg_visual': v_avg,
            'avg_auditory': a_avg,
            'avg_kinesthetic': k_avg,
            'avg_growth': g_avg,
            'avg_stress': s_avg,
            'visual_pct': v_pct,
            'auditory_pct': a_pct,
            'kinesthetic_pct': k_pct,
            'dominant_modality': dominant_modality,
            'stress_watchlist_count': stress_watchlist_count,
            'growth_champions_count': growth_champions_count,
        }

        # Apply Filters
        active_tier = request.GET.get('tier', '')
        active_style = request.GET.get('style', '')
        active_status = request.GET.get('status', '')
        search_query = request.GET.get('q', '').strip()
        sort_by = request.GET.get('sort', 'newest')

        filtered_qs = submissions_qs

        if active_tier in [t[0] for t in User.AcademicTier.choices]:
            filtered_qs = filtered_qs.filter(tier=active_tier)

        if active_style == 'VISUAL':
            filtered_qs = filtered_qs.filter(visual_score__gte=Avg('visual_score'))
        elif active_style == 'AUDITORY':
            filtered_qs = filtered_qs.filter(auditory_score__gte=Avg('auditory_score'))
        elif active_style == 'KINESTHETIC':
            filtered_qs = filtered_qs.filter(kinesthetic_score__gte=Avg('kinesthetic_score'))

        if active_status == 'HIGH_STRESS':
            filtered_qs = filtered_qs.filter(stress_score__gte=65)
        elif active_status == 'HIGH_GROWTH':
            filtered_qs = filtered_qs.filter(growth_score__gte=75)

        if search_query:
            filtered_qs = filtered_qs.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__username__icontains=search_query) |
                Q(student__email__icontains=search_query) |
                Q(student__institution__icontains=search_query) |
                Q(student__grade_or_year__icontains=search_query) |
                Q(persona_title__icontains=search_query)
            )

        if sort_by == 'oldest':
            filtered_qs = filtered_qs.order_by('submitted_at')
        elif sort_by == 'stress_desc':
            filtered_qs = filtered_qs.order_by('-stress_score')
        elif sort_by == 'growth_desc':
            filtered_qs = filtered_qs.order_by('-growth_score')
        elif sort_by == 'name_asc':
            filtered_qs = filtered_qs.order_by('student__first_name', 'student__last_name')
        else:
            filtered_qs = filtered_qs.order_by('-submitted_at')

        saved_llm_key = request.session.get('teacher_llm_api_key', '')
        has_custom_llm_key = bool(saved_llm_key)

        context = {
            'teacher': request.user,
            'submissions': filtered_qs,
            'total_matching': filtered_qs.count(),
            'cohort_stats': cohort_stats,
            'all_tiers': User.AcademicTier.choices,
            'active_tier': active_tier,
            'active_style': active_style,
            'active_status': active_status,
            'search_query': search_query,
            'sort_by': sort_by,
            'has_custom_llm_key': has_custom_llm_key,
            'saved_llm_key_masked': f"••••••••{saved_llm_key[-4:]}" if len(saved_llm_key) > 4 else ("Configured" if saved_llm_key else "Not Set"),
        }
        return render(request, 'dashboard/teacher_dashboard.html', context)


@method_decorator(teacher_required, name='dispatch')
class StudentPlaybookView(LoginRequiredMixin, View):
    """
    Teacher 1-on-1 Deep-Dive Playbook:
    Presents 3-pillar pedagogical guidance, Whole-Student profile tags,
    open student message to educator, timestamped private notes, and AI lesson plan generator.
    """
    def get(self, request, student_id=None, submission_id=None):
        if submission_id:
            submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id)
            student = submission.student
        else:
            student = get_object_or_404(User, id=student_id)
            student_submissions = Submission.objects.filter(student=student).order_by('-submitted_at')
            if not student_submissions.exists():
                messages.warning(request, f"Student {student.get_full_name() or student.username} has not completed any diagnostic assessments yet.")
                return redirect('dashboard:teacher_overview')
            submission = student_submissions.first()

        historical_submissions = Submission.objects.filter(student=student).order_by('-submitted_at')
        teacher_notes = TeacherNote.objects.filter(student=student).order_by('-created_at')
        note_form = TeacherNoteForm()

        scores = {
            'visual_score': submission.visual_score,
            'auditory_score': submission.auditory_score,
            'kinesthetic_score': submission.kinesthetic_score,
            'growth_score': submission.growth_score,
            'stress_score': submission.stress_score,
        }
        persona_dict = {
            'title': submission.persona_title,
            'tagline': submission.persona_tagline,
        }
        strategies = generate_student_strategies(scores, persona_dict, submission.tier)

        context = {
            'student': student,
            'submission': submission,
            'historical_submissions': historical_submissions,
            'teacher_notes': teacher_notes,
            'note_form': note_form,
            'strategies': strategies,
            'tier_display': submission.get_tier_display(),
            'is_latest': (submission.id == historical_submissions.first().id if historical_submissions.exists() else True),
            'has_custom_llm_key': bool(request.session.get('teacher_llm_api_key')),
        }
        return render(request, 'dashboard/student_playbook.html', context)

    def post(self, request, student_id=None, submission_id=None):
        if submission_id:
            submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id)
            student = submission.student
        else:
            student = get_object_or_404(User, id=student_id)
            submission = Submission.objects.filter(student=student).order_by('-submitted_at').first()

        form = TeacherNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.teacher = request.user
            note.student = student
            note.submission = submission
            note.save()
            messages.success(request, "✓ Private observation note recorded successfully.")
        else:
            messages.error(request, "Please enter valid note content before saving.")

        if submission_id:
            return redirect('dashboard:submission_playbook', submission_id=submission.id)
        return redirect('dashboard:student_playbook', student_id=student.id)


class DeleteTeacherNoteView(LoginRequiredMixin, View):
    """
    Allows teachers to delete their own notes.
    """
    def post(self, request, note_id):
        note = get_object_or_404(TeacherNote, id=note_id, teacher=request.user)
        student_id = note.student.id
        sub_id = note.submission.id if note.submission else None
        note.delete()
        messages.success(request, "Observation note deleted.")

        if sub_id:
            return redirect('dashboard:submission_playbook', submission_id=sub_id)
        return redirect('dashboard:student_playbook', student_id=student_id)


class GenerateStudentAIPlanView(LoginRequiredMixin, View):
    """
    Generates a 4-part individualized AI lesson and conversation strategy for a student.
    """
    def get(self, request, submission_id):
        submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id)
        student = submission.student

        student_data = {
            'name': student.get_full_name() or student.username,
            'tier': submission.get_tier_display(),
            'persona_title': submission.persona_title,
            'visual_score': submission.visual_score,
            'kinesthetic_score': submission.kinesthetic_score,
            'auditory_score': submission.auditory_score,
            'growth_score': submission.growth_score,
            'stress_score': submission.stress_score,
            'personality_tag': submission.personality_tag or 'Achiever',
            'interests_tag': submission.interests_tag or 'STEM/Analytical',
            'wellbeing_flag': submission.wellbeing_flag or 'Green',
            'soft_skills': submission.soft_skills_summary or 'Collaborative, Reliable',
            'open_message': submission.open_message_to_teacher,
        }

        api_key = request.session.get('teacher_llm_api_key')
        ai_result = generate_student_ai_playbook(student_data, api_key=api_key)

        return JsonResponse({
            'success': True,
            'is_live_ai': ai_result['is_live_ai'],
            'source': ai_result['source'],
            'analysis': ai_result['content']
        })


class SaveTeacherLLMKeyView(LoginRequiredMixin, View):
    """
    Saves the teacher's LLM API key into session.
    """
    def post(self, request):
        api_key = request.POST.get('api_key', '').strip()
        provider = request.POST.get('provider', 'gemini')

        if not api_key:
            request.session.pop('teacher_llm_api_key', None)
            messages.info(request, "Custom LLM API key cleared. The platform will use offline pedagogical synthesis.")
            return redirect('dashboard:teacher_overview')

        request.session['teacher_llm_api_key'] = api_key
        request.session['teacher_llm_provider'] = provider
        messages.success(request, "✨ LLM API Key successfully configured! AI Pedagogical Co-Pilot is now active.")
        return redirect('dashboard:teacher_overview')


class GenerateCohortAISummaryView(LoginRequiredMixin, View):
    """
    Generates an AI cohort analysis using LLM or offline fallback engine.
    """
    def get(self, request):
        all_subs = Submission.objects.all()
        total = all_subs.values('student').distinct().count() or all_subs.count()

        if total == 0:
            return JsonResponse({
                'success': False,
                'message': 'No student submissions found to analyze.'
            })

        avg_stats = all_subs.aggregate(
            avg_v=Avg('visual_score'),
            avg_a=Avg('auditory_score'),
            avg_k=Avg('kinesthetic_score'),
            avg_g=Avg('growth_score')
        )
        v = round(avg_stats['avg_v'] or 0)
        a = round(avg_stats['avg_a'] or 0)
        k = round(avg_stats['avg_k'] or 0)
        tot = max(v + a + k, 1)

        cohort_data = {
            'total_students': total,
            'visual_pct': round((v / tot) * 100),
            'auditory_pct': round((a / tot) * 100),
            'kinesthetic_pct': round((k / tot) * 100),
            'avg_growth': round(avg_stats['avg_g'] or 0),
            'stress_count': all_subs.filter(stress_score__gte=65).count(),
        }

        api_key = request.session.get('teacher_llm_api_key')
        ai_result = generate_cohort_ai_strategy(cohort_data, api_key=api_key)

        return JsonResponse({
            'success': True,
            'is_live_ai': ai_result['is_live_ai'],
            'source': ai_result['source'],
            'analysis': ai_result['content']
        })


class StudentReportPDFView(LoginRequiredMixin, View):
    """
    Renders a print-optimized, clean A4 PDF conference report.
    Accessible to teachers for any student, or students for their own submission.
    """
    def get(self, request, submission_id):
        if request.user.role == User.Role.TEACHER:
            submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id)
        else:
            submission = get_object_or_404(Submission.objects.select_related('student'), id=submission_id, student=request.user)

        context = {
            'student': submission.student,
            'submission': submission,
            'viewer': request.user,
        }
        return render(request, 'dashboard/student_report_pdf.html', context)

