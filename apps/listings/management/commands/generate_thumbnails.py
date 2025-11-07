from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.listings.models import ListingImage
from PIL import Image
from io import BytesIO
import os

class Command(BaseCommand):
    help = "Regenerate thumbnails from existing blurred listing images (ignore existing thumbnails)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of images to process (useful for batch processing).'
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        queryset = ListingImage.objects.exclude(image__isnull=True)

        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ No listing images found to process."))
            return

        THUMB_SIZE = (600, 400)
        self.stdout.write(self.style.WARNING(f"Found {total} images. Regenerating thumbnails..."))

        for idx, img in enumerate(queryset, start=1):
            try:
                self.stdout.write(f"Processing {idx}/{total}: {img.image.name}")

                # Open existing image (already blurred/watermarked)
                image = Image.open(img.image)
                image = image.convert("RGB")

                # Resize to thumbnail
                thumb = image.copy()
                thumb.thumbnail(THUMB_SIZE)

                # Save thumbnail to buffer
                thumb_buffer = BytesIO()
                thumb.save(thumb_buffer, format="JPEG", quality=85, optimize=True, progressive=True)
                thumb_buffer.seek(0)

                # Generate filename and save
                base, _ = os.path.splitext(os.path.basename(img.image.name))
                thumb_name = base.replace(" ", "_") + "_thumb.jpg"

                img.thumbnail.save(thumb_name, ContentFile(thumb_buffer.read()), save=False)
                img.save(update_fields=["thumbnail"])

                self.stdout.write(self.style.SUCCESS(f"✅ Thumbnail regenerated for {img.image.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error processing {img.image.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 All thumbnails regenerated successfully."))
