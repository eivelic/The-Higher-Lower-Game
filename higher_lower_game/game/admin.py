from django.contrib import admin
from .models import ClassicItem, CSQuestion
from import_export.admin import ExportMixin, ImportExportModelAdmin

# Register your models here.

@admin.register(CSQuestion)
class CSQuestionAdmin(ImportExportModelAdmin):
    list_display = ('question_text', 'correct_answer', 'difficulty')

@admin.register(ClassicItem)
class ClassicItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_searches')
