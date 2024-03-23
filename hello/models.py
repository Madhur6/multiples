from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    pass

def user_directory_path(instance, filename):
    base_name = os.path.basename(filename)
    name,ext = os.path.splitext(base_name)

    return "note/user/"+ str(instance.note.user.id) + "/"+ str(instance.note.id)+ "/"+"IMG_" + str(instance.note.id)+"_"+name +ext
   

class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    text = models.TextField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Images(models.Model):
    note = models.ForeignKey(Note,on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path,null=True,blank=True)

@receiver(post_delete, sender=Images)
def delete_image_file(sender, instance, **kwargs):
    # Delete the file from the media folder when the record is deleted
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except Exception as e:
            # Log any errors that occur during file deletion
            print(f"Error deleting file: {str(e)}")