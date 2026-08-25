from django.contrib import admin
from .models import Question, Choice, Submission, SubmissionAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ('order', 'text', 'visual_weight', 'auditory_weight', 'kinesthetic_weight', 'growth_weight', 'stress_weight')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt_preview', 'tier', 'category', 'order', 'choice_count', 'is_active')
    list_filter = ('tier', 'category', 'is_active')
    search_fields = ('prompt', 'subtitle')
    inlines = [ChoiceInline]
    ordering = ('tier', 'order', 'id')

    def prompt_preview(self, obj):
        return obj.prompt[:75] + '...' if len(obj.prompt) > 75 else obj.prompt
    prompt_preview.short_description = 'Prompt'

    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Choices'


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice')
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'tier', 'persona_title', 'visual_score', 'auditory_score', 'kinesthetic_score', 'growth_score', 'stress_score', 'submitted_at')
    list_filter = ('tier', 'persona_title', 'submitted_at')
    search_fields = ('student__username', 'student__email', 'student__first_name', 'student__last_name', 'persona_title')
    readonly_fields = ('submitted_at',)
    inlines = [SubmissionAnswerInline]
    ordering = ('-submitted_at',)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'visual_weight', 'auditory_weight', 'kinesthetic_weight', 'growth_weight', 'stress_weight')
    list_filter = ('question__tier', 'question__category')
    search_fields = ('text', 'question__prompt')
