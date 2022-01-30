from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

import random,string
import base64
from pathlib import Path
def randomStringGenerator():
	name = "I"
	name = name + str(random.randint(100, 999))
	letters = string.ascii_uppercase
	name = name + ''.join(random.choice(letters) for i in range(2))
	name = name + str(random.randint(10, 99))
	name = name + ''.join(random.choice(letters) for i in range(2))
	name = name + str(random.randint(100, 999))
	return name

def fileUrlGenerate(bytes_obj):
    format, imgstr = bytes_obj.split(';base64,') 
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr))
    fs = FileSystemStorage(
            location=Path.joinpath(Path(__file__).parent.parent,'media'),
            base_url='/media/'
        )
    filename = fs.save(randomStringGenerator()+'.'+ext, data)
    url_ = fs.url(filename)
    return url_