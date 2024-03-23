from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Note, Images
from django.db import IntegrityError

from .forms import NoteForm, NoteFullForm

from django.core.exceptions import ValidationError
from django.conf import settings

from django.http import JsonResponse, HttpResponse
from django.core.signing import Signer, BadSignature
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_images = Images.objects.filter(note__user=request.user)
    return render(request, 'hello/index.html', {
        'user_images': user_images
    })

# def get_image_url(request, image_id):
#     try:
#         image = Images.objects.get(id=image_id)
#         image_url = image.image.url
#         return JsonResponse({'image_url': image_url})
#     except Images.DoesNotExist:
#         return JsonResponse({'error': 'Image not found'}, status=404)
    

def get_temporary_image_url(request, image_id):
    try:
        image = Images.objects.get(id=image_id)
        image_url = image.image.url
        signer = Signer()
        timestamp = int(timezone.now().timestamp())
        signed_value = signer.sign(f'{image_id}-{timestamp}')
        return JsonResponse({'image_url': f'/get-image/{signed_value}/'})
    except Images.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)

def get_image(request, signed_value):
    signer = Signer()
    try:
        image_id, timestamp = signer.unsign(signed_value).split('-')
        image = Images.objects.get(id=image_id)
        return redirect(image.image.url)
    
        # Check if the request is made within a certain time window (e.g., 5 minutes)
        # if int(timezone.now().timestamp()) - int(timestamp) <= 300:  
        #     return redirect(image.image.url)
        # else:
        #     return HttpResponse('Link expired.', status=403)

    except (BadSignature, ValueError, Images.DoesNotExist):
        return HttpResponse('Invalid link.', status=403)

def addNoteView(request):
    if request.method == "POST":
        #images will be in request.FILES
        form = NoteFullForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            try:
                user = request.user
                title = form.cleaned_data['title']
                text = form.cleaned_data['text']
                note_obj = Note.objects.create(user=user,title=title,text=text) #create will create as well as save too in db.

                # Count the total number of images uploaded by the user
                total_images_count = Images.objects.filter(note__user=user).count()

                # Check if the user has exceeded the maximum limit (10 images)
                if total_images_count + len(request.FILES.getlist('images')) > 10:
                    raise ValidationError("You can upload a maximum of 10 images. Delete some previous images to add more.")



                images = request.FILES.getlist('images')
                # Check if the number of images exceeds 5
                if images and len(images) > 3:
                    raise ValidationError("You can upload a maximum of 3 images.")
            
                for image in images:
                    if image.size > settings.MAX_UPLOAD_SIZE*1024*1024:
                        raise ValidationError(f"Image file {image.name} exceeds {settings.MAX_UPLOAD_SIZE} MB size limit")
                    Images.objects.create(note=note_obj, image=image)

            except ValidationError as e:
                message = ''.join(e)
                return render(request, 'hello/addNote.html', {'message':message})
            
            return redirect('index')
        else:
            print("Form invalid")
    return render(request, 'hello/addNote.html')

def delete_images(request):
    if request.method == "POST":
        selected_image_ids = request.POST.getlist('selected_image_ids')

        # Delete selected images
        Images.objects.filter(id__in=selected_image_ids).delete()

    return redirect('index')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'hello/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'hello/login.html')


def logout_view(request):
    logout(request)
    return redirect('index')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']

        password = request.POST['password']
        confirmation = request.POST['confirmation']

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'hello/register.html', {
                "message": "User already exists!"
            })
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'hello/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'hello/register.html')