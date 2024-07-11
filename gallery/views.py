import json
import os
from django.shortcuts import render
from django.conf import settings

def gallery_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'styles_config.json')
    with open(json_path, 'r') as f:
        images_data = json.load(f)
    return render(request, 'gallery/gallery.html', {'images_data': images_data})

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)
        return redirect('gallery')  # Redirect to the gallery view after upload
    return render(request, 'gallery/upload.html')