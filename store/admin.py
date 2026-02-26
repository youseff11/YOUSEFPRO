from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage ,ContactMessage

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    # تحديد الحقول التي ستظهر في الـ Inline
    fields = ('image', 'preview_image')
    # جعل حقل المعاينة للقراءة فقط حتى لا يحاول دجانغو البحث عنه في قاعدة البيانات
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 150px; height: auto; border-radius: 5px; border: 1px solid #ccc;" />', obj.image.url)
        return "لا توجد صورة"

    preview_image.short_description = 'معاينة الصورة'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('get_image', 'title', 'technologies', 'is_published', 'created_at')
    list_display_links = ('get_image', 'title')
    search_fields = ('title', 'description', 'technologies')
    list_filter = ('is_published', 'created_at')
    ordering = ('-created_at',)
    list_editable = ('is_published',)
    inlines = [ProjectImageInline]

    def get_image(self, obj):
        # محاولة جلب أول صورة مرتبطة بالمشروع
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
    readonly_fields = ('created_at',) # لجعل التاريخ للقراءة فقط