from django.shortcuts import render, get_object_or_404,redirect
from .models import Project
from .models import Project, ContactMessage
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
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
        subject = request.POST.get('subject') or "رسالة جديدة من الموقع"
        message_content = request.POST.get('message')

        # 1. حفظ الرسالة في قاعدة البيانات (كما فعلت سابقاً)
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_content
        )

        # 2. إعداد محتوى الإيميل الذي سيصل إليك
        full_email_message = f"""
        لديك رسالة جديدة من: {name}
        البريد الإلكتروني للمرسل: {email}
        العنوان: {subject}
        
        نص الرسالة:
        {message_content}
        """

        # 3. إرسال الإيميل
        try:
            send_mail(
                subject=f"تنبيه: {subject}", # عنوان الإيميل الواصل إليك
                message=full_email_message,     # نص الإيميل
                from_email=settings.EMAIL_HOST_USER, 
                recipient_list=['1youseff777@gmail.com'], # بريدك الذي تريد استقبال الرسائل عليه
                fail_silently=False,
            )
        except Exception as e:
            # اختياري: يمكنك طباعة الخطأ في السيرفر إذا فشل الإرسال
            print(f"Error sending email: {e}")

        messages.success(request, 'تم إرسال رسالتك بنجاح! سأتواصل معك قريباً.')
        return redirect('contact')

    return render(request, 'contact.html')