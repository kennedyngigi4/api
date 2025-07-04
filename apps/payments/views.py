import requests
import base64
import json
from requests.auth import HTTPBasicAuth
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import *
from apps.listings.models import *
from apps.payments.models import *
# Create your views here.



class MPesa:
    def __init__(self, phone, amount, reference):
        self.consumer_key = "CoekQiy5PmUdgRJtRKyCoV9WB3pMWj6cabG1lWP2H6XllhHB"
        self.consumer_secret = "sksJnGakoPJdNFFuoLsXbs7AyLCVFpyAQ9SrspTdG6EzeIVvANFTjwtYCjuoNdlk"
        self.authorization_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.phone = phone
        self.amount = amount
        self.reference = reference


    def generateCredentials(self):
        auth = requests.get(self.authorization_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        response = json.loads(auth.text)
        access_token = response["access_token"]
        return access_token


    def LipaNow(self):
        lipa_time = datetime.now().strftime("%Y%m%d%H%M%S")
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        data_to_encode = business_short_code + passkey + lipa_time
        online_password = base64.b64encode(data_to_encode.encode())
        decode_password = online_password.decode("utf-8")

        context = {
            "lipa_time": lipa_time,
            "business_short_code": business_short_code,
            "decode_password": decode_password
        }

        return context


    def MpesaSTKPush(self):
        access_token = self.generateCredentials()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        payload = {
            "BusinessShortCode": self.LipaNow()['business_short_code'],
            "Password": self.LipaNow()['decode_password'],
            "Timestamp": self.LipaNow()['lipa_time'],
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": int(self.amount),
            "PartyA": self.phone,  # replace with your phone number to get stk push
            "PartyB": self.LipaNow()['business_short_code'],
            "PhoneNumber": self.phone,  # replace with your phone number to get stk push
            "CallBackURL": "https://kenautos.co.ke/api/payments/mpesa_callback/",
            "AccountReference": self.reference,
            "TransactionDesc": "KENAUTOS HUB"
        }
        response = requests.post(api_url, json=payload, headers=headers)
        return response
        
    



class SubscriptionPurchase(APIView):

    def post(self, request):
        print(request.data)
        try:
            selected_package = Package.objects.get(pid=request.data["package"])
            mpesa_req = MPesa(request.data["phone"], selected_package.price, request.data["package"]).MpesaSTKPush()
            
            if mpesa_req.status_code == 200:
                data = mpesa_req.json()
                req =  PaymentRequest.objects.create(
                    owner=self.request.user.uid,
                    package=request.data["package"],
                    checkout_request_id=data["CheckoutRequestID"],
                    merchant_request_id=data["MerchantRequestID"],
                    vehicle=request.data["vehicleid"],
                )
                req.save()
                return Response({ "success": True}, status=status.HTTP_200_OK)
            
            else:
                error = mpesa_req.json()
                return Response({ "success": False, "error": error}, status=400)
        
        except Package.DoesNotExist:
            return Response({ "success": False, "error": "Invalid package" }, status=400)

       

class PaymentView(APIView):

    def post(self, request, callback_data=None):
     
        data = callback_data or request.data
        callback = data.get("Body", {}).get("stkCallback", {})
        result_code = callback.get("ResultCode")
        checkout_id = callback.get("CheckoutRequestID")

        if result_code != 0:
            return Response({ "success": False, "error": "Payment failed or cancelled" }, status=400)


        try:
            payment_req = PaymentRequest.objects.get(checkout_request_id=checkout_id)
        except PaymentRequest.DoesNotExist:
            return Response({ "success": False, "error": "Pending payment not found"}, status=404)
        
        try:
            with transaction.atomic():

                # Create Subscription
                user = User.objects.get(uid=payment_req.owner)
                package = Package.objects.get(pid=payment_req.package)
                subscription = Subscription.objects.create(
                    user=user,
                    package=package,
                )
                

                items = callback.get("CallbackMetadata", {}).get("Item", [])
                metadata = {item["Name"]: item.get("Value") for item in items}
                amount = metadata.get("Amount")
                phone = metadata.get("PhoneNumber")
                transaction_id = metadata.get("MpesaReceiptNumber")
                transaction_date = metadata.get("TransactionDate")


                # Create Payment Record
                mpesa_payment = Payment.objects.create(
                    transaction_id=transaction_id,
                    amount=amount,
                    phone=phone,
                    transaction_date=transaction_date,
                    paid_by=user.uid,
                    subscription=subscription.subscription_id
                )

                # Activate the primary car selected for publishing
                if payment_req.vehicle:
                    try:
                        vehicle = Listing.objects.get(listing_id=payment_req.vehicle)
                        vehicle.status = "published"
                        vehicle.updated_at = datetime.now()
                        vehicle.save()

                        subscription.uploads_used += 1
                        subscription.save()
                    except:
                        return Response({
                            "success": False,
                            "error": "Not a vehicle update"
                        }, status=status.HTTP_404_NOT_FOUND)

                


                return Response({ "success": True, "message": "Payment successful."}, status=status.HTTP_200_OK)
        
        except IntegrityError as e:
            return Response({
                "success": False,
                "error": "Database integrity error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({
                "success": False,
                "error": "Unexpected error during payment",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



