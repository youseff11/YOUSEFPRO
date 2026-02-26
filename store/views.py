from django.shortcuts import render, get_object_or_404,redirect
from .models import Project
from .models import Project, ContactMessage
from django.contrib import messages

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
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # حفظ الرسالة في قاعدة البيانات
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # إضافة رسالة نجاح تظهر للمستخدم
        messages.success(request, 'تم إرسال رسالتك بنجاح! سأتواصل معك قريباً.')
        return redirect('contact') # تأكد من اسم الـ url

    return render(request, 'contact.html')