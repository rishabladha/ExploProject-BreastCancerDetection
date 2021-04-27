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
import cv2
import os
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

# Create your views here.


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
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')   # after successful info user will be registered and will be redirected to login page

        context = {'form': form}           # dictionary format
    return render(request, 'register.html', context)    #if not post request then form will be created and user will be redirected to register,html page



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
    return redirect('login')                  


# to redirect the website to home page
@login_required(login_url='login')
def index(request):
    context = {'a': 1}
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

    print(s)
    k = result.objects.create(image=fileObj, result=s)      
    context = {'s': s, 'id': k.id}
    return render(request, 'predict.html', context)    # sending results to predict.html page to print


# here we are creating a view for to download the report as pdf

def some_view(request, pk):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    k = result.objects.get(id=pk)
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    p.setLineWidth(2)                                 # line width 
    p.drawBoundary(1, 1.3, 1, 592.7, 840)             # to draw boundary around pdf
    p.line(0.5, 0, 0.5, 2000)                         # straight line with given cordinates

    p.setStrokeColorRGB(0.2, 0.5, 0.3)                # color setting
    p.setFillColorRGB(1, 0, 1)                         
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica-Bold", 32)                   # to set font type
    p.setLineWidth(3)                                 
    p.line(1.5, 750, 592.6, 750)    
    p.drawString(130, 780, "Breast Cancer Report")    # used to writr string
    p.setFont("Helvetica-Bold", 22)
  
    p.drawString(130, 180, k.result + "%")
   
    p.drawImage(k.image.path, 102, 270, height=400,
                width=400, showBoundary=True)         # used to draw image

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='Report.pdf')    #this will return report.pdf
