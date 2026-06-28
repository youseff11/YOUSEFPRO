from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Project, ProjectParagraph, ProjectImage, ContactMessage


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        self.attrs.update(attrs)


class MultiFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProjectAdminForm(forms.ModelForm):
    upload_multiple_images = MultiFileField(
        label="📸 رفع عدة صور دفعة واحدة",
        required=False,
        help_text="اختر عدة صور مرة واحدة (اضغط Ctrl أو Shift لاختيار أكثر من صورة)"
    )

    class Meta:
        model = Project
        fields = '__all__'


class ProjectParagraphInline(admin.StackedInline):
    model = ProjectParagraph
    extra = 1
    fields = ('text', 'text_en', 'order')


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0
    fields = ('image', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: auto; border-radius: 5px; border: 1px solid #ccc;" />',
                obj.image.url
            )
        return "لا توجد صورة"

    preview_image.short_description = 'معاينة الصورة'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('get_image', 'title', 'order', 'technologies', 'is_published', 'created_at')
    list_display_links = ('get_image', 'title')
    list_editable = ('is_published', 'order')
    search_fields = ('title', 'description', 'technologies')
    list_filter = ('is_published', 'created_at')
    ordering = ('order', '-created_at')
    inlines = [ProjectParagraphInline, ProjectImageInline]

    fieldsets = (
        ('البيانات الأساسية (عربي)', {
            'fields': ('title', 'description', 'technologies', 'live_url', 'github_url', 'is_published', 'order')
        }),
        ('الترجمة الإنجليزية (اختياري)', {
            'classes': ('collapse',),
            'fields': ('title_en', 'description_en'),
            'description': 'أضف الترجمة الإنجليزية هنا لتفعيل زرار تبديل اللغة في الموقع'
        }),
        ('رفع الصور', {
            'fields': ('upload_multiple_images',),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        images = request.FILES.getlist('upload_multiple_images')
        for image in images:
            ProjectImage.objects.create(project=obj, image=image)

    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                first_image.image.url
            )
        return "No Image"

    get_image.short_description = 'Preview'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
