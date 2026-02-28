from django.shortcuts import render, get_object_or_404,redirect
from .models import Project
from .models import Project, ContactMessage
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
def index(request):
    projects = Project.objects.filter(is_published=True).prefetch_related('images').order_by('-created_at')
    context = {
        'projects': projects,
        'total_projects': projects.count(),
    }
    return render(request, 'index.html', context)

def project(request):
    projects = Project.objects.filter(is_published=True).prefetch_related('images').order_by('-created_at')
    context = {
        'projects': projects,
        'total_projects': projects.count(),
    }
    return render(request, 'projects.html', context)

def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('images'), 
        pk=pk, 
        is_published=True
    )
    return render(request, 'project_detail.html', {'project': project})
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone') # الحقل الجديد
        subject = request.POST.get('subject') or "طلب جديد من الموقع"
        message_content = request.POST.get('message')

        # 1. حفظ الرسالة في قاعدة البيانات
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_content
        )

        # 2. إعداد محتوى الإيميل بتنسيق HTML احترافي
        html_content = f"""
        <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; border: 1px solid #00f3ff; border-radius: 15px; overflow: hidden; background-color: #030305; color: #ffffff;">
            <div style="background: linear-gradient(90deg, #00f3ff, #bc13fe); padding: 20px; text-align: center;">
                <h2 style="margin: 0; color: #000; letter-spacing: 2px;">رسالة جديدة من الموقع</h2>
            </div>
            <div style="padding: 30px; line-height: 1.6;">
                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px;">👤 <strong>بيانات المرسل:</strong></p>
                <p><strong>الاسم:</strong> {name}</p>
                <p><strong>البريد:</strong> <a href="mailto:{email}" style="color: #00f3ff;">{email}</a></p>
                <p><strong>الهاتف:</strong> <a href="tel:{phone}" style="color: #00f3ff;">{phone}</a></p>
                
                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 25px;">📝 <strong>موضوع الرسالة:</strong></p>
                <p>{subject}</p>

                <p style="font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 25px;">💬 <strong>نص الرسالة:</strong></p>
                <div style="background: #111; padding: 15px; border-radius: 8px; border-right: 4px solid #00f3ff;">
                    {message_content}
                </div>
            </div>
            <div style="background: #111; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                تم إرسال هذه الرسالة تلقائياً من نظام الموقع الخاص بك.
            </div>
        </div>
        """
        
        text_content = strip_tags(html_content) # نسخة نصية احتياطية

        # 3. إرسال الإيميل الاحترافي
        try:
            msg = EmailMultiAlternatives(
                subject=f"🚀 {name} - {subject}",
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['1youseff777@gmail.com'],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            print(f"Error: {e}")

        messages.success(request, 'تم استلام رسالتك بنجاح، شكراً لتواصلك!')
        return redirect('contact')

    return render(request, 'contact.html')