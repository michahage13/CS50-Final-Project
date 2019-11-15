from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Case, When, Sum
from PIL import Image as PilImage
from datetime import date


from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)

from .models import macros
from .forms import macrosForm


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def index(request):
    # retrieve data from form and validate, add user as foreignkey
    form = macrosForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.username = request.user
        # check if user uploaded a picture
        if request.FILES:
            instance.image = request.FILES['image']
        # save form data
        instance.save()
        form = macrosForm()
    try:
        #get last 10 meals recorded from logged in user
        queryset = macros.objects.filter(username=request.user).order_by('-date')[:10]
        if len(queryset) != 0:
            #get average macro for last 10 meals and store as average number value
            proteinAvg = macros.objects.filter(username=request.user).order_by('-date')[:10].aggregate(Avg('protein'))
            fatAvg = macros.objects.filter(username=request.user).order_by('-date')[:10].aggregate(Avg('fat'))
            carbAvg = macros.objects.filter(username=request.user).order_by('-date')[:10].aggregate(Avg('carbohydrates'))
            proteinAvg = round(proteinAvg.get("protein__avg"))
            fatAvg = round(fatAvg.get("fat__avg"))
            carbAvg = round(carbAvg.get("carbohydrates__avg"))
            #calculate average calories for last 10 meals
            calAvg = round((proteinAvg*4) + (fatAvg*9) + (carbAvg*4))
            #count cheatdays during last 10 cheatdays
            cheatTotal = macros.objects.filter(username=request.user).order_by('-date')[:10].aggregate(dictkey=Count(Case(When(cheat=True, then=1))))
            cheatTotal = cheatTotal.get("dictkey")
        else:
            proteinAvg = None
            fatAvg = None
            carbAvg = None
            calAvg = None
            cheatTotal = None
    except macros.DoesNotExist:
        raise Http404("No data exists")
    context = {
            'form':form,
            'instances':queryset,
            'protein_avg':proteinAvg,
            'fat_avg':fatAvg,
            'carb_avg':carbAvg,
            'cal_avg':calAvg,
            'cheat_total':cheatTotal
        }
    return render(request, "nutrition/index.html", context)

# can possibly be deleted
class macrosListView(ListView):
    template_name = "nutrition/macros_list.html"
    queryset = macros.objects.all()

# get all entries and display them on a page
@login_required
def macroslist(request):
    try:
        queryset = macros.objects.filter(username=request.user)
    except macros.DoesNotExist:
        raise Http404("No data exists")
    context = {
        "instances": queryset
    }
    return render(request, "nutrition/macroslist.html", context)

# validates search parameter
def valid_search(para):
    return para != '' and para is not None

# get all entries and filter them according to search input
@login_required
def search_entry(request):
    try:
        queryset = macros.objects.filter(username=request.user)
    except macros.DoesNotExist:
        raise Http404("No data exists")
    # store search form inputs in variables
    comment = request.GET.get('comment')
    mealdate = request.GET.get('mealdate')
    mealdateEnd = request.GET.get('mealdateEnd')
    macroFilter = request.GET.get('macrofilter')
    cheatcheck = request.GET.get('cheat')
    # filter queryset with user search inputs
    if valid_search(comment):
        queryset = queryset.filter(comment__icontains=comment)
    if valid_search(mealdate):
        queryset = queryset.filter(date__gte=mealdate)
    if valid_search(mealdateEnd):
        queryset = queryset.filter(date__lte=mealdateEnd)
    # Filter by cheat days
    if valid_search(cheatcheck):
        if cheatcheck == "cheat":
            queryset = queryset.filter(cheat=True)
        elif cheatcheck == "clean":
            queryset = queryset.filter(cheat=False)
    # order queryset by macro
    if valid_search(macroFilter):
        if macroFilter == "protein":
            queryset = queryset.order_by('protein')
        elif macroFilter == "fat":
            queryset = queryset.order_by('fat')
        elif macroFilter == "carbohydrate":
            queryset = queryset.order_by('carbohydrates')
    # calculate total values and average for applied searched
    proteinTOTAL = queryset.aggregate(Sum('protein'))
    proteinAVG = queryset.aggregate(Avg('protein'))
    fatTOTAL = queryset.aggregate(Sum('fat'))
    fatAVG = queryset.aggregate(Avg('fat'))
    carbTOTAL = queryset.aggregate(Sum('carbohydrates'))
    carbAVG = queryset.aggregate(Avg('carbohydrates'))
    # extract values and save as ints
    try:
        proteinTOTAL = round(proteinTOTAL.get("protein__sum"))
        proteinAVG = round(proteinAVG.get("protein__avg"))
        fatTOTAL = round(fatTOTAL.get("fat__sum"))
        fatAVG = round(fatAVG.get("fat__avg"))
        carbTOTAL = round(carbTOTAL.get("carbohydrates__sum"))
        carbAVG = round(carbAVG.get("carbohydrates__avg"))
    except:
        raise Http404("No data exists. Make sure to select a period that is in the past")
    # calculate total and average calories according to these values
    calTOTAL = round((proteinTOTAL*4) + (fatTOTAL*9) + (carbTOTAL*4))
    calAVG = round((proteinAVG*4) + (fatAVG*9) + (carbAVG*4))
    # number of cheatdays during period
    cheatTOTAL = queryset.aggregate(dictkey=Count(Case(When(cheat=True, then=1))))
    cheatTOTAL = cheatTOTAL.get("dictkey")
    # number of meals in specified period
    mealsTOTAL = len(queryset)
    # store in context and render page
    context = {
        "instances": queryset,
        "proteinTOTAL": proteinTOTAL,
        "proteinAVG": proteinAVG,
        "fatTOTAL": fatTOTAL,
        "fatAVG": fatAVG,
        "carbTOTAL": carbTOTAL,
        "carbAVG": carbAVG,
        "calTOTAL": calTOTAL,
        "calAVG": calAVG,
        "cheatTOTAL": cheatTOTAL,
        "mealsTOTAL": mealsTOTAL
    }
    return render(request, "nutrition/macroslist.html", context)


