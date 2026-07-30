import os
import resend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.utils.html import strip_tags
from .models import Project, ContactMessage

# --- الصفحة الرئيسية ---
def index(request):
    # PERF: list() تنفّذ الاستعلام مرة واحدة، و len() لا تعمل استعلام COUNT إضافي على قاعدة البيانات
    projects = list(
        Project.objects.filter(is_published=True)
        .prefetch_related('images', 'paragraphs')
        .order_by('order', '-created_at')
    )
    context = {
        'projects': projects,
        'total_projects': len(projects),
    }
    return render(request, 'index.html', context)

# --- صفحة كل المشاريع ---
def project(request):
    projects = list(
        Project.objects.filter(is_published=True)
        .prefetch_related('images', 'paragraphs')
        .order_by('order', '-created_at')
    )
    context = {
        'projects': projects,
        'total_projects': len(projects),
    }
    return render(request, 'projects.html', context)

# --- صفحة تفاصيل المشروع ---
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('images'), 
        pk=pk, 
        is_published=True
    )
    return render(request, 'project_detail.html', {'project': project})

# --- صفحة التواصل (مع نظام الإرسال الاحترافي عبر Resend) ---
def contact(request):
    if request.method == 'POST':
        # سحب البيانات من الفورم
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject') or "طلب جديد من الموقع"
        message_content = request.POST.get('message')

        # 1. حفظ الرسالة في قاعدة البيانات (للمراجعة من لوحة Admin)
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_content
        )

        # 2. إعداد محتوى الإيميل بتنسيق HTML (Cyber Theme)
        html_content = f"""
        <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 600px; margin: auto; border: 1px solid #00f3ff; border-radius: 15px; overflow: hidden; background-color: #030305; color: #ffffff;">
            <div style="background: linear-gradient(90deg, #00f3ff, #bc13fe); padding: 20px; text-align: center;">
                <h2 style="margin: 0; color: #000; letter-spacing: 2px; font-weight: bold;">رسالة جديدة من الموقع</h2>
            </div>
            <div style="padding: 30px; line-height: 1.6;">
                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px;">👤 <strong>بيانات المرسل:</strong></p>
                <p><strong>الاسم:</strong> {name}</p>
                <p><strong>البريد:</strong> <a href="mailto:{email}" style="color: #00f3ff;">{email}</a></p>
                <p><strong>الهاتف:</strong> <a href="tel:{phone}" style="color: #00f3ff;">{phone}</a></p>
                
                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 25px;">📝 <strong>الموضوع:</strong></p>
                <p>{subject}</p>

                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 25px;">💬 <strong>نص الرسالة:</strong></p>
                <div style="background: #111; padding: 15px; border-radius: 8px; border-right: 4px solid #00f3ff; white-space: pre-wrap;">
                    {message_content}
                </div>
            </div>
            <div style="background: #111; padding: 15px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #333;">
                هذا الإيميل تم إنشاؤه تلقائياً بواسطة نظام Portfolio الخاص بك.
            </div>
        </div>
        """

        # 3. محاولة الإرسال عبر Resend API
        try:
            resend.api_key = os.environ.get('RESEND_API_KEY')

            resend.Emails.send({
                "from": "JooTech Portfolio <onboarding@resend.dev>",
                "to": ["jootech3@gmail.com"],
                "subject": f"🚀 {name}: {subject}",
                "html": html_content
            })
            messages.success(request, 'تم استلام رسالتك بنجاح، سأتواصل معك قريباً!')
        except Exception as e:
            # طباعة الخطأ في الكونسول لتتمكن من معرفة السبب الحقيقي
            print(f"Resend API Error Log: {e}")
            messages.warning(request, 'تم حفظ رسالتك، ولكن واجهنا مشكلة في إرسال التنبيه البريدي.')

        # توجيه المستخدم إلى قسم التواصل في الصفحة الرئيسية بعد الإرسال
        return redirect('/#contact')

    # توجيه أي شخص يحاول الدخول للرابط مباشرة إلى الصفحة الرئيسية
    return redirect('index')