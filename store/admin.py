from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Project, ProjectParagraph, ProjectImage, ContactMessage

class MultiFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs.update({'multiple': True})

class ProjectAdminForm(forms.ModelForm):
    upload_multiple_images = forms.FileField(
        widget=MultiFileInput(),
        label="إضافة عدة صور دفعة واحدة",
        required=False
    )

    class Meta:
        model = Project
        fields = '__all__'

class ProjectParagraphInline(admin.StackedInline):
    model = ProjectParagraph
    extra = 1

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0
    fields = ('image', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 150px; height: auto; border-radius: 5px; border: 1px solid #ccc;" />', obj.image.url)
        return "لا توجد صورة"

    preview_image.short_description = 'معاينة الصورة'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('get_image', 'title', 'technologies', 'is_published', 'created_at')
    list_display_links = ('get_image', 'title')
    search_fields = ('title', 'description', 'technologies')
    list_filter = ('is_published', 'created_at')
    ordering = ('-created_at',)
    list_editable = ('is_published',)
    inlines = [ProjectParagraphInline, ProjectImageInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        images = request.FILES.getlist('upload_multiple_images')
        for image in images:
            ProjectImage.objects.create(project=obj, image=image)

    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" style="width: 80px; height: 50px; object-fit: cover; border-radius: 8px;" />', first_image.image.url)
        return "No Image"
    
    get_image.short_description = 'Preview'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)