def macro(request, day_id):
    try:
        day = macros.objects.get(pk=day_id)
    except macros.DoesNotExist:
        raise Http404("Day does not exist")
    context = {
        "dailynutrition": day
    }
    return render(request, "nutrition/nutrition.html", context)

# delete an entry on click
@login_required
def delete_record(request, id):
    try:
        rec = macros.objects.get(pk=id)
    except macros.DoesNotExist:
        raise Http404("Record does not exist")
    rec.delete()
    return redirect('../')

# Show one meal entry with all its model fields from the database (searched or from the table)
@login_required
def meal_display(request, id):
    try:
        rec = macros.objects.get(pk=id)
        if rec.username != request.user:
            raise Http404("Record does belong to different user")
    except macros.DoesNotExist:
        raise Http404("Record does not exist")
    context = {
        "meal": rec
    }
    return render(request, "nutrition/meal_display.html", context)

# rotate picture 90 degrees to the left - does not work
@login_required
def image_rotate_right(request, id):
    # getting instance of the model
    rec = macros.objects.get(pk=id)
    # opening image for PIL to access
    img = PilImage.open(rec.image)
    # rotating it by built in PIL command
    rotated_img = img.rotate(270)
    #saving rotated image instead of original. Overwriting is on
    rotated_img.save(rec.image.file.name, overwrite=True)
    #return HttpResponse(str(macros.image))
    context = {
        "meal": rec
    }
    return render(request, "nutrition/meal_display.html", context)

@login_required
def image_rotate_left(request, id):
    # getting instance of the model
    rec = macros.objects.get(pk=id)
    # opening image for PIL to access
    img = PilImage.open(rec.image)
    # rotating it by built in PIL command
    rotated_img = img.rotate(90)
    #saving rotated image instead of original. Overwriting is on
    rotated_img.save(rec.image.file.name, overwrite=True)
    #return HttpResponse(str(macros.image))
    context = {
        "meal": rec
    }
    return render(request, "nutrition/meal_display.html", context)

#render account page
@login_required
def account(request):
    try:
        queryset = macros.objects.filter(username=request.user)
    except macros.DoesNotExist:
        raise Http404("No data exists")
    # number of meals registered as current user and date of registration
    recs = len(queryset)
    joined = request.user.date_joined
    context = {
        "entries": recs,
        "joinDate": joined
    }
    return render(request, "nutrition/account.html", context)

@login_required
def change_pw(request):
    #if request.method=="GET":
        #return render(request, "nutrition/change_pw.html")
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account_page')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'nutrition/change_pw.html', {
        'form': form
    })

# delete current user NEEDS confirmation // redirect to different profile
@login_required
def del_user(request):
        #u = User.objects.get(username = request.user)
    request.user.delete()
        #messages.success(request, "The user is deleted")
    return render(request, 'registration/bye.html')

# raise confirmation page for deleting account
@login_required
def del_user_confirm(request):
    return render(request, 'nutrition/delete_confirm.html')

# render about page
@login_required
def about_page(request):
    return render(request, 'nutrition/about.html')


# Create your views here.
# def sign_up(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             return HttpResponse('A new user has been successfully registered!')
#     else:
#         form = UserCreationForm()
#     return render(request, 'nutrition/register.html', {'form': form})

#test if needed
# @login_required
# def index_first(request):
#     try:
#         #get last 10 meals recorded from logged in user
#         queryset = macros.objects.filter(username=request.user).order_by('-date')[:10]
#     except macros.DoesNotExist:
#         raise Http404("No data exists")
#     form = macrosForm(request.POST or None)
#     if form.is_valid():
#         instance = form.save(commit=False)
#         instance.username = request.user
#         # check if user uploaded a picture
#         if request.FILES:
#             instance.image = request.FILES['image']
#         # save form data
#         instance.save()
#         form = macrosForm()
#
#     context = {
#             'form':form,
#         }
#     return render(request, "nutrition/index.html", context)

# @login_required()
# def user_dashboard(request):
#     return render(request, 'nutrition/dashboard.html')
