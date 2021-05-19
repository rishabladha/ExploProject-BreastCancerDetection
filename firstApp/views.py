from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import numpy as np
from PIL import Image
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
from keras.models import load_model
from keras.utils.vis_utils import plot_model
from reportlab.lib.utils import ImageReader
import cv2
import re
import os
import random
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from reportlab.lib.colors import yellow, red, black, white
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateUserForm
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
# Create your views here.
# from pyrebase import pyrebase
from django.forms import EmailField
from django.core.exceptions import ValidationError


from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


def base2(request):
    context = {'a': 1}
    return render(request, 'base2.html', context)    


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = 'password_reset_email.txt'
					c = {
					"email": user.email,
					'domain': 'Breast Cancer Deection.com',
					'site_name': 'Cancer Detection',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect('index.html')      
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name='password_reset.html', context={"password_reset_form":password_reset_form})






def isEmailAddressValid( email ):
    try:
        EmailField().clean(email)
        return True
    except ValidationError:
        return False

# view function for registration of user
def registerPage(request):
    if request.user.is_authenticated:   #checking is user is authenticated or not
        return redirect('homepage')     # if user is already logged it will send to home page
    else:                               # else it will create registration form and ask ceredentals
        form = CreateUserForm()          
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                if isEmailAddressValid(email):
                    print("exectuted email")
                    print(email)
                    messages.success(request, 'Account was created for ' + user)
                    return redirect('login')   
                  # after successful info user will be registered and will be redirected to login pag
        context = {'form': form}           # dictionary format
    return render(request, 'newregister.html', context)    #if not post request then form will be created and user will be redirected to register,html page



# view for login - this will check the user authentication
def loginPage(request):
    if request.user.is_authenticated:    #checking is user is authenticated or not
        return redirect('homepage')      # if user is already logged it will send to home page
    else:                                
        if request.method == 'POST':     # if user submitted ceredentals then it will check is it correct or not
            username = request.POST.get('username')    # getting username
            password = request.POST.get('password')    # getting password

            user = authenticate(request, username=username, password=password)

            if user is not None:         
                login(request, user)
                return redirect('homepage')     # if user is registered and ceredentals are correct then it will redirect to home page
            else:
                messages.info(request, 'Username OR password is incorrect')   # if user is not registered or username or password are incorrect

        context = {}
    return render(request, 'login.html', context)



# view for logout
def logoutUser(request):
    logout(request)                           # logout fn 
    return redirect('base')                  


# to redirect the website to home page
@login_required(login_url='login')
def index(request):
    counter=Counter.objects.get(pk=1)
    counte=counter.count1
    counte+=1
    counter.count1=counte
    counter.save()
    context = {'counte': counte}
    return render(request, 'index.html', context)      # redirect to index.html





# important - this is the view for the prediction of image
@login_required(login_url='login')
def predictImage(request):
    print(request)
    print(request.POST.dict())
    fileObj = request.FILES['filePath']                # this will provide image path
    fs = FileSystemStorage()
    filePathName = fs.save(fileObj.name, fileObj)
    filePathName = fs.url(filePathName)                 # full path of the image
    model = load_model('./models/BreastCancer.h5')      # this will load the model
    img = cv2.imread(filePathName)                      # reading image using cv2
    result.objects.create(image=fileObj, result='102')  # result object is created
    filePathName = str(".") + filePathName               
    test_image = cv2.imread(filePathName)
    try:
        test_image = cv2.resize(test_image, (140, 92))  # it will resize image to required format
    except Exception as e:
        print(str(e))
    test_image = test_image.reshape(92, 140, 3)          # it will reshape image
    test_image = np.array(test_image)                    # converting image to num py array format
    test_image = test_image.astype('float32')
    test_image /= 255                                    # normalizing
    print(test_image.shape)
    test_image = np.expand_dims(test_image, axis=0)      # finally converted in required format
    pa = model.predict(test_image)                       # predicting image
    if((model.predict(test_image) > 0.5).any() == [0]):
        s = "BENIGN : " + str(pa[0][0]*100)
    else:
        s = "MALIGNANT : " + str(pa[0][1]*100)
    if(pa[0][1]*100 <= 50):
        s = "BENIGN : " + str(pa[0][0]*100)   # now storing the address!
     
    username = request.user.username
    email = request.user.email
    # print(k.image.url)    
    i=0
    t = []
    while i < 17:
        t.append(s[i])
        i += 1

    ''.join(t)    
    
    str1 = "" 
    for ele in t: 
        str1 += ele
   

