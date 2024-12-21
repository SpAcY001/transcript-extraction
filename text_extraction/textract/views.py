from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
from .models import UploadedFile
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from django.contrib import messages
import boto3
from django.core.exceptions import ObjectDoesNotExist
from botocore.exceptions import ClientError
import time
from dotenv import load_dotenv
load_dotenv()
from django.conf import settings
import os
from .models import Contract
from .serializers import ContractSerializer
from openai import OpenAI
from pathlib import PurePosixPath
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.views.decorators.clickjacking import xframe_options_exempt
from .extract_2 import extract_text_from_pdf,extract_results
os.environ['OPENAI_API_KEY']='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'
@csrf_exempt
def list_contracts(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'  # Adjust as necessary
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'  # Specify allowed headers
        return response
    print("contracts list called")
    if request.method == 'GET':
        contracts = Contract.objects.all()
        contracts_list = [{'id': contract.id, 'name': contract.name, 'prompt': contract.prompt, 'description': contract.description} for contract in contracts]
        return JsonResponse({'contracts': contracts_list})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
@ensure_csrf_cookie
def set_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})
from rest_framework.decorators import api_view

@api_view(['GET'])
def auth_status(request):
    """
    View to check user's authentication status and username.
    """
    # return JsonResponse({
    #     'isAuthenticated': False,
    #     'username': 'DebugUser'
    # })
    if request.method == 'OPTIONS':
        # Prepare response for OPTIONS request
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'  # Adjust as necessary
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'  # Specify allowed headers
        return response
    print("auth_status")
    if request.method == 'GET':
        if request.user.is_authenticated:
            # User is authenticated
            print(JsonResponse({
                'isAuthenticated': True,
                'username': request.user.username  # Or any other user attribute
            }))
            return JsonResponse({
                'isAuthenticated': True,
                'username': request.user.username  # Or any other user attribute
            })
        else:
            # User is not authenticated
            return JsonResponse({'isAuthenticated': False,'username': 'Anonymous'})
    



def py_path(win_path):
    python_path = "" # The result of this script.
    # Convert to ASCII list
    ascii_values_list = []
    for character in win_path:
        ascii_values_list.append(ord(character))
    # Replace all ASCII values for "\" (=92) with value for "/" (=47).
    for i in range(0, len(ascii_values_list)):
        if ascii_values_list[i] == 92:
            ascii_values_list[i] = 47
    path_py = "" # Convert ASCII list to string
    for val in ascii_values_list:
        path_py = path_py + chr(val)

    if path_py[-1] != "/": # Add "/" at end of path if needed.
        path_py = path_py + "/"
    path_py+='text_extraction'    
    return path_py
# def start_job(client, s3_bucket_name, object_name):
#     response = None
#     response = client.start_document_text_detection(
#         DocumentLocation={
#             'S3Object': {
#                 'Bucket': s3_bucket_name,
#                 'Name': object_name
#             }}
#     )

#     return response["JobId"]

# def is_job_complete(client, job_id):
#     time.sleep(1)
#     response = client.get_document_text_detection(JobId=job_id)
#     status = response["JobStatus"]
#     # print("Job status: {}".format(status))

#     while(status == "IN_PROGRESS"):
#         time.sleep(1)
#         response = client.get_document_text_detection(JobId=job_id)
#         status = response["JobStatus"]
#         # print("Job status: {}".format(status))

#     return status

# def get_job_results(client, job_id):
#     pages = []
#     time.sleep(1)
#     response = client.get_document_text_detection(JobId=job_id)
#     pages.append(response)
#     print("Resultset page received: {}".format(len(pages)))
#     next_token = None
#     if 'NextToken' in response:
#         next_token = response['NextToken']

#     while next_token:
#         time.sleep(1)
#         response = client.get_document_text_detection(JobId=job_id, NextToken=next_token)
#         pages.append(response)
#         print("Resultset page received: {}".format(len(pages)))
#         next_token = None
#         if 'NextToken' in response:
#             next_token = response['NextToken']

#     return pages
# # def extract_text_from_pdf(pdf_file,gpt=False):

#     doc_path=pdf_file
#     file=pdf_file.split('/')[-1]
#     # print(file)
#     s3_bucket_name="textextractbucket17"
#     s3_client = boto3.client('s3',aws_access_key_id='AKIA4MTWLND6TG4GPBYZ',aws_secret_access_key='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')
#     try:
#         response = s3_client.upload_file(Filename=doc_path, Bucket=s3_bucket_name, Key=file)
#     except ClientError as e:
#         print(e)
    
#     client = boto3.client('textract',region_name='eu-west-1',aws_access_key_id='AKIA4MTWLND6TG4GPBYZ',aws_secret_access_key='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')
    
#     job_id = start_job(client, s3_bucket_name, file)
#     # print("Started job with id: {}".format(job_id))
#     print('Processing files...')
#     if is_job_complete(client, job_id):
#         response = get_job_results(client, job_id)

#     # print(response)
#     lines=[]
#     for result_page in response:
#         for item in result_page["Blocks"]:
#             if item["BlockType"] == "LINE":
#                 print(item["Text"])
#                 lines.append(item["Text"])  
#     # if (gpt):            
#     #     key='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'
#     #     open_client = OpenAI(api_key=key)            
#     #     chat_response = open_client.chat.completions.create(
#     #     model="gpt-3.5-turbo-1106",
#     #     messages=[
#     #         {"role": "system", "content": "You are a helpful assistant."},
#     #         {"role": "user", "content": f"Please go through this ocr extracted data, just give me output in json format of this data like key value pairs no need to explain:{lines}"},

#     #     ]
#     #     )   
#     #     chat_gpt=chat_response.choices[0].message.content  
#     #     print(chat_gpt)         
#     return lines    

