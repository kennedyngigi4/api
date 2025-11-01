import os
from celery import Celery, shared_task
from datetime import timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from celery import shared_task
from apps.accounts.models import User, UserBusiness


@shared_task
def process_listing_image(image_id):
    from apps.listings.models import ListingImage
    from apps.accounts.models import User, UserBusiness  # adjust if paths differ

    try:
        instance = ListingImage.objects.get(pk=image_id)
    except ListingImage.DoesNotExist:
        return

    if not instance.image:
        return

    # ---- Get business name ----
    try:
        sold_by = instance.listing.sold_by
        user = User.objects.get(uid=sold_by)
        business = UserBusiness.objects.get(user=user)
        business_name = business.name.upper()
    except Exception:
        business_name = "KENAUTOS VERIFIED"

    # ---- Open image ----
    img = Image.open(instance.image).convert("RGBA")

    MASTER_SIZE = (1200, 800)
    THUMB_SIZE = (600, 400)

    # Determine if first image
    is_first = not ListingImage.objects.filter(
        listing=instance.listing
    ).exclude(pk=instance.pk).exists()

    img.thumbnail(MASTER_SIZE, Image.LANCZOS)

    # ---- Prepare background ----
    if is_first:
        canvas = Image.new("RGBA", MASTER_SIZE, (255, 255, 255, 255))
        x = (MASTER_SIZE[0] - img.width) // 2
        y = (MASTER_SIZE[1] - img.height) // 2
        canvas.paste(img, (x, y), img)
    else:
        bg = img.copy().convert("RGB")
        bg = bg.resize(MASTER_SIZE, Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(20))
        canvas = bg.convert("RGBA")
        x = (canvas.width - img.width) // 2
        y = (canvas.height - img.height) // 2
        canvas.paste(img, (x, y), img)

    # ---- Add watermark ----
    line1 = "POSTED ON KENAUTOS"
    line2 = business_name

    watermark_layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/open_sans.ttf")
    if not os.path.exists(font_path):
        font1 = font2 = ImageFont.load_default()
    else:
        font1 = ImageFont.truetype(font_path, max(int(min(img.size) * 0.04), 24))
        font2 = ImageFont.truetype(font_path, max(int(min(img.size) * 0.07), 24))

    bbox1 = draw.textbbox((0, 0), line1, font=font1)
    bbox2 = draw.textbbox((0, 0), line2, font=font2)
    text1_w, text1_h = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
    text2_w, text2_h = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]

    total_height = text1_h + text2_h + 25
    center_x = canvas.width // 2
    start_y = (canvas.height - total_height) // 2

    draw.text(
        (center_x - text1_w // 2, start_y),
        line1, font=font1, fill=(0, 0, 0, 80),
        stroke_width=2, stroke_fill=(255, 255, 255, 120)
    )
    draw.text(
        (center_x - text2_w // 2, start_y + text1_h + 25),
        line2, font=font2, fill=(0, 0, 0, 80),
        stroke_width=2, stroke_fill=(255, 255, 255, 120)
    )

    final = Image.alpha_composite(canvas, watermark_layer).convert("RGB")

    # ---- Save processed main image ----
    buffer = BytesIO()
    final.save(buffer, format="JPEG", quality=88, optimize=True, progressive=True)
    buffer.seek(0)

    base, _ = os.path.splitext(os.path.basename(instance.image.name))
    file_name = base.replace(" ", "_") + ".jpg"
    instance.image.save(file_name, ContentFile(buffer.read()), save=False)

    # ---- Generate and save thumbnail ----
    thumb = final.copy()
    thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
    thumb_buffer = BytesIO()
    thumb.save(thumb_buffer, format="JPEG", quality=85, optimize=True, progressive=True)
    thumb_buffer.seek(0)

    thumb_name = base.replace(" ", "_") + "_thumb.jpg"
    instance.thumbnail.save(thumb_name, ContentFile(thumb_buffer.read()), save=False)

    # ---- Update listing thumbnail if first ----
    if is_first and hasattr(instance.listing, "thumbnail_image"):
        instance.listing.thumbnail_image = instance.thumbnail
        instance.listing.save(update_fields=["thumbnail_image"])

    # ---- Final save + force DB sync ----
    instance.save()
    instance.refresh_from_db()

    # Debug
    print("✅ Thumbnail saved:", instance.thumbnail.url if instance.thumbnail else "❌ Missing")


@shared_task
def deactivate_expired_listings():
    from apps.listings.models import Listing, Auction

    now = timezone.now()
    expired_listings = Listing.objects.filter(expires_at__lte=now, status="published")
    for listing in expired_listings:
        listing.status = "expired"
        listing.save()



@shared_task
def update_auction_status():
    from apps.listings.models import Listing, Auction
    
    now = timezone.now()

    # set to live
    live_auctions =  Auction.objects.filter(
        status="upcoming",
        start_time__lte=now,
        end_time__gt=now
    )
    live_auctions.update(status="live")

    for auction in live_auctions.select_related("vehicle"):
        if auction.vehicle:
            auction.vehicle.display_type = "auction"
            auction.vehicle.save(update_fields=["display_type"])


    # Set to ended
    ended_auctions = Auction.objects.filter(
        status="live",
        end_time__lte=now
    )
    ended_auctions.update(status="ended")

    for auction in ended_auctions.select_related("vehicle"):
        if auction.vehicle:
            auction.vehicle.display_type = ""
            auction.vehicle.save(update_fields=["display_type"])
