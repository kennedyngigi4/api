from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.listings.models import *
from apps.listings.serializers.serializers import *
from apps.listings.serializers.dealer_serializers import *
# Create your views here.




def canUserUpload(userId):
    # 1. check if user is_partner
    user = User.objects.get(uid=userId)
    user_uploads = Listing.objects.filter(sold_by=user.uid).count()

    if user.is_partner and user_uploads < 100:
        return True, 'partner', None


    # 2. When Admin has activated FREE MODE
    free_mode = FreePostingMode.objects.first()
    if free_mode and free_mode.is_active:
        return True, 'free_mode', free_mode
    

    # 3. Subscription
    user_sub = Subscription.objects.filter(user=user).order_by("-start_date").first()
    if user_sub and user_sub.is_active():
        return True, "subscription", user_sub
    

    # 4. First time user free upload
    if user.free_limit < 1:
        return True, 'free_once', None
    

    # 5. Pay as you go option
    return False, 'pay', None




class uploadEligibilityCheckView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = request.user
        allowed, reason, extra = canUserUpload(user.uid) 

        response_data = {
            "can_upload": allowed,
            "reason": reason
        }

        if allowed:
            if reason == "subscription" and extra:
                response_data["message"] = "You have an active subscription."
                response_data["subscription"] = {
                    "package": extra.package.name,
                    "uploads_used": extra.uploads_used,
                    "uploads_allowed": extra.package.uploads_allowed,
                    "remaining_uploads": extra.package.uploads_allowed - extra.uploads_used
                }
            else:
                response_data["message"] = "You are eligible to upload a car."
        else:
            # get packages
            packages = Package.objects.filter().order_by("price")
            package_data = PackageSerializer(packages, many=True).data
            return Response({
                "can_upload": False,
                "reason": reason,
                "message": "You are not eligible to upload. Please choose a package.",
                "packages": package_data
            })
        return Response(response_data)


class VehicleUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        user = request.user
        print(request.data)
        serializer = ListingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({ 'success': False, 'message': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST})
        
        # Upload eligibility
        allowed, reason, extra = canUserUpload(user.uid)
        status_value = "published" if allowed else "draft" 


        listing = serializer.save(sold_by=user.uid, status=status_value)
        # force refresh from DB
        # listing.refresh_from_db()

        # Saving Images
        # images = request.FILES.getlist("images")
        # saved_images = []
        # for img in images:
        #     listing_image = ListingImage.objects.create(listing=listing, image=img)
        #     saved_images.append(ListingImageSerializer(listing_image).data)

        if allowed:
            if reason == "subscription":
                extra.uploads_used += 1
                listing.expires_at = timezone.now() + timedelta(days=extra.package.active_days)
                extra.save()

            elif reason == "free_mode":
                listing.was_free_post = True
                listing.expires_at = timezone.now() + timedelta(days=extra.post_duration)
                listing.save()

            elif reason == "free_once":
                user.free_limit += 1
                listing.expires_at = timezone.now() + timedelta(days=14)
                user.save() 
                

        return Response({
            'success': True,
            'message': "Published successfully!" if allowed else "Saved as draft. Please subscribe to publish",
            'published': listing.status,
            'payment_required': not allowed,
            'listing_id': listing.listing_id
        }, status=status.HTTP_201_CREATED)



class ListingImageUploadView(APIView):
    parser_classes = [ MultiPartParser, FormParser ]

    def post(self, request, *args, **kwargs):
        serializer = ListingImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DealerVehiclesList(generics.ListAPIView):
    permission_classes = [ IsAuthenticated]
    serializer_class = DealerVehicleListSerializer
    queryset = Listing.objects.all().prefetch_related("images").order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(sold_by=request.user.uid).exclude(availability="Sold")
        serializer = DealerVehicleListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)



class VehicleDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated]
    serializer_class = DealerVehicleDetailsSerializer
    queryset = Listing.objects.all().prefetch_related("images")
    lookup_field = "slug"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({ "success": True, "message": "Vehicle updated."}, status=status.HTTP_200_OK)


class VehicleDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [ IsAuthenticated, IsOwner ]
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()
    lookup_field = "slug"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({ "success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



class VehicleImageDeleteView(generics.DestroyAPIView):
    permission_classes = [ IsAuthenticated ]
    queryset = ListingImage.objects.all()
    serializer_class = ListingImageSerializer
    


class VehicleNewImagesView(APIView):
    permission_classes = [ IsAuthenticated ]
    parser_classes = [ MultiPartParser, FormParser ]


    def post(self, request, *args, **kwargs):
        listing_id = request.data.get("listing_id")
        images = request.FILES.getlist("images")

        if not listing_id and not images:
            return Response({ "success": False,  "message": "At least one image is required", "status": status.HTTP_400_BAD_REQUEST })
        
        listing = get_object_or_404(Listing, listing_id=listing_id)
        created_images = []

        for image in images:
            image_instance = ListingImage.objects.create(listing=listing, image=image)
            created_images.append(image_instance)

        serializer = ListingImageSerializer(created_images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class PriceHistoryView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PriceHistorySerializer
    queryset = PriceHistory.objects.all()



class PackagesView(generics.ListAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all().order_by("active_days")


class UploadSparePartsView(APIView):
    permission_classes = [ IsAuthenticated ]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = SparePartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({ "success": False, "error": "Invalid serializer" }, status=status.HTTP_400_BAD_REQUEST)

        
        # Checking eligibility
        allowed, reason, extra = canUserUpload(user.uid)
        status_value = "published" if allowed else "draft"

        spare = serializer.save(sold_by=user.uid, status=status_value)
        if allowed:
            if reason == "subscription":
                extra.uploads_used += 1
                spare.expires_at = timezone.now() + timedelta(days=extra.package.active_days)
                extra.save()
            
            elif reason == "free_mode":
                spare.free_post = True
                spare.expires_at = timezone.now() + timedelta(days=extra.post_duration)
                spare.save()

            elif reason == "free_once":
                user.free_limit += 1
                spare.expires_at = timezone.now() + timedelta(days=21)
                user.save()

       
        return Response({
            'success': True,
            'message': "Published successfully!" if allowed else "Saved as draft. Please subscribe to publish",
            'published': spare.status,
            'payment_required': not allowed,
            'id': spare.id
        }, status=status.HTTP_201_CREATED)


class SpareImagesUploadView(APIView):
    parser_classes = [ MultiPartParser, FormParser ]

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = PartImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DealerSparesListView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = SparePartSerializer
    queryset = SparePart.objects.all().order_by("-expires_at")

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(sold_by=request.user.uid)
        serializer = SparePartSerializer(queryset, many=True)
        return Response(serializer.data)


class SparesRetrieveEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ IsAuthenticated, IsOwner ]
    serializer_class = SparePartSerializer
    queryset = SparePart.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Update successful!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Update successful!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({ "success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



class DealerSpareDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = SparePartSerializer
    queryset = SparePart.objects.all()


    def get_object(self):
        instance = super().get_object()
        if instance.sold_by != self.request.user.uid:
            return Response({ "success": False, "message": "You must be the owner of the spare part"}, status=status.HTTP_400_BAD_REQUEST)
        return instance
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({ "success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


















