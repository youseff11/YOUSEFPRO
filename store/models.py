from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان المشروع")
    description = models.TextField(verbose_name="وصف المشروع")
    technologies = models.CharField(max_length=200, blank=True, verbose_name="التقنيات المستخدمة (مثل: Django, HTML)")
    live_url = models.URLField(blank=True, verbose_name="رابط المشروع الحي (Live)")
    github_url = models.URLField(blank=True, verbose_name="رابط الكود (GitHub - إن وجد)")
    is_published = models.BooleanField(default=True, verbose_name="نشر المشروع؟ (إلغاء التحديد سيخفيه من الموقع)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"

    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio_images/')

    class Meta:
        verbose_name = "صورة المشروع"
        verbose_name_plural = "صور المشروع"
class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم المرسل")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", blank=True, null=True)
    subject = models.CharField(max_length=250, blank=True, null=True, verbose_name="الموضوع")
    message = models.TextField(verbose_name="محتوى الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"

    def __str__(self):
        return f"رسالة من: {self.name} - {self.subject if self.subject else 'بدون موضوع'}"