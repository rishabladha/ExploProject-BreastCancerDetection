from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
# Create your views here.
from tkinter import *
from tkinter import filedialog
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import h5py
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
from reportlab.lib.colors import yellow, red, black,white
from django.contrib import messages

from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import *
from .forms import CreateUserForm
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


def some_view(request, pk):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    k = result.objects.get(id=pk)
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    print(pk)
    p.setLineWidth(2)
    p.drawBoundary(1,1.3,1,592.7,840)
    p.line(0.5,0,0.5,2000)
    
    # p.setFillColorRGB(1,0,0)
    # p.setStrokeColorRGB(black)
    p.setStrokeColorRGB(0.2, 0.5, 0.3)
    p.setFillColorRGB(1,0,1)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica-Bold", 32)
    p.setLineWidth(3)
    p.line(1.5,750,592.6,750)
    p.drawString(130, 780,"Breast Cancer Report")
    p.setFont("Helvetica-Bold", 22)
    # p.setFillColor((#99b0e7)
    p.drawString(130, 180,k.result + "%")
    # print(k.image)
    # p.drawBoundary(True)
    p.drawImage(k.image.path,102,270, height=400 , width= 400 , showBoundary=True)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='Report.pdf')


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index(request):
    context = {'a': 1}
    return render(request, 'index.html', context)


@login_required(login_url='login')
def predictImage(request):
    print(request)
    print(request.POST.dict())
    fileObj = request.FILES['filePath']
    fs = FileSystemStorage()
    filePathName = fs.save(fileObj.name, fileObj)
    filePathName = fs.url(filePathName)
    model = load_model('./models/9april.h5')
    img = cv2.imread(filePathName)
    print(filePathName)
    print(type(img))
    result.objects.create(image=fileObj, result='102')
    # print(img.shape)
    # test_image = cv2.imread(r'media/SOB_M_DC-14-2523-40-010.png')
    # test_image = cv2.imread(r'media/benign3.png')
    filePathName = str(".") + filePathName
    print(filePathName)
    test_image = cv2.imread(filePathName)
    # test_image = cv2.imread(r'filePathName')
    # test_image = Image.open('media/SOB_M_DC-14-2523-40-010.png')
    print(type(test_image))
    type(test_image)
    type(test_image)
    # print(test_image.shape)
    # /home/rishi_maheswari/Downloads/exploratory/Breast_Cancer_Detection/media/SOB_M_LC-14-16196-100-014.png
    try:
        test_image = cv2.resize(test_image, (140, 92))
        print("executed1")
    except Exception as e:
        print(str(e))

    # print(test_image.shape)
    test_image = test_image.reshape(92, 140, 3)

    test_image = np.array(test_image)
    print("executed1")
    print(test_image.shape)
    test_image = test_image.astype('float32')
    print("executed3")
    test_image /= 255
    print(test_image.shape)
    print("executed4")
    test_image = np.expand_dims(test_image, axis=0)
    print(test_image.shape)
    print("executed5")
    pa = model.predict(test_image)
    print(str(pa[0][0]*100))
    print(str(pa[0][1]*100))
    # print("executed6")s
    print(test_image.shape)
    print("executed7")
    # if(model.predict_classes(test_image) == [0]):
    # print((model.predict(test_image) > 0.5).any())

    if((model.predict(test_image) > 0.5).any() == [0]):
        s = "BENIGN : " + str(pa[0][0]*100)
    else:
        s = "MALIGNANT : " + str(pa[0][1]*100) 

    if(pa[0][1]*100 <= 50):
        s = "BENIGN : " + str(pa[0][0]*100) 

    print("executed8")
    print(s)
    k = result.objects.create(image=fileObj, result=s)
    context = {'s': s, 'id': k.id}
    # context = {'filePathName': filePathName}
    return render(request, 'predict.html', context)
# /home/rishi_maheswari/Desktop/Breast_Cancer_Detection/media/SOB_M_DC-14-2523-40-010.png
# media/SOB_M_DC-14-2523-40-010.png
