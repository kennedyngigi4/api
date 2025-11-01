from django.core.management.base import BaseCommand
from apps.listings.models import ListingImage



class Command(BaseCommand):
    help = "Generate thumbnails for listing images"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of images to process (useful for batch processing).'
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        queryset = ListingImage.objects.filter(thumbnail__isnull=True).exclude(image__isnull=True)

        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ No images without thumbnails. All up to date."))
            return

        self.stdout.write(self.style.WARNING(f"Found {total} images without thumbnails."))

        for idx, img in enumerate(queryset, start=1):
            self.stdout.write(f"Processing {idx}/{total}: {img.image.name}")
            try:
                img.save()  # triggers your custom save() logic to regenerate watermark & thumbnail
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error processing {img.image.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 All missing thumbnails have been generated successfully."))