## storing strings in a list
    digits = [i for i in range(0, 10)]

## initializing a string
    random_str = ""

## we can generate any lenght of string we want
    for i in range(6):
        index12 = math.floor(random.random() * 10)
        random_str += str(digits[index12])

    k = result.objects.create(image=fileObj, result=str1) 
    print(t)
    context = {'str1': str1, 'id': k.id , 'image' : k.image.url , 'email' : email , 'username' : username , 'random_str' : random_str}
    return render(request, 'predict.html', context)    # sending results to predict.html page to print


# here we are creating a view for to download the report as pdf
def some_view(request, pk):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    
    k = result.objects.get(id=pk)
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    username = request.user.username
    email = request.user.email
    p.setLineWidth(2)                                 # line width 
    p.drawBoundary(1, 1.3, 1, 592.7, 840)             # to draw boundary around pdf
    p.line(0.5, 0 , 0.5, 2000)                         # straight line with given cordinates

    # p.setStrokeColorRGB(0.2, 0.5, 0.3)                # color setting
    p.setFillColorRGB(0, 0, 0)                         
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica-Bold", 32)                   # to set font type
    ## storing strings in a list
    digits = [i for i in range(0, 10)]
     
## initializing a string
    random_str = ""

## we can generate any lenght of string we want
    for i in range(6):
        index12 = math.floor(random.random() * 10)
        random_str += str(digits[index12])
    p.setLineWidth(3)                                 
    p.line(1.5, 750, 592.6, 750)    
    p.drawString(190, 780, "TEST RESULTS")    # used to writr string
    p.setFont("Helvetica-Bold", 18)
    p.drawString(122, 690, "Patient Id        :" + "  "  + random_str )
    p.drawString(122, 660, "Patient Name : " + "  "  + username )
    p.drawString(122, 630, "Email Id          : " + "  "  + email )
    p.setFont("Helvetica-Bold", 22)
    p.drawString(122    , 150, k.result + "%")
    # p.drawImage(static/assets/images/iitbhulogo.png, 122, 200, height=400,width=400, showBoundary=True)
    logo = ImageReader('https://old.iitbhu.ac.in/icmc2018/apm/images/IITBHU-Logo.jpg')
    logo2 = ImageReader('https://www.iitbhu.ac.in/sites/default/files/iitbhu/iit_name.jpg')
    # logo2 = ImageReader('https://alumni.iitbhu.ac.in/static/images/logos/cent.png')
    # p.setStrokeColorRGB(0.2, 0.5, 0.3) 
    p.drawImage(logo2, 20, 760, height=70,width=140)
    p.drawImage(logo, 500, 760, height=70,width=70)
    p.setStrokeColorRGB(0.2, 0.5, 0.3) 
    p.drawImage(k.image.path, 122, 200, height=380,width=400, showBoundary=True)         # used to draw image

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    print(type(p))
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    # email = EmailMessage(
    # 'Subject here', 'Here is the message.', 'rishab.ladha.cd.se19@itbhu.ac.in', ['rishab.ladha.cer19@itbhu.ac.in'])
    # email.attach_file('/home/rishi_maheswari/Documents/GitHub/Explo-Under-SKS-Sir-BreastCancerPrediction (w)/template/Report.pdf')
    # email.send()
    print(type(buffer))
    return FileResponse(buffer, as_attachment=True, filename='Report.pdf')    #this will return report.pdf
   
# @staticmethod
def send_email(request):
    print("this send view executed")
    email1 = request.user.email
    email = EmailMessage(
    'Your Breast Cancer Detection Report', 'See Below Attachment We have provide you Report , Stay Safe , Stay Home!', 'rishab.ladha.cd.cse19@itbhu.ac.in', [email1])
    email.attach_file('/home/rishi_maheswari/Downloads/Report.pdf')
    print("this send view executed1")
    email.send()
    print("this send view executed2")
    context = {'a': 1}
    return render(request,'index.html', context)