@xframe_options_exempt
@csrf_exempt
def home(request):
    
    context = {}
    if request.method == 'OPTIONS':
        # Prepare response for OPTIONS request
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*' 
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'  
        return response
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        contract_id = request.POST.get('contract_id')
        print(contract_id)
        contract = None
        if contract_id:
            try:
                contract = Contract.objects.get(id=contract_id)
            except Contract.DoesNotExist:
                context['error'] = 'Contract not found'
                return JsonResponse(context, status=400)
        cur_dir=py_path(os.path.dirname(os.getcwd()))
        full_path=cur_dir+'/media/'+filename
        context['success_message'] = 'Your file has been uploaded successfully!'
        extract_text_from_pdf(full_path)
        text=extract_results(contract.prompt)
        context['uploaded_file_url']=uploaded_file_url
        context['extracted_text']=text
        # print(request.user)
        if request.user.is_authenticated:
            print("user is authenticated")
            UploadedFile.objects.create(
                    user=request.user,
                    file=file,
                    extracted_text=text,
                    contract=contract
            )
        return JsonResponse(context)    

    return render(request, 'home.html', context)

def view_history(request):
    if request.method == 'OPTIONS':
        # Prepare response for OPTIONS request
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'  
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type' 
        return response

    elif request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'detail': 'Unauthorized'}, status=401)

        uploaded_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
        files_list = [{
            'id': file.id,
            'filename': file.file.name,
            'extracted_text': file.extracted_text,
            'upload_date': file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            'file_url': request.build_absolute_uri(file.file.url)
        } for file in uploaded_files]

        return JsonResponse({'uploaded_files': files_list})

# @csrf_exempt
# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # Log the user in after signing up
#             login(request, user)
#             # Redirect to home or any other page
#             return redirect('home')
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})
@csrf_exempt  # Note: Better to handle CSRF in AJAX calls than disable it
def signup(request):
    if request.method == 'OPTIONS':
        # Prepare response for OPTIONS request
        response = JsonResponse({'detail': 'Options request successful'})
        response['Access-Control-Allow-Origin'] = '*' 
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'  
        return response   
    if request.method == 'POST':
        # print("Received data:", request.body.decode('utf-8'))
       
        data = json.loads(request.body.decode('utf-8'))
        form = SignUpForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'detail': 'Successfully signed up and logged in.'}, status=201)
        else:
            print(form.errors)  
            return JsonResponse(form.errors, status=400)
    else:
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
@csrf_exempt
def custom_logout(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'  
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'  
        return response
    elif request.method == 'POST':
            print("key",os.environ.get("OPENAI_API_KEY"))
            
            logout(request)  
            return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})  # Send a success response
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


# def upload(request):
#     if request.method == 'POST' and request.FILES['file']:
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)
#         uploaded_file_url = fs.url(filename)
#         UploadedFile.objects.create(file=filename)
#         # Add a success message
#         messages.success(request, 'Your file has been uploaded successfully!')
#         return redirect('upload')  
#     return render(request, 'upload.html')
@csrf_exempt
def exempted_login_view(request, *args, **kwargs):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173' 
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type'  
        return response    
    elif request.method == 'POST':
        # print("post request sent")

        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            print(username)
            print(password)
            
            user = authenticate(request, username=username, password=password)
            print("Authenticated user:", user)
            if user is not None:
                login(request, user)
                return JsonResponse({"detail": "Login successful."}, status=200)
            else:
                return JsonResponse({"detail": "Invalid credentials."}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON."}, status=400)
    else:
        return HttpResponse(status=405)

@csrf_exempt
def exempted_admin_login_view(request, *args, **kwargs):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173' 
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type'  
        return response    
    elif request.method == 'POST':
        # print("post request sent")

        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            print(username)
            print(password)
            
            user = authenticate(request, username=username, password=password)
            print("Authenticated user:", user)
            if user is not None:
                login(request, user)
                is_admin = user.is_staff
                if is_admin:
                    print("-------------------------------------------user is staff--------------------------------")
                return JsonResponse({"detail": "Login successful.","is_admin": is_admin}, status=200)
            else:
                return JsonResponse({"detail": "Invalid credentials."}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON."}, status=400)
    else:
        return HttpResponse(status=405)

class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer    





@csrf_exempt
def create_contract(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type'
        return response
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            contract = Contract.objects.create(
                name=data['name'], 
                prompt=data.get('prompt', ''), 
                description=data.get('description', '')
            )
            return JsonResponse({
                "id": contract.id, 
                "name": contract.name, 
                "prompt": contract.prompt, 
                "description": contract.description
            }, status=201)
        except (TypeError, ValueError, KeyError):
            return JsonResponse({"error": "Bad request"}, status=400)
    else:
        return HttpResponse(status=405)

@csrf_exempt
def update_contract(request, contract_id):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type'
        return response
    elif request.method == 'PUT':
        try:
            print('put method called')
            data = json.loads(request.body)
            print(data)
            print(type(contract_id),contract_id)
            contract = Contract.objects.get(id=contract_id)

            contract.name = data.get('name', contract.name)
            contract.prompt = data.get('prompt', contract.prompt)
            contract.description = data.get('description', contract.description)
            contract.save()
            return JsonResponse({"message": "Contract updated successfully"}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Contract not found"}, status=404)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Bad request"}, status=400)
    else:
        return HttpResponse(status=405)     
@csrf_exempt
def delete_contract(request, contract_id):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type'
        return response
    elif request.method == 'DELETE':
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.delete()
            return HttpResponse(status=204)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Contract not found"}, status=404)
    else:
        return HttpResponse(status=405)    


