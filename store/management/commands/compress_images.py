"""
أمر ضغط كل الصور القديمة الموجودة على الموقع.

الاستخدام:
    python manage.py compress_images              # ضغط كل الصور (يحذف الأصلية بعد النجاح)
    python manage.py compress_images --keep       # ضغط مع الاحتفاظ بالصور الأصلية كنسخة احتياطية
    python manage.py compress_images --dry-run    # عرض ما سيحدث فقط بدون تنفيذ أي شيء

ماذا يفعل:
1. صور المشاريع (المسجلة في قاعدة البيانات): يحوّلها إلى WebP مضغوطة
   ويحدّث قاعدة البيانات تلقائياً — الموقع يعرضها فوراً بدون أي تعديل يدوي.
2. الصور الحرة في مجلد media/images (مثل صورة الهيرو): يضغطها في مكانها
   بنفس الاسم والصيغة حتى لا تنكسر أي روابط مكتوبة في القوالب.

آمن تماماً لإعادة التشغيل: الصور المضغوطة مسبقاً (WebP) يتم تخطيها.
"""
import os
from io import BytesIO

from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageOps

from store.models import ProjectImage, compress_image_to_webp, IMG_MAX_DIMENSION


def fmt_kb(size_bytes):
    return f"{size_bytes / 1024:.0f} KB"


class Command(BaseCommand):
    help = "ضغط كل صور الموقع (القديمة والحالية) تلقائياً"

    def add_arguments(self, parser):
        parser.add_argument('--keep', action='store_true',
                            help='الاحتفاظ بالملفات الأصلية بدل حذفها بعد الضغط')
        parser.add_argument('--dry-run', action='store_true',
                            help='عرض النتائج المتوقعة فقط بدون تعديل أي ملف')

    def handle(self, *args, **options):
        keep = options['keep']
        dry = options['dry_run']
        total_before = 0
        total_after = 0
        done = 0
        skipped = 0
        missing = 0

        self.stdout.write(self.style.MIGRATE_HEADING("== 1) صور المشاريع (قاعدة البيانات) =="))

        for pimg in ProjectImage.objects.all():
            name = pimg.image.name
            if name.lower().endswith('.webp'):
                skipped += 1
                self.stdout.write(f"  ⏭  متخطاة (مضغوطة بالفعل): {name}")
                continue

            storage = pimg.image.storage
            if not storage.exists(name):
                missing += 1
                self.stdout.write(self.style.WARNING(f"  ⚠  الملف غير موجود على السيرفر: {name}"))
                continue

            size_before = storage.size(name)

            with storage.open(name, 'rb') as f:
                try:
                    compressed = compress_image_to_webp(f)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✖  فشل ضغط {name}: {e}"))
                    continue

            if compressed is None:
                skipped += 1
                self.stdout.write(f"  ⏭  متخطاة (GIF متحرك): {name}")
                continue

            size_after = compressed.size
            # ذكاء إضافي: لو الضغط هيكبّر الملف (صور بسيطة مضغوطة أصلاً) نسيبه كما هو
            if size_after >= size_before:
                skipped += 1
                self.stdout.write(f"  ⏭  متخطاة (الأصلية أصغر بالفعل): {name}")
                continue

            total_before += size_before
            total_after += size_after
            saving = (1 - size_after / size_before) * 100 if size_before else 0

            if dry:
                self.stdout.write(
                    f"  🔍 {name}: {fmt_kb(size_before)} → {fmt_kb(size_after)} (توفير {saving:.0f}%)"
                )
                continue

            new_name = os.path.splitext(os.path.basename(name))[0] + '.webp'
            # save=False على الحقل ثم super().save يتجنب إعادة الضغط في ProjectImage.save
            pimg.image.save(new_name, compressed, save=False)
            super(ProjectImage, pimg).save(update_fields=['image'])

            if not keep:
                try:
                    storage.delete(name)
                except Exception:
                    pass

            done += 1
            self.stdout.write(self.style.SUCCESS(
                f"  ✔  {name}: {fmt_kb(size_before)} → {fmt_kb(size_after)} (توفير {saving:.0f}%)"
            ))

        # ---- 2) الصور الحرة في media/images (الهيرو، الأيقونة...) ----
        self.stdout.write(self.style.MIGRATE_HEADING("== 2) الصور الحرة في media/images =="))
        loose_dir = os.path.join(settings.MEDIA_ROOT, 'images')
        if os.path.isdir(loose_dir):
            for fname in sorted(os.listdir(loose_dir)):
                path = os.path.join(loose_dir, fname)
                ext = os.path.splitext(fname)[1].lower()
                if not os.path.isfile(path) or ext not in ('.jpg', '.jpeg', '.png'):
                    continue

                size_before = os.path.getsize(path)
                try:
                    img = Image.open(path)
                    img_format = img.format  # نحتفظ بنفس الصيغة حتى لا تنكسر الروابط
                    img = ImageOps.exif_transpose(img)
                    if img.mode == 'P':
                        img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')
                    elif img.mode == 'CMYK':
                        img = img.convert('RGB')
                    if max(img.size) > IMG_MAX_DIMENSION:
                        img.thumbnail((IMG_MAX_DIMENSION, IMG_MAX_DIMENSION), Image.LANCZOS)

                    buf = BytesIO()
                    if img_format == 'PNG':
                        img.save(buf, format='PNG', optimize=True)
                    else:
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        img.save(buf, format='JPEG', quality=82, optimize=True, progressive=True)
                    data = buf.getvalue()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✖  فشل ضغط {fname}: {e}"))
                    continue

                size_after = len(data)
                if size_after >= size_before:
                    skipped += 1
                    self.stdout.write(f"  ⏭  متخطاة (مضغوطة بالفعل بشكل جيد): {fname}")
                    continue

                total_before += size_before
                total_after += size_after
                saving = (1 - size_after / size_before) * 100

                if dry:
                    self.stdout.write(
                        f"  🔍 {fname}: {fmt_kb(size_before)} → {fmt_kb(size_after)} (توفير {saving:.0f}%)"
                    )
                    continue

                if keep:
                    backup = path + '.original'
                    if not os.path.exists(backup):
                        os.rename(path, backup)
                with open(path, 'wb') as out:
                    out.write(data)
                done += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  ✔  {fname}: {fmt_kb(size_before)} → {fmt_kb(size_after)} (توفير {saving:.0f}%)"
                ))
        else:
            self.stdout.write("  (مجلد media/images غير موجود — لا يوجد شيء هنا)")

        # ---- الملخص ----
        self.stdout.write(self.style.MIGRATE_HEADING("== الملخص =="))
        mode = "معاينة فقط (dry-run)" if dry else "تم التنفيذ"
        self.stdout.write(f"  الوضع: {mode}")
        self.stdout.write(f"  صور تمت معالجتها: {done if not dry else '—'} | متخطاة: {skipped} | مفقودة: {missing}")
        if total_before:
            total_saving = (1 - total_after / total_before) * 100
            self.stdout.write(self.style.SUCCESS(
                f"  الحجم الكلي: {fmt_kb(total_before)} → {fmt_kb(total_after)}"
                f"  (توفير {total_saving:.0f}%)"
            ))
