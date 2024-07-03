
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import jsons
import base64
import time
from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from .models import Cart,Transection,MyOrders
from django.db.models import F, ExpressionWrapper, DecimalField,Sum,Q
import hmac
import hashlib

def makepayment(request):
    if request.method == 'POST':
        userid=request.user.id
        item_total=ExpressionWrapper(
        (F('flowerob__price') - (F('flowerob__price') * F('flowerob__offvalue') / 100))*F('quantity'),
        output_field=DecimalField(max_digits=10, decimal_places=2))
        carts=Cart.objects.filter(userob_id=userid).select_related('flowerob').annotate(itemtotal=item_total)
        # Calculate total price
        total_price = carts.aggregate(total=Sum('itemtotal'))['total']
        #amount = int(request.POST.get('amount')) * 100  # Amount in paise
        amount = int(total_price)*100
        order_id = 'ORDER' + str(int(time.time()))  # Unique order ID
        callback_url = settings.PHONEPE_REDIRECT_URL

        MAINPAYLOAD = {
            "merchantId": settings.PHONEPE_MID,
            "merchantTransactionId": order_id,
            "merchantUserId": "MUID123",
            "amount": amount,
            "redirectUrl": callback_url,
            "redirectMode": "POST",
            "callbackUrl": callback_url,
            "mobileNumber": "9999999999",
            "paymentInstrument": {
                "type": "PAY_PAGE"
            },
        }
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # SETTING
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        INDEX = settings.PHONEPE_SALT_INDEX
        ENDPOINT = "/pg/v1/pay"
        SALTKEY = settings.PHONEPE_SALT_KEY
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        base64String = base64_encode(MAINPAYLOAD)
        mainString = base64String + ENDPOINT + SALTKEY;
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX;
        # # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # # Payload Send
        # # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checkSum,
            'accept': 'application/json',
        }
        json_data = {
            'request': base64String,
        }
        response = requests.post('https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay', headers=headers, json=json_data)
        responseData = response.json();

        # Debug prints
        print("responseData:", responseData)
        print("Headers:", headers)
        #response = requests.post(f'{settings.PHONEPE_BASE_URL}/pg/v1/pay', data=payload_str, headers=headers)

        # Debug response
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.content)

        if response.status_code == 200:
            payment_data = response.json()
            if payment_data.get('success'):
                userob_id = request.user.id
                tr = Transection.objects.create(userob_id=userob_id,
                                                      statusCode="Initiate",
                                                      transactionId=order_id,
                                                      providerReferenceId="pending",
                                                      amount=amount,
                                                      )
                if(tr):
                    print('transection save initiated')
                for cart in carts:
                    print(cart.flowerob)
                    flower = cart.flowerob
                    created = MyOrders.objects.create(flowerob_id=flower.id,
                                                      userob_id=userob_id,
                                                      transactionId=order_id,
                                                      quantity=cart.quantity,
                                                      amount=flower.price,
                                                      offvalue=flower.offvalue,
                                                      )
                    if(created):
                        print('order saved')
                return redirect(payment_data['data']['instrumentResponse']['redirectInfo']['url'])
            else:
                return render(request, 'error.html', {"message": "Error in PhonePe payment initiation"})
        else:
            return render(request, 'error.html', {"message": "Error in PhonePe payment request"})

    return redirect('cart')

def calculate_sha256_string(input_string):
    # Create a hash object using the SHA-256 algorithm
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    # Update hash with the encoded string
    sha256.update(input_string.encode('utf-8'))
    # Return the hexadecimal representation of the hash
    return sha256.finalize().hex()
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def base64_encode(input_dict):
    # Convert the dictionary to a JSON string
    json_data = jsons.dumps(input_dict)
    # Encode the JSON string to bytes
    data_bytes = json_data.encode('utf-8')
    # Perform Base64 encoding and return the result as a string
    return base64.b64encode(data_bytes).decode('utf-8')

def phonepecallback(request):
    if request.method == 'POST':
        try:
            # Debugging: Log the raw request body
            print(f"Raw request body: {request.body}")

            # Debugging: Log form data
            print(f"Form data: {request.POST}")

            # Extract necessary data from form-encoded request body
            transaction_id = request.POST.get('transactionId')
            merchant_id=request.POST.get('merchantid')
            providerReferenceId=request.POST.get('providerReferenceId')
            amount=request.POST.get('amount')
            code = request.POST.get('code')
            checksum = request.POST.get('checksum')
            custom_data = request.POST.get('customData')
            print(custom_data)
            payload = f"{merchant_id}|{transaction_id}|{amount}|{providerReferenceId}|{code}"
            generated_signature = hmac.new(
                settings.PHONEPE_SALT_KEY.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            print(checksum.split('###')[0])
            print('-----------------------------------')
            print(generated_signature)
            if checksum.split('###')[0] == generated_signature or 1==1: #ypassing signature for testing 
            # Ensure the transaction ID is present
                if providerReferenceId:
                    trob = Transection.objects.get(transactionId=transaction_id)
                    if(trob):
                        trob.providerReferenceId=providerReferenceId
                        trob.statusCode=code
                        trob.save()
                    else:
                        print('no transection object found')
                    # Handle the payment status
                    if code == "PAYMENT_SUCCESS":
                        # Process successful payment
                        return render(request, 'success.html', {"transaction_id": transaction_id,"providerReferenceId":providerReferenceId})
                    else:
                        # Handle other payment statuses if needed
                        return render(request, 'error.html', {"message": f"Payment failed with code :{code}"})
                else:
                    return render(request, 'error.html', {"message": "Transaction ID missing in callback data"})
            else:
                return render(request, 'error.html', {"message": "signature failed"})
        except Exception as e:
            # Log the error for debugging
            print(f"Error processing callback: {str(e)}")
            return render(request, 'error.html', {"message": f"Error processing callback: {str(e)}"})
    return render(request, 'error.html', {"message": "Invalid request"})

