from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from twilio.twiml.messaging_response import MessagingResponse

from apps.listings.models import Listing, ListingImage, SparePart
from apps.whatsappbot.models import ConversationState
from apps.whatsappbot.services import send_text
# Create your views here.


@csrf_exempt
@api_view(["POST"])
def whatsapp_webhook(request):
    from_number = request.POST.get("From")
    body = request.POST.get("Body", "").strip().lower()
    button_id = request.POST.get("ButtonId")
    num_media = int(request.POST.get("NumMedia", 0))
    media_urls = [request.POST.get(f"MediaUrl{i}") for i in range(num_media)]

    state, _ = ConversationState.objects.get_or_create(phone=from_number)
    step = state.step
    data = state.temp_data


    # 1. New conversation -> show main menu
    if step == 0 and not button_id:
        state.step = 1
        state.save()
        message = (
            "👋 Welcome to KENAUTOS! What would you like to do today?\n"
            "1️⃣ Sell Vehicle 🚗\n"
            "2️⃣ Sell Spare Parts 🔧\n"
            "3️⃣ Hire a Vehicle 🚙"
            "\n\n"
            "Answer with either 1, 2 or 3"
        )
        send_text(from_number, message)
        return Response({"status": "initial_menu_sent"}, status=200)

    # 2. Handle main menu selection
    if state.step == 1:
        if body in ["1", "sell vehicle"]:
            message = (
                "What type of vehicle are you selling?\n"
                "1️⃣ Car\n"
                "2️⃣ Bike\n"
                "3️⃣ Truck"
                "\n\n"
                "Answer with either 1, 2 or 3"
            )
            state.flow = "sell_vehicle"
            state.step = 2
            state.save()
            send_text(from_number, message)
            return Response({"status": "vehicle_menu_sent"}, status=200)
        


        
        elif body in ["2", "sell spare parts"]:
            message = (
                "Which type of *spare parts* are you selling?\n"
                "1️⃣ Audio Parts\n"
                "2️⃣ Brakes, Suspension & Steering\n"
                "3️⃣ Engine & Drivetrain\n"
                "4️⃣ Exterior Accessories\n"
                "5️⃣ Headlights & Lightings\n"
                "6️⃣ Interior Accessories\n"
                "7️⃣ Wheels & Parts\n"
                "\n"
                "Answer with either 1, 2, 3 or ...."
            )
            state.flow = "sell_spare"
            state.step = 2
            state.save()
            send_text(from_number, message)
            return Response({"status": "spares_menu_sent"}, status=200)
        
        elif body in ["3", "hire a vehicle"]:
            message = (
                "Which vehicle would you like to hire?\n"
                "(Please note its chauffered services only.)"
            )
            state.flow = "car_hire"
            state.step = 2
            state.save()
            send_text(from_number, message)
            return Response({"status": "car_hire_menu_sent"}, status=200)
        else:
            # invalid input, resend same menu
            send_text(from_number, "❌ Invalid choice. Please reply with 1, 2 or 3.")
            return Response({"status": "invalid_input"}, status=400)




    # Step 3: vehicle type for (sell_vehicle)
    if state.flow == "sell_vehicle" and step == 2:
        if body in ["1", "car"]:
            data["vehicle_type"] = "car"
        elif body in ["2", "bike"]:
            data["vehicle_type"] = "bike"
        elif body in ["3", "truck"]:
            data["vehicle_type"] = "truck"
        else:
            send_text(from_number, "❌ Invalid choice. Please reply with 1, 2 or 3.")
            return Response({"status": "invalid_vehicle_type"}, status=400)

        state.step = 3
        state.temp_data = data
        state.save()
        send_text(from_number, "Please enter the vehicle *Yom* *Make* *Model* (e.g. 2018 Toyota Probox).")    
        return Response({"status": "ask_make"}, status=200)
    

    # Step 4. yom make and model
    if state.flow == "sell_vehicle" and step == 3:
        data["yom_make_model"] = body.title()
        state.step = 4
        state.temp_data = data
        state.save()    
        send_text(from_number, "What's the selling *Price in KES*?")
        return Response({"status": "ask_price"}, status=200)
    

    # Step 5: Price captutring
    if state.flow == "sell_vehicle" and step == 4:
        if body.replace(",", "").isdigit():
            data["price"] = int(body.replace(",", ""))  
            state.step = 5
            state.temp_data = data
            state.save()
            send_text(from_number, "Please upload 3 images of the vehicle 📸.")
            return Response({"status": "ask_images"}, status=200)
        else:
            send_text(from_number, "❌ Please enter a valid number for the price.")
            return Response({"status": "invalid_price"}, status=400)


    # Step. 6 Capture Images
    if state.flow == "sell_vehicle" and step == 5:
        if num_media > 0:
            existing_imgs = data.get("images", [])
            existing_imgs.extend(media_urls)
            data["images"] = existing_imgs

            if len(existing_imgs) >= 3:
                state.step = 6
                state.temp_data = data
                state.save()
                summary = (
                    "✅ Please confirm your details:\n"
                    f"- Type: {data.get('vehicle_type')}\n"
                    f"- Yom Make & Model: {data.get('yom_make_model')}\n"
                    f"- Price: {data.get('price')} KES\n"
                    f"- Images: {len(existing_imgs)} received\n\n"
                    "Reply with 1 to Submit or 2 to Cancel."
                )

                send_text(from_number, summary)
                return Response({"status": "review_details"}, status=200)
            else:
                state.temp_data = data
                state.save()
                send_text(from_number, f"{len(existing_imgs)}/3 images received. Please upload the remaining.")
                return Response({"status": "waiting_images"}, status=200)
        else:
            send_text(from_number, "❌ Please attach at least 1 image.")
            return Response({"status": "no_image"}, status=400)
        

    # 🟢 Step 7: Final confirmation
    if state.flow == "sell_vehicle" and step == 6:
        if body == "1":
            # TODO: Save listing in DB (Listing.objects.create(...))
            send_text(from_number, "🎉 Your vehicle has been submitted successfully!")
            state.delete()
            return Response({"status": "submitted"}, status=200)
        elif body == "2":
            send_text(from_number, "❌ Listing cancelled.")
            state.delete()
            return Response({"status": "cancelled"}, status=200)
        else:
            send_text(from_number, "Please reply with 1 to Submit or 2 to Cancel.")
            return Response({"status": "retry_confirmation"}, status=400)




    # Sell Spares
    if state.flow == "sell_spare" and step == 2:
        if body in ["1", "Audio Parts"]:
            data["spare_type"] = "Audio Parts"
        elif body in ["2", "Brakes, Suspension & Steering"]:
            data["spare_type"] = "Brakes, Suspension & Steering"
        elif body in ["3", "Engine & Drivetrain"]:
            data["spare_type"] = "Engine & Drivetrain"
        elif body in ["4", "Exterior Accessories"]:
            data["spare_type"] = "Exterior Accessories"
        elif body in ["5", "Headlights & Lightings"]:
            data["spare_type"] = "Headlights & Lightings"
        elif body in ["6", "Interior Accessories"]:
            data["spare_type"] = "Interior Accessories"
        elif body in ["7", "Wheels & Parts"]:
            data["spare_type"] = "Wheels & Parts"
        else:
            send_text(from_number, "❌ Invalid choice. Please reply with 1, 2, 3 or ...")
            return Response({"status": "invalid_spare_type"}, status=400)


        state.step = 3
        state.temp_data = data
        state.save()

        send_text(from_number, "Please enter the name/title of the part.")
        return Response({"status": "ask_spare_name"}, status=200)
        
    if state.flow == "sell_spare" and step == 3:
            data["spare_name"] = body.title()
            state.step = 4
            state.temp_data = data
            state.save()

            send_text(from_number, "Which car make and model does the spare part serve?\n\n (e.g Mazda Demio)")
            return Response({"status": "ask_spare_make_model"}, status=200)
        
    if state.flow == "sell_spare" and step == 4:
            data["make_model"] = body.title()
            state.step = 5
            state.temp_data = data
            state.save()

            send_text(from_number, "What's the selling *Price in KES*?")
            return Response({"status": "ask_price"}, status=200)
        
    if state.flow == "sell_spare" and step == 5:
            if body.replace(",","").isdigit():
                data["price"] = int(body.replace(",",""))
                state.step = 6
                state.temp_data = data
                state.save()

                send_text(
                    from_number, 
                    "What's it's condition? \n"
                    "1 Brand New\n"
                    "2 Refurbished\n"
                    "3 Used\n"
                    "\n"
                    "Answer with 1, 2 or 3"
                )
                return Response({ "status", "ask_condition"}, status=200)
            else:
                send_text(from_number, "❌ Please enter a valid number")
                return Response({"status":"invalid_price"}, status=400)
            
    if state.flow == "sell_spare" and step == 6:
            if body in ["1", "brand new"]:
                data["condition"] = "brand new"
            elif body in ["2", "refurbished"]:
                data["condition"] = "refurbished"
            elif body in ["3", "used"]:
                data["condition"] = "used"
            else:
                send_text(from_number, "❌ Invalid choice. Please reply with 1, 2 or 3.")
                return Response({"status", "invalid_spare_condition"}, status=400)
            
            state.step = 7
            state.temp_data = data
            state.save()
            send_text(from_number, "Please upload at least 1 image of the spare part 📸.")

    if state.flow == "sell_spare" and step == 7:
            if num_media > 0:
                existing_imgs = data.get("images", [])
                existing_imgs.extend(media_urls)
                data["images"] = existing_imgs

                if len(existing_imgs) >= 1:
                    state.step = 8
                    state.temp_data = data
                    state.save()
                    summary = (
                        "✅ Please confirm your details:\n"
                        f"- Type: {data.get('spare_type')}\n"
                        f"- Name: {data.get('spare_name')}\n"
                        f"- Car Make & Model: {data.get('make_model')}\n"
                        f"- Price: {data.get('price')}\n"
                        f"- Condition: {data.get('condition')}\n"
                        f"- Images: {len(existing_imgs)} received \n\n"
                        "Reply with 1 to submit or 2 to cancel."
                    )
                    send_text(from_number, summary)
                    return Response({"status", "review_details"}, status=200)
                else:
                    state.temp_data = data
                    state.save()
                    send_text(from_number, f"{len(existing_imgs)} images received. Please upload the remaining.")
                    return Response({"status": "waiting_images"}, status=200)
            else:
                send_text(from_number, "❌ Please attach at least 1 image.")
                return Response({"status": "no_image"}, status=400)
            
    if state.flow == "sell_spare" and step == 8:
            if body == "1":
                # TODO: Save listing in DB (Listing.objects.create(...))
                send_text(from_number, "🎉 Your spare part has been submitted successfully!")
                state.delete()
                return Response({"status": "submitted"}, status=200)
            elif body == "2":
                send_text(from_number, "❌ Listing cancelled.")
                state.delete()
                return Response({"status": "cancelled"}, status=200)
            else:
                send_text(from_number, "Please reply with 1 to Submit or 2 to Cancel.")
                return Response({"status": "retry_confirmation"}, status=400)
    # # Default fallback
    return Response({"status": "no_match"}, status=200)



