# Standard Library Imports
import random
import time
from datetime import datetime
import os
from itertools import chain
import re
import string

# Third-Party Imports
import openai
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

# Django REST Framework Imports
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Local Imports
from .models import (QuestionP2, QuestionP1, QuestionP3, Profile, Pwdlist, PDFFile, Like, P2ASOCR, P1ASOCR)
from .serializers import (Paper1serializer, Paper2serializer, Paper3serializer)




script_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(script_dir, '', 'STIX Two Math Regular.ttf')
pdfmetrics.registerFont(TTFont('STIXTwoMath', font_path))

pdfs_folder = os.path.join(settings.MEDIA_ROOT, 'pdfs')
if not os.path.exists(pdfs_folder):
    os.makedirs(pdfs_folder)

openai.api_key = "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"

#def ads(request):
 #   return render(request, 'ads.txt')

def ai_exam_(request):
    if request.method == 'POST':
        selected_checkboxes = request.POST.getlist('checkbox_name')
        user_object = User.objects.get(username=request.user.username)
        file = request.POST['filename']
        difficulty = request.POST.get('hard', '')
        large = request.POST.get('large', '')

        if large == "large":
            if difficulty == "hard":
                messages = [{"role": "user", "content": f"Write me 24 GCSE questions (with mark scheme at end and make sure there is space between last question markscheme) of these following topics '{selected_checkboxes}' (same topic, but make sure they are different numbers or wording). if question requires a diagram please descirbe the diagram and the whole paper should be around 50 minutes long. This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…' THE DIFFICULTY IS HARD. MAKE SURE THE QUESTIONS GET HARDER AND HARDER."}]
            else:
                messages = [{"role": "user", "content": f"Write me 22 GCSE questions (with mark scheme at end and make sure there is space between last question markscheme) of these following topics '{selected_checkboxes}' (same topic, but make sure they are different numbers or wording). if question requires a diagram please descirbe the diagram and the whole paper should be around 50 minutes long. This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…' "}]
        else:
            if difficulty == "hard":
                messages = [{"role": "user", "content": f"Write me 12 GCSE questions (with mark scheme at end and make sure there is space between last question markscheme) of these following topics '{selected_checkboxes}' (same topic, but make sure they are different numbers or wording). if question requires a diagram please descirbe the diagram and the whole paper should be around 25 minutes long. This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…' THE DIFFICULTY IS HARD. MAKE SURE THE QUESTIONS GET HARDER AND HARDER."}]
            else:
                messages = [{"role": "user", "content": f"Write me 10 GCSE questions (with mark scheme at end and make sure there is space between last question markscheme) of these following topics '{selected_checkboxes}' (same topic, but make sure they are different numbers or wording). if question requires a diagram please descirbe the diagram and the whole paper should be around 25 minutes long. This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…' "}]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )
        response_message = response["choices"][0]["message"]

        # Ensure response_message is a string
        response_message = str(response_message["content"])

        # Create a PDF document
        pdf_file_path = os.path.join(pdfs_folder, f"{file}.pdf")
        doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)

        # Define styles for paragraphs
        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(name='CustomStyle', fontName='STIXTwoMath', fontSize=12, leading=14)

        # Create content for the PDF
        story = []

        if large == "large":
            intro_text = f"Mathsbase Exam Mini Mock\n\n 55 Minutes"
            story.append(Paragraph(intro_text, styles["Title"]))
            story.append(PageBreak())  # Add a page break before adding questions
        else:
            header_text = f"Mathsbase Exam Questions: \n\n 25 Minutes"
            story.append(Paragraph(header_text, styles['Title']))

        # Add questions
        questions = response_message.split("QQ ")
        for question in questions:
            if question.strip():
                story.append(Spacer(1, 10))
                q = question.strip()
                p = Paragraph(q, custom_style)
                story.append(p)
                story.append(Spacer(1, 225))
                #story.append(Paragraph("Answer: ___________________________________________", styles['Normal']))

        # Build the PDF document
        doc.build(story)

        # Save the PDF object to the database
        pdf_object = PDFFile(name=file, file=f"pdfs/{file}.pdf", username=user_object)
        pdf_object.save()

        # Return the PDF as a response
        with open(pdf_file_path, 'rb') as pdf_data:
            response = HttpResponse(pdf_data.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{file}.pdf"'
            return response



def ai_exam(request):
    return render(request, 'ai_exam.html')

def sitemap(request):
    return render(request, 'sitemap.xml')

def homepage(request):
    return render(request, 'homepage.html')

def map(request):
    return render(request, 'map.html')

def like(request):
    username = request.user.username
    pdf_name = request.GET.get('pdf_name')

    post = PDFFile.objects.get(name=pdf_name)

    like_filter = Like.objects.filter(pdf_name=pdf_name, username=username).first()

    if like_filter == None:
        new_like = Like.objects.create(pdf_name=pdf_name, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/library')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/library')

def library(request):
    pdf_files = PDFFile.objects.all()
    return render(request, 'library.html', {'pdf_files': pdf_files})

def delete_pdf(request, pdf_id):
    int(pdf_id)
    pdf_file = PDFFile.objects.get(pk=pdf_id)
    pdf_file.file.delete()
    pdf_file.delete()
    return redirect('library')

def download_pdf(request, pdf_id):
    # Retrieve the PDFFile object by its ID or any other unique identifier
    pdf_file = PDFFile.objects.get(pk=pdf_id)

    try:
        # Use FileResponse to serve the file for download
        response = FileResponse(open(pdf_file.file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_file.name}.pdf"'
        return response
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)

def ai_exercises(request):
    return render(request, 'ai_exercise.html')

def ai_ex(request):
    if request.method == 'POST':
        user_object = User.objects.get(username=request.user.username)
        prompt = request.POST['prompt']
        file = request.POST['filename']
        topic = request.POST['topic']
        quantity = int(request.POST['quantity'])
        difficulty = request.POST.get('hard', '')
        compact = request.POST.get('compact', '')
        formatted = request.POST.get('f', '')

        if difficulty == "hard":
            messages = [{"role": "user", "content": f"Write me {quantity} questions like this one of '{prompt}' (same topic, but make sure they are different numbers or wording) . This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…' THE DIFFICULTY IS HARD. MAKE SURE THE QUESTIONS GET HARDER AND HARDER."}]
        else:
            messages = [{"role": "user", "content": f"Write me {quantity} questions like this one of '{prompt}' (same topic, but make sure they are different numbers or wording). This is for my program that creates AI generated pdf with questions. Make sure there is a mark scheme with answers at the end. Please keep it GCSE Style and mention the amount of marks. Also it is extremely important before every question to write QQ, for example: 'QQ 1) what is…'"}]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )
        response_message = response["choices"][0]["message"]

        # Ensure response_message is a string
        response_message = str(response_message["content"])

        # Create a PDF document
        pdf_file_path = os.path.join(pdfs_folder, f"{file}.pdf")
        doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)

        # Define styles for paragraphs
        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(name='CustomStyle', fontName='STIXTwoMath', fontSize=12, leading=14)

        # Create content for the PDF
        story = []

        if formatted == "f":
            intro_text = f"Mathsbase Exam Questions\n\n {topic}"
            story.append(Paragraph(intro_text, styles["Title"]))
            story.append(PageBreak())  # Add a page break before adding questions
        else:
            header_text = f"Mathsbase Exam Questions: {topic}"
            story.append(Paragraph(header_text, styles['Title']))

        # Add questions
        questions = response_message.split("QQ ")
        for question in questions:
            if question.strip():
                if compact == "compact":
                    story.append(Spacer(1, 20))
                    q = question.strip()
                    p = Paragraph(q, custom_style)
                    story.append(p)
                    story.append(Spacer(1, 20))
                    story.append(Paragraph("Answer: ______________", styles['Normal']))
                else:
                    story.append(Spacer(1, 10))
                    q = question.strip()
                    p = Paragraph(q, custom_style)
                    story.append(p)
                    story.append(Spacer(1, 150))
                    story.append(Paragraph("Answer: ______________", styles['Normal']))

        # Build the PDF document
        doc.build(story)

        # Save the PDF object to the database
        pdf_object = PDFFile(name=file, file=f"pdfs/{file}.pdf", username=user_object)
        pdf_object.save()

        # Return the PDF as a response
        with open(pdf_file_path, 'rb') as pdf_data:
            response = HttpResponse(pdf_data.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{file}.pdf"'
            return response


def ai(request):
    # Example prompt 5-2021-2
    if request.method == 'POST':
        prompt = request.POST['prompt']
        pattern = r'\d+-\d+-\d+'

        # Check if the prompt matches the pattern
        if re.match(pattern, prompt):
            split_prompt = prompt.split("-")
            year = split_prompt[1]
            number = split_prompt[0]

            if prompt[-1] == "1":
                p = QuestionP1.objects.get(year=year, number=number)
                messages = [{"role": "user", "content": p.prompt}]
                img = p.img

            elif prompt[-1] == "2":
                p = QuestionP2.objects.get(year=year, number=number)
                messages = [{"role": "user", "content": p.prompt}]
                img = p.img

            elif prompt[-1]  == "3":
                p = QuestionP3.objects.get(year=year, number=number)
                messages = [{"role": "user", "content": p.prompt}]
                img = p.img

            if p.ans == "Not Set":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=messages,
                    #function_call="auto",  # auto is default, but we'll be explicit
                )
                response_message = response["content"]
                p.ans = response_message
                flag = True
            else:
                response_message = p.ans
                flag = False

            return render(request, 'ai_site.html', {'ans':response_message,'prompt':prompt, 'img':img, 'flag':flag})
        else:
            flag = True
            messages = [{"role": "user", "content": prompt}]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                #function_call="auto",  # auto is default, but we'll be explicit
            )
            response_message = response["choices"][0]["message"]

            return render(request, 'ai_site.html', {'ans':response_message, 'prompt':prompt, 'flag':flag})


def ai_site(request):
    return render(request, 'ai_site.html')

@login_required(login_url="signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

        pdf_list = []
        for users in username_profile_list:
            pdf_files = PDFFile.objects.filter(username=users)
            n_pdfs = pdf_files.count()
            pdf_list.append(n_pdfs)

        context = {
            'list': username_profile_list,
            'user_profile': user_profile,
            'np': pdf_list
        }

    return render(request, 'search.html', context)

#
@api_view(['GET'])
def paper1(request, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        if request.method == 'GET':
            p1 = QuestionP1.objects.all()
            serializer = Paper1serializer(p1, many=True)
            return JsonResponse({'Question':serializer.data})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def paper2(request, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        if request.method == 'GET':
            p2 = QuestionP2.objects.all()
            serializer = Paper2serializer(p2, many=True)
            return JsonResponse({'Question':serializer.data})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def paper3(request, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        if request.method == 'GET':
            p3 = QuestionP3.objects.all()
            serializer = Paper3serializer(p3, many=True)
            return JsonResponse({'Question':serializer.data})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

#
@api_view(['GET'])
def paper1details(request, id, pk, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        try:
            question = QuestionP1.objects.get(year=id, number=pk)
        except QuestionP1.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = Paper1serializer(question)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def paper2details(request, id, pk, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        try:
            question = QuestionP2.objects.get(year=id, number=pk)
        except QuestionP2.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = Paper2serializer(question)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def paper3details(request, id, pk, api, format=None):
    profiles = Profile.objects.all()
    keys = []
    is_valid = False

    for i in profiles:
        keys.append(i.api_key)

    for j in range(len(keys)):
        if api == keys[j]:
            is_valid = True
        else:
            is_valid = False

    if is_valid == True:
        try:
            question = QuestionP3.objects.get(year=id, number=pk)
        except QuestionP3.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = Paper3serializer(question)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

# Create your views here.
@login_required(login_url="signin")
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'home.html', context)

@login_required(login_url="signin")
def profile(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    pdf_files = PDFFile.objects.filter(username=user_object)

    n_pdfs = pdf_files.count()

    context = {
        'user': user_object,
        'data': user_profile,
        'number_of_pdfs': n_pdfs
    }

    return render(request, 'profile.html', context)

@login_required(login_url="signin")
def paper3maths(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'paper3maths.html', context)

@login_required(login_url="signin")
def paper2maths(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'paper2maths.html', context)

@login_required(login_url="signin")
def paper1maths(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'paper1maths.html', context)

@login_required(login_url="signin")
def pcomp(request):
    pass

@login_required(login_url="signin")
def upload(request):
    if request.method == 'POST':
        image = request.FILES.get('img')
        year = request.POST['year']
        number = request.POST['number']
        topic = request.POST['topic']
        marks = request.POST['marks']
        prompt = request.POST['prompt']
        ans = request.POST['ans']
        p = request.POST['paper']

        if p == '1':
            new_QuestionP1 = QuestionP1.objects.create(year=year, number=number, topic=topic, marks=marks, img=image, prompt=prompt, ans=ans)
            new_QuestionP1.save()

            return render(request, 'upload_top1.html')
        elif p == '2':
            new_QuestionP2 = QuestionP2.objects.create(year=year, number=number, topic=topic, marks=marks, img=image, prompt=prompt, ans=ans)
            new_QuestionP2.save()

            return render(request, 'upload_top2.html')
        elif p == '3':
            new_QuestionP3 = QuestionP3.objects.create(year=year, number=number, topic=topic, marks=marks, img=image, prompt=prompt, ans=ans)
            new_QuestionP3.save()

            return render(request, 'upload_top3.html')
    else:
        pass


def search_all(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        number = request.POST.get('number')
        marks = request.POST.get('marks')
        topic = request.POST.get('topic')
        p = request.POST.get('paper')

        filters = {}

        if year:
            filters['year'] = year
        if number:
            filters['number'] = number
        if marks:
            filters['marks'] = marks
        if topic:
            filters['topic'] = topic

        if p == '1':
            r_q = QuestionP1.objects.filter(**filters)
            QuestionP1s = list(r_q)
            return render(request, 'paper1maths.html', {"q": QuestionP1s})
        elif p == '2':
            r_q = QuestionP2.objects.filter(**filters)
            QuestionP2s = list(r_q)
            return render(request, 'paper2maths.html', {"q": QuestionP2s})
        elif p == '3':
            r_q = QuestionP3.objects.filter(**filters)
            QuestionP3s = list(r_q)
            return render(request, 'paper3maths.html', {"q": QuestionP3s})

    # Redirect if the request method is not POST
    return redirect('/index')

    if request.method == 'POST':
        number = request.POST['number']
        p = request.POST['paper']

        if p == '1':
            r_q1 = QuestionP1.objects.filter(year=2021, number=number)
            r_q2 = QuestionP1.objects.filter(year=2020, number=number)
            r_q3 = QuestionP1.objects.filter(year=2019, number=number)

            QuestionP1s = []

            for q in r_q1:
                QuestionP1s.append(q)
            for q in r_q2:
                QuestionP1s.append(q)
            for q in r_q3:
                QuestionP1s.append(q)

            return render(request, 'paper1maths.html', {"q":QuestionP1s})
        elif p == '2':
            r_q1 = QuestionP2.objects.filter(year=2021, number=number)
            r_q2 = QuestionP2.objects.filter(year=2020, number=number)
            r_q3 = QuestionP2.objects.filter(year=2019, number=number)
            r_q4 = QuestionP2.objects.filter(year=20190, number=number)
            r_q5 = QuestionP2.objects.filter(year=2018, number=number)
            r_q6 = QuestionP2.objects.filter(year=20180, number=number)


            QuestionP2s = []

            for q in r_q1:
                QuestionP2s.append(q)
            for q in r_q2:
                QuestionP2s.append(q)
            for q in r_q3:
                QuestionP2s.append(q)
            for q in r_q4:
                QuestionP2s.append(q)
            for q in r_q5:
                QuestionP2s.append(q)
            for q in r_q6:
                QuestionP2s.append(q)

            return render(request, 'paper2maths.html', {"q":QuestionP2s})
        elif p == '3':
            r_q1 = QuestionP3.objects.filter(year=2021, number=number)
            r_q3 = QuestionP3.objects.filter(year=2019, number=number)

            QuestionP3s = []

            for q in r_q1:
                QuestionP3s.append(q)
            for q in r_q3:
                QuestionP3s.append(q)

            return render(request, 'paper3maths.html', {"q":QuestionP3s})
    else:
        return redirect('/index')

@login_required(login_url="signin")
def upload_top1(request):

    p12021 = []
    p12020 = []
    p12019 = []
    p120190 = []
    p12018 = []
    p120180 = []

    p1 = QuestionP1.objects.filter(year=2021)
    p2 = QuestionP1.objects.filter(year=2020)
    p3 = QuestionP1.objects.filter(year=2019)
    p4 = QuestionP1.objects.filter(year=20190)
    p5 = QuestionP1.objects.filter(year=2018)
    p6 = QuestionP1.objects.filter(year=20180)

    for q in p1:
        p12021.append(q)
    for q in p2:
        p12020.append(q)
    for q in p3:
        p12019.append(q)
    for q in p4:
        p120190.append(q)
    for q in p5:
        p12018.append(q)
    for q in p6:
        p120180.append(q)

    return render(request, 'upload_top1.html',
                {"q2021":p12021, "q2020":p12020, "q2019":p12019,
                "q20190":p120190, "q2018":p12018, "q20180":p120180}
    )

@login_required(login_url="signin")
def upload_top2(request):

    p22021 = []
    p22020 = []
    p22019 = []
    p220190 = []
    p22018 = []
    p220180 = []

    p1 = QuestionP2.objects.filter(year=2021)
    p2 = QuestionP2.objects.filter(year=2020)
    p3 = QuestionP2.objects.filter(year=2019)
    p4 = QuestionP2.objects.filter(year=20190)
    p5 = QuestionP2.objects.filter(year=2018)
    p6 = QuestionP2.objects.filter(year=20180)

    for q in p1:
        p22021.append(q)
    for q in p2:
        p22020.append(q)
    for q in p3:
        p22019.append(q)
    for q in p4:
        p220190.append(q)
    for q in p5:
        p22018.append(q)
    for q in p6:
        p220180.append(q)

    return render(request, 'upload_top2.html', {"q2021":p22021, "q2020":p22020, "q2019":p22019, "q20190":p220190, "q2018":p22018, "q20180":p220180})

@login_required(login_url="signin")
def upload_top3(request):

    p32021 = []
    p32020 = []
    p32019 = []
    p320190 = []
    p32018 = []
    p320180 = []

    p1 = QuestionP3.objects.filter(year=2021)
    p2 = QuestionP3.objects.filter(year=2020)
    p3 = QuestionP3.objects.filter(year=2019)
    p4 = QuestionP3.objects.filter(year=20190)
    p5 = QuestionP3.objects.filter(year=2018)
    p6 = QuestionP3.objects.filter(year=20180)

    for q in p1:
        p32021.append(q)
    for q in p2:
        p32020.append(q)
    for q in p3:
        p32019.append(q)
    for q in p4:
        p320190.append(q)
    for q in p5:
        p32018.append(q)
    for q in p6:
        p320180.append(q)

    return render(request, 'upload_top3.html', {"q2021":p32021, "q2020":p32020, "q2019":p32019, "q20190":p320190, "q2018":p32018, "q20180":p320180})


@login_required(login_url="signin")
def analysisp1(request):

    tri = []
    Triangle = QuestionP1.objects.filter(topic="Triangle")
    for q in Triangle:

        tri.append(q)

    pro = []
    Probability = QuestionP1.objects.filter(topic="Probability")
    for q in Probability:
        pro.append(q)

    sta = []
    Statistics = QuestionP1.objects.filter(topic="Statistics")
    for q in Statistics:
        sta.append(q)

    geo = []
    Geometry = QuestionP1.objects.filter(topic="Geometry")
    for q in Geometry:
        geo.append(q)


    gra = []
    Graph = QuestionP1.objects.filter(topic="Graph")
    for q in Graph:
        gra.append(q)

    num = []
    Numbers = QuestionP1.objects.filter(topic="Numbers")
    for q in Numbers:
        num.append(q)

    alg = []
    Algebra = QuestionP1.objects.filter(topic="Algebra")
    for q in Algebra:
        alg.append(q)

    rat = []
    Ratio = QuestionP1.objects.filter(topic="Ratio")
    for q in Ratio:
        rat.append(q)

    ine = []
    Inequality = QuestionP1.objects.filter(topic="Inequality")
    for q in Inequality:
        ine.append(q)

    int = []
    Interest = QuestionP1.objects.filter(topic="Interest")
    for q in Interest:
        int.append(q)

    den = []
    Density = QuestionP1.objects.filter(topic="Density")
    for q in Density:
        den.append(q)

    vec = []
    Vectors = QuestionP1.objects.filter(topic="Vectors")
    for q in Vectors:
        vec.append(q)

    const = 67

    #Percentage

    trip = round(((len(tri) / const) * 100), 2)
    prop = round(((len(pro) / const) * 100), 2)
    stap = round(((len(sta) / const) * 100), 2)

    geop = round(((len(geo) / const) * 100), 2)
    grap = round(((len(gra) / const) * 100), 2)
    nump = round(((len(num) / const) * 100), 2)

    algp = round(((len(alg) / const) * 100), 2)
    ratp = round(((len(rat) / const) * 100), 2)
    inep = round(((len(ine) / const) * 100), 2)

    intp = round(((len(int) / const) * 100), 2)
    denp = round(((len(den) / const) * 100), 2)
    vecp = round(((len(vec) / const) * 100), 2)

    #Marks

    mtri = []
    Triangle = QuestionP1.objects.filter(topic="Triangle")
    for q in Triangle:
        mtri.append(q.marks)

    mpro = []
    Probability = QuestionP1.objects.filter(topic="Probability")
    for q in Probability:
        mpro.append(q.marks)

    msta = []
    Statistics = QuestionP1.objects.filter(topic="Statistics")
    for q in Statistics:
        msta.append(q.marks)

    mgeo = []
    Geometry = QuestionP1.objects.filter(topic="Geometry")
    for q in Geometry:
        mgeo.append(q.marks)

    mgra = []
    Graph = QuestionP1.objects.filter(topic="Graph")
    for q in Graph:
        mgra.append(q.marks)

    mnum = []
    Numbers = QuestionP1.objects.filter(topic="Numbers")
    for q in Numbers:
        mnum.append(q.marks)

    malg = []
    Algebra = QuestionP1.objects.filter(topic="Algebra")
    for q in Algebra:
        malg.append(q.marks)

    mrat = []
    Ratio = QuestionP1.objects.filter(topic="Ratio")
    for q in Ratio:
        mrat.append(q.marks)

    mine = []
    Inequality = QuestionP1.objects.filter(topic="Inequality")
    for q in Inequality:
        mine.append(q.marks)

    mint = []
    Interest = QuestionP1.objects.filter(topic="Interest")
    for q in Interest:
        mint.append(q.marks)

    mden = []
    Density = QuestionP1.objects.filter(topic="Density")
    for q in Density:
        mden.append(q.marks)

    mvec = []
    Vectors = QuestionP1.objects.filter(topic="Vectors")
    for q in Vectors:
        mvec.append(q.marks)

    cm = 3 * 80

    ptri = round((sum(mtri) / cm) * 100, 2)
    ppro = round((sum(mpro) / cm) * 100, 2)
    psta = round((sum(msta) / cm) * 100, 2)
    pgeo = round((sum(mgeo) / cm) * 100, 2)
    pgra = round((sum(mgra) / cm) * 100, 2)
    pnum = round((sum(mnum) / cm) * 100, 2)
    palg = round((sum(malg) / cm) * 100, 2)
    prat = round((sum(mrat) / cm) * 100, 2)
    pine = round((sum(mine) / cm) * 100, 2)
    pint = round((sum(mint) / cm) * 100, 2)
    pden = round((sum(mden) / cm) * 100, 2)
    pvec = round((sum(mvec) / cm) * 100, 2)

    ttri = []
    tpro = []
    tsta = []
    tgeo = []
    tgra = []
    tnum = []
    talg = []
    trat = []
    tine = []
    tint = []
    tden = []
    tvec = []

    ttri2 = []
    tpro2 = []
    tsta2 = []
    tgeo2 = []
    tgra2 = []
    tnum2 = []
    talg2 = []
    trat2 = []
    tine2 = []
    tint2 = []
    tden2 = []
    tvec2 = []

    ttri3 = []
    tpro3 = []
    tsta3 = []
    tgeo3 = []
    tgra3 = []
    tnum3 = []
    talg3 = []
    trat3 = []
    tine3 = []
    tint3 = []
    tden3 = []
    tvec3 = []

    ttri4 = []
    tpro4 = []
    tsta4 = []
    tgeo4 = []
    tgra4 = []
    tnum4 = []
    talg4 = []
    trat4 = []
    tine4 = []
    tint4 = []
    tden4 = []
    tvec4 = []

    ttri5 = []
    tpro5 = []
    tsta5 = []
    tgeo5 = []
    tgra5 = []
    tnum5 = []
    talg5 = []
    trat5 = []
    tine5 = []
    tint5 = []
    tden5 = []
    tvec5 = []

    ttri6 = []
    tpro6 = []
    tsta6 = []
    tgeo6 = []
    tgra6 = []
    tnum6 = []
    talg6 = []
    trat6 = []
    tine6 = []
    tint6 = []
    tden6 = []
    tvec6 = []

    ttri7 = []
    tpro7 = []
    tsta7 = []
    tgeo7 = []
    tgra7 = []
    tnum7 = []
    talg7 = []
    trat7 = []
    tine7 = []
    tint7 = []
    tden7 = []
    tvec7 = []

    ttri8 = []
    tpro8 = []
    tsta8 = []
    tgeo8 = []
    tgra8 = []
    tnum8 = []
    talg8 = []
    trat8 = []
    tine8 = []
    tint8 = []
    tden8 = []
    tvec8 = []

    ttri9 = []
    tpro9 = []
    tsta9 = []
    tgeo9 = []
    tgra9 = []
    tnum9 = []
    talg9 = []
    trat9 = []
    tine9 = []
    tint9 = []
    tden9 = []
    tvec9 = []

    ttri10 = []
    tpro10 = []
    tsta10 = []
    tgeo10 = []
    tgra10 = []
    tnum10 = []
    talg10 = []
    trat10 = []
    tine10 = []
    tint10 = []
    tden10 = []
    tvec10 = []

    ttri11 = []
    tpro11 = []
    tsta11 = []
    tgeo11 = []
    tgra11 = []
    tnum11 = []
    talg11 = []
    trat11 = []
    tine11 = []
    tint11 = []
    tden11 = []
    tvec11 = []


    ttri12 = []
    tpro12 = []
    tsta12 = []
    tgeo12 = []
    tgra12 = []
    tnum12 = []
    talg12 = []
    trat12 = []
    tine12 = []
    tint12 = []
    tden12 = []
    tvec12 = []


    n1 = QuestionP1.objects.filter(number=1)
    n2 = QuestionP1.objects.filter(number=2)
    n3 = QuestionP1.objects.filter(number=3)
    n4 = QuestionP1.objects.filter(number=4)
    n5 = QuestionP1.objects.filter(number=5)
    n6 = QuestionP1.objects.filter(number=6)
    n7 = QuestionP1.objects.filter(number=7)
    n8 = QuestionP1.objects.filter(number=8)
    n9 = QuestionP1.objects.filter(number=9)
    n10 = QuestionP1.objects.filter(number=10)
    n11 = QuestionP1.objects.filter(number=11)
    n12 = QuestionP1.objects.filter(number=12)

    for q in n1:
        if q.topic == 'Triangle':
            ttri.append(1)
        if q.topic == 'Probabilty':
            tpro.append(1)
        if q.topic == 'Statistics':
            tsta.append(1)
        if q.topic == 'Geometry':
            tgeo.append(1)
        if q.topic == 'Graph':
            tgra.append(1)
        if q.topic == 'Number':
            tnum.append(1)
        if q.topic == 'Algebra':
            talg.append(1)
        if q.topic == 'Ratio':
            trat.append(1)
        if q.topic == 'Inequality':
            tine.append(1)
        if q.topic == 'Interest':
            tint.append(1)
        if q.topic == 'Density':
            tden.append(1)
        if q.topic == 'Vectors':
            tvec.append(1)
    for q in n2:
        if q.topic == 'Triangle':
            ttri2.append(1)
        if q.topic == 'Probabilty':
            tpro2.append(1)
        if q.topic == 'Statistics':
            tsta2.append(1)
        if q.topic == 'Geometry':
            tgeo2.append(1)
        if q.topic == 'Graph':
            tgra2.append(1)
        if q.topic == 'Number':
            tnum2.append(1)
        if q.topic == 'Algebra':
            talg2.append(1)
        if q.topic == 'Ratio':
            trat2.append(1)
        if q.topic == 'Inequality':
            tine2.append(1)
        if q.topic == 'Interest':
            tint2.append(1)
        if q.topic == 'Density':
            tden2.append(1)
        if q.topic == 'Vectors':
            tvec2.append(1)
    for q in n3:
        if q.topic == 'Triangle':
            ttri3.append(1)
        if q.topic == 'Probabilty':
            tpro3.append(1)
        if q.topic == 'Statistics':
            tsta3.append(1)
        if q.topic == 'Geometry':
            tgeo3.append(1)
        if q.topic == 'Graph':
            tgra3.append(1)
        if q.topic == 'Number':
            tnum3.append(1)
        if q.topic == 'Algebra':
            talg3.append(1)
        if q.topic == 'Ratio':
            trat3.append(1)
        if q.topic == 'Inequality':
            tine3.append(1)
        if q.topic == 'Interest':
            tint3.append(1)
        if q.topic == 'Density':
            tden3.append(1)
        if q.topic == 'Vectors':
            tvec3.append(1)
    for q in n4:
        if q.topic == 'Triangle':
            ttri4.append(1)
        if q.topic == 'Probabilty':
            tpro4.append(1)
        if q.topic == 'Statistics':
            tsta4.append(1)
        if q.topic == 'Geometry':
            tgeo4.append(1)
        if q.topic == 'Graph':
            tgra4.append(1)
        if q.topic == 'Number':
            tnum4.append(1)
        if q.topic == 'Algebra':
            talg4.append(1)
        if q.topic == 'Ratio':
            trat4.append(1)
        if q.topic == 'Inequality':
            tine4.append(1)
        if q.topic == 'Interest':
            tint4.append(1)
        if q.topic == 'Density':
            tden4.append(1)
        if q.topic == 'Vectors':
            tvec4.append(1)
    for q in n5:
        if q.topic == 'Triangle':
            ttri5.append(1)
        if q.topic == 'Probabilty':
            tpro5.append(1)
        if q.topic == 'Statistics':
            tsta5.append(1)
        if q.topic == 'Geometry':
            tgeo5.append(1)
        if q.topic == 'Graph':
            tgra5.append(1)
        if q.topic == 'Number':
            tnum5.append(1)
        if q.topic == 'Algebra':
            talg5.append(1)
        if q.topic == 'Ratio':
            trat5.append(1)
        if q.topic == 'Inequality':
            tine5.append(1)
        if q.topic == 'Interest':
            tint5.append(1)
        if q.topic == 'Density':
            tden5.append(1)
        if q.topic == 'Vectors':
            tvec5.append(1)
    for q in n6:
        if q.topic == 'Triangle':
            ttri6.append(1)
        if q.topic == 'Probabilty':
            tpro6.append(1)
        if q.topic == 'Statistics':
            tsta6.append(1)
        if q.topic == 'Geometry':
            tgeo6.append(1)
        if q.topic == 'Graph':
            tgra6.append(1)
        if q.topic == 'Number':
            tnum6.append(1)
        if q.topic == 'Algebra':
            talg6.append(1)
        if q.topic == 'Ratio':
            trat6.append(1)
        if q.topic == 'Inequality':
            tine6.append(1)
        if q.topic == 'Interest':
            tint6.append(1)
        if q.topic == 'Density':
            tden6.append(1)
        if q.topic == 'Vectors':
            tvec6.append(1)
    for q in n7:
        if q.topic == 'Triangle':
            ttri7.append(1)
        if q.topic == 'Probabilty':
            tpro7.append(1)
        if q.topic == 'Statistics':
            tsta7.append(1)
        if q.topic == 'Geometry':
            tgeo7.append(1)
        if q.topic == 'Graph':
            tgra7.append(1)
        if q.topic == 'Number':
            tnum7.append(1)
        if q.topic == 'Algebra':
            talg7.append(1)
        if q.topic == 'Ratio':
            trat7.append(1)
        if q.topic == 'Inequality':
            tine7.append(1)
        if q.topic == 'Interest':
            tint7.append(1)
        if q.topic == 'Density':
            tden7.append(1)
        if q.topic == 'Vectors':
            tvec7.append(1)
    for q in n8:
        if q.topic == 'Triangle':
            ttri8.append(1)
        if q.topic == 'Probabilty':
            tpro8.append(1)
        if q.topic == 'Statistics':
            tsta8.append(1)
        if q.topic == 'Geometry':
            tgeo8.append(1)
        if q.topic == 'Graph':
            tgra8.append(1)
        if q.topic == 'Number':
            tnum8.append(1)
        if q.topic == 'Algebra':
            talg8.append(1)
        if q.topic == 'Ratio':
            trat8.append(1)
        if q.topic == 'Inequality':
            tine8.append(1)
        if q.topic == 'Interest':
            tint8.append(1)
        if q.topic == 'Density':
            tden8.append(1)
        if q.topic == 'Vectors':
            tvec8.append(1)
    for q in n9:
        if q.topic == 'Triangle':
            ttri9.append(1)
        if q.topic == 'Probabilty':
            tpro9.append(1)
        if q.topic == 'Statistics':
            tsta9.append(1)
        if q.topic == 'Geometry':
            tgeo9.append(1)
        if q.topic == 'Graph':
            tgra9.append(1)
        if q.topic == 'Number':
            tnum9.append(1)
        if q.topic == 'Algebra':
            talg9.append(1)
        if q.topic == 'Ratio':
            trat9.append(1)
        if q.topic == 'Inequality':
            tine9.append(1)
        if q.topic == 'Interest':
            tint9.append(1)
        if q.topic == 'Density':
            tden9.append(1)
        if q.topic == 'Vectors':
            tvec9.append(1)
    for q in n10:
        if q.topic == 'Triangle':
            ttri10.append(1)
        if q.topic == 'Probabilty':
            tpro10.append(1)
        if q.topic == 'Statistics':
            tsta10.append(1)
        if q.topic == 'Geometry':
            tgeo10.append(1)
        if q.topic == 'Graph':
            tgra10.append(1)
        if q.topic == 'Number':
            tnum10.append(1)
        if q.topic == 'Algebra':
            talg10.append(1)
        if q.topic == 'Ratio':
            trat10.append(1)
        if q.topic == 'Inequality':
            tine10.append(1)
        if q.topic == 'Interest':
            tint10.append(1)
        if q.topic == 'Density':
            tden10.append(1)
        if q.topic == 'Vectors':
            tvec10.append(1)
    for q in n11:
        if q.topic == 'Triangle':
            ttri11.append(1)
        if q.topic == 'Probabilty':
            tpro11.append(1)
        if q.topic == 'Statistics':
            tsta11.append(1)
        if q.topic == 'Geometry':
            tgeo11.append(1)
        if q.topic == 'Graph':
            tgra11.append(1)
        if q.topic == 'Number':
            tnum11.append(1)
        if q.topic == 'Algebra':
            talg11.append(1)
        if q.topic == 'Ratio':
            trat11.append(1)
        if q.topic == 'Inequality':
            tine11.append(1)
        if q.topic == 'Interest':
            tint11.append(1)
        if q.topic == 'Density':
            tden11.append(1)
        if q.topic == 'Vectors':
            tvec11.append(1)
    for q in n12:
        if q.topic == 'Triangle':
            ttri12.append(1)
        if q.topic == 'Probabilty':
            tpro12.append(1)
        if q.topic == 'Statistics':
            tsta12.append(1)
        if q.topic == 'Geometry':
            tgeo12.append(1)
        if q.topic == 'Graph':
            tgra12.append(1)
        if q.topic == 'Number':
            tnum12.append(1)
        if q.topic == 'Algebra':
            talg12.append(1)
        if q.topic == 'Ratio':
            trat12.append(1)
        if q.topic == 'Inequality':
            tine12.append(1)
        if q.topic == 'Interest':
            tint12.append(1)
        if q.topic == 'Density':
            tden12.append(1)
        if q.topic == 'Vectors':
            tvec12.append(1)

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    return render(request, 'analysisp1.html',
                  {'tri':tri, 'pro':pro, 'sta':sta, 'geo':geo,
                   'gra':gra, 'num':num, 'alg':alg, 'rat':rat,
                   'ine':ine, 'int':int, 'den':den, 'vec':vec,

                   'trip':trip, 'prop':prop, 'stap':stap, 'geop':geop,
                   'grap':grap, 'nump':nump, 'algp':algp, 'ratp':ratp,
                   'inep':inep, 'intp':intp, 'denp':denp, 'vecp':vecp,

                   'mtri':sum(mtri), 'mpro':sum(mpro), 'msta':sum(msta), 'mgeo':sum(mgeo),
                   'mgra':sum(mgra), 'mnum':sum(mnum), 'malg':sum(malg), 'mrat':sum(mrat),
                   'mine':sum(mine), 'mint':sum(mint), 'mden':sum(mden), 'mvec':sum(mvec),

                   'ptri':ptri, 'ppro':ppro, 'psta':psta, 'pgeo':pgeo, 'pgra':pgra, 'pnum':pnum,
                   'palg':palg, 'prat':prat, 'pine':pine, 'pint':pint, 'pden':pden, 'pvec':pvec,

                   't1':sum(ttri), 'p1':sum(tpro), 's1':sum(tsta), 'g1':sum(tgeo), 'gr1':sum(tgra), 'n1':sum(tnum),
                   'a1':sum(talg), 'r1':sum(trat), 'i1':sum(tine), 'in1':sum(tint), 'd1':sum(tden), 'v1':sum(tvec),

                   't2':sum(ttri2), 'p2':sum(tpro2), 's2':sum(tsta2), 'g2':sum(tgeo2), 'gr2':sum(tgra2), 'n2':sum(tnum2),
                   'a2':sum(talg2), 'r2':sum(trat2), 'i2':sum(tine2), 'in2':sum(tint2), 'd2':sum(tden2), 'v2':sum(tvec2),

                   't3':sum(ttri3), 'p3':sum(tpro3), 's3':sum(tsta3), 'g3':sum(tgeo3), 'gr3':sum(tgra3), 'n3':sum(tnum3),
                   'a3':sum(talg3), 'r3':sum(trat3), 'i3':sum(tine3), 'in3':sum(tint3), 'd3':sum(tden3), 'v3':sum(tvec3),

                   't4':sum(ttri4), 'p4':sum(tpro4), 's4':sum(tsta4), 'g4':sum(tgeo4), 'gr4':sum(tgra4), 'n4':sum(tnum4),
                   'a4':sum(talg4), 'r4':sum(trat4), 'i4':sum(tine4), 'in4':sum(tint4), 'd4':sum(tden4), 'v4':sum(tvec4),

                   't5':sum(ttri5), 'p5':sum(tpro5), 's5':sum(tsta5), 'g5':sum(tgeo5), 'gr5':sum(tgra5), 'n5':sum(tnum5),
                   'a5':sum(talg5), 'r5':sum(trat5), 'i5':sum(tine5), 'in5':sum(tint5), 'd5':sum(tden5), 'v5':sum(tvec5),

                    't6': sum(ttri6), 'p6': sum(tpro6), 's6': sum(tsta6), 'g6': sum(tgeo6), 'gr6': sum(tgra6), 'n6': sum(tnum6),
                    'a6': sum(talg6), 'r6': sum(trat6), 'i6': sum(tine6), 'in6': sum(tint6), 'd6': sum(tden6), 'v6': sum(tvec6),

                    't7': sum(ttri7), 'p7': sum(tpro7), 's7': sum(tsta7), 'g7': sum(tgeo7), 'gr7': sum(tgra7), 'n7': sum(tnum7),
                    'a7': sum(talg7), 'r7': sum(trat7), 'i7': sum(tine7), 'in7': sum(tint7), 'd7': sum(tden7), 'v7': sum(tvec7),

                    't8': sum(ttri8), 'p8': sum(tpro8), 's8': sum(tsta8), 'g8': sum(tgeo8), 'gr8': sum(tgra8), 'n8': sum(tnum8),
                    'a8': sum(talg8), 'r8': sum(trat8), 'i8': sum(tine8), 'in8': sum(tint8), 'd8': sum(tden8), 'v8': sum(tvec8),

                    't9': sum(ttri9), 'p9': sum(tpro9), 's9': sum(tsta9), 'g9': sum(tgeo9), 'gr9': sum(tgra9), 'n9': sum(tnum9),
                    'a9': sum(talg9), 'r9': sum(trat9), 'i9': sum(tine9), 'in9': sum(tint9), 'd9': sum(tden9), 'v9': sum(tvec9),

                    't10': sum(ttri10), 'p10': sum(tpro10), 's10': sum(tsta10), 'g10': sum(tgeo10), 'gr10': sum(tgra10), 'n10': sum(tnum10),
                    'a10': sum(talg10), 'r10': sum(trat10), 'i10': sum(tine10), 'in10': sum(tint10), 'd10': sum(tden10), 'v10': sum(tvec10),

                    't11': sum(ttri11), 'p11': sum(tpro11), 's11': sum(tsta11), 'g11': sum(tgeo11), 'gr11': sum(tgra11), 'n11': sum(tnum11),
                    'a11': sum(talg11), 'r11': sum(trat11), 'i11': sum(tine11), 'in11': sum(tint11), 'd11': sum(tden11), 'v11': sum(tvec11),

                    't12': sum(ttri12), 'p12': sum(tpro12), 's12': sum(tsta12), 'g12': sum(tgeo12), 'gr12': sum(tgra12), 'n12': sum(tnum12),
                    'a12': sum(talg12), 'r12': sum(trat12), 'i12': sum(tine12), 'in12': sum(tint12), 'd12': sum(tden12), 'v12': sum(tvec12),

                    'user':user_object,
                    'data':user_profile,})

@login_required(login_url="signin")
def analysisp2(request):

    tri = []
    Triangle = QuestionP2.objects.filter(topic="Triangle")
    for q in Triangle:

        tri.append(q)

    pro = []
    Probability = QuestionP2.objects.filter(topic="Probability")
    for q in Probability:
        pro.append(q)

    sta = []
    Statistics = QuestionP2.objects.filter(topic="Statistics")
    for q in Statistics:
        sta.append(q)

    geo = []
    Geometry = QuestionP2.objects.filter(topic="Geometry")
    for q in Geometry:
        geo.append(q)


    gra = []
    Graph = QuestionP2.objects.filter(topic="Graph")
    for q in Graph:
        gra.append(q)

    num = []
    Numbers = QuestionP2.objects.filter(topic="Numbers")
    for q in Numbers:
        num.append(q)

    alg = []
    Algebra = QuestionP2.objects.filter(topic="Algebra")
    for q in Algebra:
        alg.append(q)

    rat = []
    Ratio = QuestionP2.objects.filter(topic="Ratio")
    for q in Ratio:
        rat.append(q)

    ine = []
    Inequality = QuestionP2.objects.filter(topic="Inequality")
    for q in Inequality:
        ine.append(q)

    int = []
    Interest = QuestionP2.objects.filter(topic="Interest")
    for q in Interest:
        int.append(q)

    den = []
    Density = QuestionP2.objects.filter(topic="Density")
    for q in Density:
        den.append(q)

    vec = []
    Vectors = QuestionP2.objects.filter(topic="Vectors")
    for q in Vectors:
        vec.append(q)

    const = 121

    #Percentage

    trip = round(((len(tri) / const) * 100), 2)
    prop = round(((len(pro) / const) * 100), 2)
    stap = round(((len(sta) / const) * 100), 2)

    geop = round(((len(geo) / const) * 100), 2)
    grap = round(((len(gra) / const) * 100), 2)
    nump = round(((len(num) / const) * 100), 2)

    algp = round(((len(alg) / const) * 100), 2)
    ratp = round(((len(rat) / const) * 100), 2)
    inep = round(((len(ine) / const) * 100), 2)

    intp = round(((len(int) / const) * 100), 2)
    denp = round(((len(den) / const) * 100), 2)
    vecp = round(((len(vec) / const) * 100), 2)

    #Marks

    mtri = []
    Triangle = QuestionP2.objects.filter(topic="Triangle")
    for q in Triangle:
        mtri.append(q.marks)

    mpro = []
    Probability = QuestionP2.objects.filter(topic="Probability")
    for q in Probability:
        mpro.append(q.marks)

    msta = []
    Statistics = QuestionP2.objects.filter(topic="Statistics")
    for q in Statistics:
        msta.append(q.marks)

    mgeo = []
    Geometry = QuestionP2.objects.filter(topic="Geometry")
    for q in Geometry:
        mgeo.append(q.marks)

    mgra = []
    Graph = QuestionP2.objects.filter(topic="Graph")
    for q in Graph:
        mgra.append(q.marks)

    mnum = []
    Numbers = QuestionP2.objects.filter(topic="Numbers")
    for q in Numbers:
        mnum.append(q.marks)

    malg = []
    Algebra = QuestionP2.objects.filter(topic="Algebra")
    for q in Algebra:
        malg.append(q.marks)

    mrat = []
    Ratio = QuestionP2.objects.filter(topic="Ratio")
    for q in Ratio:
        mrat.append(q.marks)

    mine = []
    Inequality = QuestionP2.objects.filter(topic="Inequality")
    for q in Inequality:
        mine.append(q.marks)

    mint = []
    Interest = QuestionP2.objects.filter(topic="Interest")
    for q in Interest:
        mint.append(q.marks)

    mden = []
    Density = QuestionP2.objects.filter(topic="Density")
    for q in Density:
        mden.append(q.marks)

    mvec = []
    Vectors = QuestionP2.objects.filter(topic="Vectors")
    for q in Vectors:
        mvec.append(q.marks)

    cm = 6 * 80

    ptri = round((sum(mtri) / cm) * 100, 2)
    ppro = round((sum(mpro) / cm) * 100, 2)
    psta = round((sum(msta) / cm) * 100, 2)
    pgeo = round((sum(mgeo) / cm) * 100, 2)
    pgra = round((sum(mgra) / cm) * 100, 2)
    pnum = round((sum(mnum) / cm) * 100, 2)
    palg = round((sum(malg) / cm) * 100, 2)
    prat = round((sum(mrat) / cm) * 100, 2)
    pine = round((sum(mine) / cm) * 100, 2)
    pint = round((sum(mint) / cm) * 100, 2)
    pden = round((sum(mden) / cm) * 100, 2)
    pvec = round((sum(mvec) / cm) * 100, 2)

    ttri = []
    tpro = []
    tsta = []
    tgeo = []
    tgra = []
    tnum = []
    talg = []
    trat = []
    tine = []
    tint = []
    tden = []
    tvec = []

    ttri2 = []
    tpro2 = []
    tsta2 = []
    tgeo2 = []
    tgra2 = []
    tnum2 = []
    talg2 = []
    trat2 = []
    tine2 = []
    tint2 = []
    tden2 = []
    tvec2 = []

    ttri3 = []
    tpro3 = []
    tsta3 = []
    tgeo3 = []
    tgra3 = []
    tnum3 = []
    talg3 = []
    trat3 = []
    tine3 = []
    tint3 = []
    tden3 = []
    tvec3 = []

    ttri4 = []
    tpro4 = []
    tsta4 = []
    tgeo4 = []
    tgra4 = []
    tnum4 = []
    talg4 = []
    trat4 = []
    tine4 = []
    tint4 = []
    tden4 = []
    tvec4 = []

    ttri5 = []
    tpro5 = []
    tsta5 = []
    tgeo5 = []
    tgra5 = []
    tnum5 = []
    talg5 = []
    trat5 = []
    tine5 = []
    tint5 = []
    tden5 = []
    tvec5 = []

    ttri6 = []
    tpro6 = []
    tsta6 = []
    tgeo6 = []
    tgra6 = []
    tnum6 = []
    talg6 = []
    trat6 = []
    tine6 = []
    tint6 = []
    tden6 = []
    tvec6 = []

    ttri7 = []
    tpro7 = []
    tsta7 = []
    tgeo7 = []
    tgra7 = []
    tnum7 = []
    talg7 = []
    trat7 = []
    tine7 = []
    tint7 = []
    tden7 = []
    tvec7 = []

    ttri8 = []
    tpro8 = []
    tsta8 = []
    tgeo8 = []
    tgra8 = []
    tnum8 = []
    talg8 = []
    trat8 = []
    tine8 = []
    tint8 = []
    tden8 = []
    tvec8 = []

    ttri9 = []
    tpro9 = []
    tsta9 = []
    tgeo9 = []
    tgra9 = []
    tnum9 = []
    talg9 = []
    trat9 = []
    tine9 = []
    tint9 = []
    tden9 = []
    tvec9 = []

    ttri10 = []
    tpro10 = []
    tsta10 = []
    tgeo10 = []
    tgra10 = []
    tnum10 = []
    talg10 = []
    trat10 = []
    tine10 = []
    tint10 = []
    tden10 = []
    tvec10 = []

    ttri11 = []
    tpro11 = []
    tsta11 = []
    tgeo11 = []
    tgra11 = []
    tnum11 = []
    talg11 = []
    trat11 = []
    tine11 = []
    tint11 = []
    tden11 = []
    tvec11 = []


    ttri12 = []
    tpro12 = []
    tsta12 = []
    tgeo12 = []
    tgra12 = []
    tnum12 = []
    talg12 = []
    trat12 = []
    tine12 = []
    tint12 = []
    tden12 = []
    tvec12 = []


    n1 = QuestionP2.objects.filter(number=1)
    n2 = QuestionP2.objects.filter(number=2)
    n3 = QuestionP2.objects.filter(number=3)
    n4 = QuestionP2.objects.filter(number=4)
    n5 = QuestionP2.objects.filter(number=5)
    n6 = QuestionP2.objects.filter(number=6)
    n7 = QuestionP2.objects.filter(number=7)
    n8 = QuestionP2.objects.filter(number=8)
    n9 = QuestionP2.objects.filter(number=9)
    n10 = QuestionP2.objects.filter(number=10)
    n11 = QuestionP2.objects.filter(number=11)
    n12 = QuestionP2.objects.filter(number=12)

    for q in n1:
        if q.topic == 'Triangle':
            ttri.append(1)
        if q.topic == 'Probabilty':
            tpro.append(1)
        if q.topic == 'Statistics':
            tsta.append(1)
        if q.topic == 'Geometry':
            tgeo.append(1)
        if q.topic == 'Graph':
            tgra.append(1)
        if q.topic == 'Number':
            tnum.append(1)
        if q.topic == 'Algebra':
            talg.append(1)
        if q.topic == 'Ratio':
            trat.append(1)
        if q.topic == 'Inequality':
            tine.append(1)
        if q.topic == 'Interest':
            tint.append(1)
        if q.topic == 'Density':
            tden.append(1)
        if q.topic == 'Vectors':
            tvec.append(1)
    for q in n2:
        if q.topic == 'Triangle':
            ttri2.append(1)
        if q.topic == 'Probabilty':
            tpro2.append(1)
        if q.topic == 'Statistics':
            tsta2.append(1)
        if q.topic == 'Geometry':
            tgeo2.append(1)
        if q.topic == 'Graph':
            tgra2.append(1)
        if q.topic == 'Number':
            tnum2.append(1)
        if q.topic == 'Algebra':
            talg2.append(1)
        if q.topic == 'Ratio':
            trat2.append(1)
        if q.topic == 'Inequality':
            tine2.append(1)
        if q.topic == 'Interest':
            tint2.append(1)
        if q.topic == 'Density':
            tden2.append(1)
        if q.topic == 'Vectors':
            tvec2.append(1)
    for q in n3:
        if q.topic == 'Triangle':
            ttri3.append(1)
        if q.topic == 'Probabilty':
            tpro3.append(1)
        if q.topic == 'Statistics':
            tsta3.append(1)
        if q.topic == 'Geometry':
            tgeo3.append(1)
        if q.topic == 'Graph':
            tgra3.append(1)
        if q.topic == 'Number':
            tnum3.append(1)
        if q.topic == 'Algebra':
            talg3.append(1)
        if q.topic == 'Ratio':
            trat3.append(1)
        if q.topic == 'Inequality':
            tine3.append(1)
        if q.topic == 'Interest':
            tint3.append(1)
        if q.topic == 'Density':
            tden3.append(1)
        if q.topic == 'Vectors':
            tvec3.append(1)
    for q in n4:
        if q.topic == 'Triangle':
            ttri4.append(1)
        if q.topic == 'Probabilty':
            tpro4.append(1)
        if q.topic == 'Statistics':
            tsta4.append(1)
        if q.topic == 'Geometry':
            tgeo4.append(1)
        if q.topic == 'Graph':
            tgra4.append(1)
        if q.topic == 'Number':
            tnum4.append(1)
        if q.topic == 'Algebra':
            talg4.append(1)
        if q.topic == 'Ratio':
            trat4.append(1)
        if q.topic == 'Inequality':
            tine4.append(1)
        if q.topic == 'Interest':
            tint4.append(1)
        if q.topic == 'Density':
            tden4.append(1)
        if q.topic == 'Vectors':
            tvec4.append(1)
    for q in n5:
        if q.topic == 'Triangle':
            ttri5.append(1)
        if q.topic == 'Probabilty':
            tpro5.append(1)
        if q.topic == 'Statistics':
            tsta5.append(1)
        if q.topic == 'Geometry':
            tgeo5.append(1)
        if q.topic == 'Graph':
            tgra5.append(1)
        if q.topic == 'Number':
            tnum5.append(1)
        if q.topic == 'Algebra':
            talg5.append(1)
        if q.topic == 'Ratio':
            trat5.append(1)
        if q.topic == 'Inequality':
            tine5.append(1)
        if q.topic == 'Interest':
            tint5.append(1)
        if q.topic == 'Density':
            tden5.append(1)
        if q.topic == 'Vectors':
            tvec5.append(1)
    for q in n6:
        if q.topic == 'Triangle':
            ttri6.append(1)
        if q.topic == 'Probabilty':
            tpro6.append(1)
        if q.topic == 'Statistics':
            tsta6.append(1)
        if q.topic == 'Geometry':
            tgeo6.append(1)
        if q.topic == 'Graph':
            tgra6.append(1)
        if q.topic == 'Number':
            tnum6.append(1)
        if q.topic == 'Algebra':
            talg6.append(1)
        if q.topic == 'Ratio':
            trat6.append(1)
        if q.topic == 'Inequality':
            tine6.append(1)
        if q.topic == 'Interest':
            tint6.append(1)
        if q.topic == 'Density':
            tden6.append(1)
        if q.topic == 'Vectors':
            tvec6.append(1)
    for q in n7:
        if q.topic == 'Triangle':
            ttri7.append(1)
        if q.topic == 'Probabilty':
            tpro7.append(1)
        if q.topic == 'Statistics':
            tsta7.append(1)
        if q.topic == 'Geometry':
            tgeo7.append(1)
        if q.topic == 'Graph':
            tgra7.append(1)
        if q.topic == 'Number':
            tnum7.append(1)
        if q.topic == 'Algebra':
            talg7.append(1)
        if q.topic == 'Ratio':
            trat7.append(1)
        if q.topic == 'Inequality':
            tine7.append(1)
        if q.topic == 'Interest':
            tint7.append(1)
        if q.topic == 'Density':
            tden7.append(1)
        if q.topic == 'Vectors':
            tvec7.append(1)
    for q in n8:
        if q.topic == 'Triangle':
            ttri8.append(1)
        if q.topic == 'Probabilty':
            tpro8.append(1)
        if q.topic == 'Statistics':
            tsta8.append(1)
        if q.topic == 'Geometry':
            tgeo8.append(1)
        if q.topic == 'Graph':
            tgra8.append(1)
        if q.topic == 'Number':
            tnum8.append(1)
        if q.topic == 'Algebra':
            talg8.append(1)
        if q.topic == 'Ratio':
            trat8.append(1)
        if q.topic == 'Inequality':
            tine8.append(1)
        if q.topic == 'Interest':
            tint8.append(1)
        if q.topic == 'Density':
            tden8.append(1)
        if q.topic == 'Vectors':
            tvec8.append(1)
    for q in n9:
        if q.topic == 'Triangle':
            ttri9.append(1)
        if q.topic == 'Probabilty':
            tpro9.append(1)
        if q.topic == 'Statistics':
            tsta9.append(1)
        if q.topic == 'Geometry':
            tgeo9.append(1)
        if q.topic == 'Graph':
            tgra9.append(1)
        if q.topic == 'Number':
            tnum9.append(1)
        if q.topic == 'Algebra':
            talg9.append(1)
        if q.topic == 'Ratio':
            trat9.append(1)
        if q.topic == 'Inequality':
            tine9.append(1)
        if q.topic == 'Interest':
            tint9.append(1)
        if q.topic == 'Density':
            tden9.append(1)
        if q.topic == 'Vectors':
            tvec9.append(1)
    for q in n10:
        if q.topic == 'Triangle':
            ttri10.append(1)
        if q.topic == 'Probabilty':
            tpro10.append(1)
        if q.topic == 'Statistics':
            tsta10.append(1)
        if q.topic == 'Geometry':
            tgeo10.append(1)
        if q.topic == 'Graph':
            tgra10.append(1)
        if q.topic == 'Number':
            tnum10.append(1)
        if q.topic == 'Algebra':
            talg10.append(1)
        if q.topic == 'Ratio':
            trat10.append(1)
        if q.topic == 'Inequality':
            tine10.append(1)
        if q.topic == 'Interest':
            tint10.append(1)
        if q.topic == 'Density':
            tden10.append(1)
        if q.topic == 'Vectors':
            tvec10.append(1)
    for q in n11:
        if q.topic == 'Triangle':
            ttri11.append(1)
        if q.topic == 'Probabilty':
            tpro11.append(1)
        if q.topic == 'Statistics':
            tsta11.append(1)
        if q.topic == 'Geometry':
            tgeo11.append(1)
        if q.topic == 'Graph':
            tgra11.append(1)
        if q.topic == 'Number':
            tnum11.append(1)
        if q.topic == 'Algebra':
            talg11.append(1)
        if q.topic == 'Ratio':
            trat11.append(1)
        if q.topic == 'Inequality':
            tine11.append(1)
        if q.topic == 'Interest':
            tint11.append(1)
        if q.topic == 'Density':
            tden11.append(1)
        if q.topic == 'Vectors':
            tvec11.append(1)
    for q in n12:
        if q.topic == 'Triangle':
            ttri12.append(1)
        if q.topic == 'Probabilty':
            tpro12.append(1)
        if q.topic == 'Statistics':
            tsta12.append(1)
        if q.topic == 'Geometry':
            tgeo12.append(1)
        if q.topic == 'Graph':
            tgra12.append(1)
        if q.topic == 'Number':
            tnum12.append(1)
        if q.topic == 'Algebra':
            talg12.append(1)
        if q.topic == 'Ratio':
            trat12.append(1)
        if q.topic == 'Inequality':
            tine12.append(1)
        if q.topic == 'Interest':
            tint12.append(1)
        if q.topic == 'Density':
            tden12.append(1)
        if q.topic == 'Vectors':
            tvec12.append(1)

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    return render(request, 'analysisp2.html',
                  {'tri':tri, 'pro':pro, 'sta':sta, 'geo':geo,
                   'gra':gra, 'num':num, 'alg':alg, 'rat':rat,
                   'ine':ine, 'int':int, 'den':den, 'vec':vec,

                   'trip':trip, 'prop':prop, 'stap':stap, 'geop':geop,
                   'grap':grap, 'nump':nump, 'algp':algp, 'ratp':ratp,
                   'inep':inep, 'intp':intp, 'denp':denp, 'vecp':vecp,

                   'mtri':sum(mtri), 'mpro':sum(mpro), 'msta':sum(msta), 'mgeo':sum(mgeo),
                   'mgra':sum(mgra), 'mnum':sum(mnum), 'malg':sum(malg), 'mrat':sum(mrat),
                   'mine':sum(mine), 'mint':sum(mint), 'mden':sum(mden), 'mvec':sum(mvec),

                   'ptri':ptri, 'ppro':ppro, 'psta':psta, 'pgeo':pgeo, 'pgra':pgra, 'pnum':pnum,
                   'palg':palg, 'prat':prat, 'pine':pine, 'pint':pint, 'pden':pden, 'pvec':pvec,

                   't1':sum(ttri), 'p1':sum(tpro), 's1':sum(tsta), 'g1':sum(tgeo), 'gr1':sum(tgra), 'n1':sum(tnum),
                   'a1':sum(talg), 'r1':sum(trat), 'i1':sum(tine), 'in1':sum(tint), 'd1':sum(tden), 'v1':sum(tvec),

                   't2':sum(ttri2), 'p2':sum(tpro2), 's2':sum(tsta2), 'g2':sum(tgeo2), 'gr2':sum(tgra2), 'n2':sum(tnum2),
                   'a2':sum(talg2), 'r2':sum(trat2), 'i2':sum(tine2), 'in2':sum(tint2), 'd2':sum(tden2), 'v2':sum(tvec2),

                   't3':sum(ttri3), 'p3':sum(tpro3), 's3':sum(tsta3), 'g3':sum(tgeo3), 'gr3':sum(tgra3), 'n3':sum(tnum3),
                   'a3':sum(talg3), 'r3':sum(trat3), 'i3':sum(tine3), 'in3':sum(tint3), 'd3':sum(tden3), 'v3':sum(tvec3),

                   't4':sum(ttri4), 'p4':sum(tpro4), 's4':sum(tsta4), 'g4':sum(tgeo4), 'gr4':sum(tgra4), 'n4':sum(tnum4),
                   'a4':sum(talg4), 'r4':sum(trat4), 'i4':sum(tine4), 'in4':sum(tint4), 'd4':sum(tden4), 'v4':sum(tvec4),

                   't5':sum(ttri5), 'p5':sum(tpro5), 's5':sum(tsta5), 'g5':sum(tgeo5), 'gr5':sum(tgra5), 'n5':sum(tnum5),
                   'a5':sum(talg5), 'r5':sum(trat5), 'i5':sum(tine5), 'in5':sum(tint5), 'd5':sum(tden5), 'v5':sum(tvec5),

                    't6': sum(ttri6), 'p6': sum(tpro6), 's6': sum(tsta6), 'g6': sum(tgeo6), 'gr6': sum(tgra6), 'n6': sum(tnum6),
                    'a6': sum(talg6), 'r6': sum(trat6), 'i6': sum(tine6), 'in6': sum(tint6), 'd6': sum(tden6), 'v6': sum(tvec6),

                    't7': sum(ttri7), 'p7': sum(tpro7), 's7': sum(tsta7), 'g7': sum(tgeo7), 'gr7': sum(tgra7), 'n7': sum(tnum7),
                    'a7': sum(talg7), 'r7': sum(trat7), 'i7': sum(tine7), 'in7': sum(tint7), 'd7': sum(tden7), 'v7': sum(tvec7),

                    't8': sum(ttri8), 'p8': sum(tpro8), 's8': sum(tsta8), 'g8': sum(tgeo8), 'gr8': sum(tgra8), 'n8': sum(tnum8),
                    'a8': sum(talg8), 'r8': sum(trat8), 'i8': sum(tine8), 'in8': sum(tint8), 'd8': sum(tden8), 'v8': sum(tvec8),

                    't9': sum(ttri9), 'p9': sum(tpro9), 's9': sum(tsta9), 'g9': sum(tgeo9), 'gr9': sum(tgra9), 'n9': sum(tnum9),
                    'a9': sum(talg9), 'r9': sum(trat9), 'i9': sum(tine9), 'in9': sum(tint9), 'd9': sum(tden9), 'v9': sum(tvec9),

                    't10': sum(ttri10), 'p10': sum(tpro10), 's10': sum(tsta10), 'g10': sum(tgeo10), 'gr10': sum(tgra10), 'n10': sum(tnum10),
                    'a10': sum(talg10), 'r10': sum(trat10), 'i10': sum(tine10), 'in10': sum(tint10), 'd10': sum(tden10), 'v10': sum(tvec10),

                    't11': sum(ttri11), 'p11': sum(tpro11), 's11': sum(tsta11), 'g11': sum(tgeo11), 'gr11': sum(tgra11), 'n11': sum(tnum11),
                    'a11': sum(talg11), 'r11': sum(trat11), 'i11': sum(tine11), 'in11': sum(tint11), 'd11': sum(tden11), 'v11': sum(tvec11),

                    't12': sum(ttri12), 'p12': sum(tpro12), 's12': sum(tsta12), 'g12': sum(tgeo12), 'gr12': sum(tgra12), 'n12': sum(tnum12),
                    'a12': sum(talg12), 'r12': sum(trat12), 'i12': sum(tine12), 'in12': sum(tint12), 'd12': sum(tden12), 'v12': sum(tvec12),

                    'user':user_object,
                    'data':user_profile,})

@login_required(login_url="signin")
def analysisp3(request):

    tri = []
    Triangle = QuestionP3.objects.filter(topic="Triangle")
    for q in Triangle:

        tri.append(q)

    pro = []
    Probability = QuestionP3.objects.filter(topic="Probability")
    for q in Probability:
        pro.append(q)

    sta = []
    Statistics = QuestionP3.objects.filter(topic="Statistics")
    for q in Statistics:
        sta.append(q)

    geo = []
    Geometry = QuestionP3.objects.filter(topic="Geometry")
    for q in Geometry:
        geo.append(q)


    gra = []
    Graph = QuestionP3.objects.filter(topic="Graph")
    for q in Graph:
        gra.append(q)

    num = []
    Numbers = QuestionP3.objects.filter(topic="Numbers")
    for q in Numbers:
        num.append(q)

    alg = []
    Algebra = QuestionP3.objects.filter(topic="Algebra")
    for q in Algebra:
        alg.append(q)

    rat = []
    Ratio = QuestionP3.objects.filter(topic="Ratio")
    for q in Ratio:
        rat.append(q)

    ine = []
    Inequality = QuestionP3.objects.filter(topic="Inequality")
    for q in Inequality:
        ine.append(q)

    int = []
    Interest = QuestionP3.objects.filter(topic="Interest")
    for q in Interest:
        int.append(q)

    den = []
    Density = QuestionP3.objects.filter(topic="Density")
    for q in Density:
        den.append(q)

    vec = []
    Vectors = QuestionP3.objects.filter(topic="Vectors")
    for q in Vectors:
        vec.append(q)

    const = 53

    #Percentage

    trip = round(((len(tri) / const) * 100), 2)
    prop = round(((len(pro) / const) * 100), 2)
    stap = round(((len(sta) / const) * 100), 2)

    geop = round(((len(geo) / const) * 100), 2)
    grap = round(((len(gra) / const) * 100), 2)
    nump = round(((len(num) / const) * 100), 2)

    algp = round(((len(alg) / const) * 100), 2)
    ratp = round(((len(rat) / const) * 100), 2)
    inep = round(((len(ine) / const) * 100), 2)

    intp = round(((len(int) / const) * 100), 2)
    denp = round(((len(den) / const) * 100), 2)
    vecp = round(((len(vec) / const) * 100), 2)

    #Marks

    mtri = []
    Triangle = QuestionP3.objects.filter(topic="Triangle")
    for q in Triangle:
        mtri.append(q.marks)

    mpro = []
    Probability = QuestionP3.objects.filter(topic="Probability")
    for q in Probability:
        mpro.append(q.marks)

    msta = []
    Statistics = QuestionP3.objects.filter(topic="Statistics")
    for q in Statistics:
        msta.append(q.marks)

    mgeo = []
    Geometry = QuestionP3.objects.filter(topic="Geometry")
    for q in Geometry:
        mgeo.append(q.marks)

    mgra = []
    Graph = QuestionP3.objects.filter(topic="Graph")
    for q in Graph:
        mgra.append(q.marks)

    mnum = []
    Numbers = QuestionP3.objects.filter(topic="Numbers")
    for q in Numbers:
        mnum.append(q.marks)

    malg = []
    Algebra = QuestionP3.objects.filter(topic="Algebra")
    for q in Algebra:
        malg.append(q.marks)

    mrat = []
    Ratio = QuestionP3.objects.filter(topic="Ratio")
    for q in Ratio:
        mrat.append(q.marks)

    mine = []
    Inequality = QuestionP3.objects.filter(topic="Inequality")
    for q in Inequality:
        mine.append(q.marks)

    mint = []
    Interest = QuestionP3.objects.filter(topic="Interest")
    for q in Interest:
        mint.append(q.marks)

    mden = []
    Density = QuestionP3.objects.filter(topic="Density")
    for q in Density:
        mden.append(q.marks)

    mvec = []
    Vectors = QuestionP3.objects.filter(topic="Vectors")
    for q in Vectors:
        mvec.append(q.marks)

    cm = 2 * 80

    ptri = round((sum(mtri) / cm) * 100, 2)
    ppro = round((sum(mpro) / cm) * 100, 2)
    psta = round((sum(msta) / cm) * 100, 2)
    pgeo = round((sum(mgeo) / cm) * 100, 2)
    pgra = round((sum(mgra) / cm) * 100, 2)
    pnum = round((sum(mnum) / cm) * 100, 2)
    palg = round((sum(malg) / cm) * 100, 2)
    prat = round((sum(mrat) / cm) * 100, 2)
    pine = round((sum(mine) / cm) * 100, 2)
    pint = round((sum(mint) / cm) * 100, 2)
    pden = round((sum(mden) / cm) * 100, 2)
    pvec = round((sum(mvec) / cm) * 100, 2)

    ttri = []
    tpro = []
    tsta = []
    tgeo = []
    tgra = []
    tnum = []
    talg = []
    trat = []
    tine = []
    tint = []
    tden = []
    tvec = []

    ttri2 = []
    tpro2 = []
    tsta2 = []
    tgeo2 = []
    tgra2 = []
    tnum2 = []
    talg2 = []
    trat2 = []
    tine2 = []
    tint2 = []
    tden2 = []
    tvec2 = []

    ttri3 = []
    tpro3 = []
    tsta3 = []
    tgeo3 = []
    tgra3 = []
    tnum3 = []
    talg3 = []
    trat3 = []
    tine3 = []
    tint3 = []
    tden3 = []
    tvec3 = []

    ttri4 = []
    tpro4 = []
    tsta4 = []
    tgeo4 = []
    tgra4 = []
    tnum4 = []
    talg4 = []
    trat4 = []
    tine4 = []
    tint4 = []
    tden4 = []
    tvec4 = []

    ttri5 = []
    tpro5 = []
    tsta5 = []
    tgeo5 = []
    tgra5 = []
    tnum5 = []
    talg5 = []
    trat5 = []
    tine5 = []
    tint5 = []
    tden5 = []
    tvec5 = []

    ttri6 = []
    tpro6 = []
    tsta6 = []
    tgeo6 = []
    tgra6 = []
    tnum6 = []
    talg6 = []
    trat6 = []
    tine6 = []
    tint6 = []
    tden6 = []
    tvec6 = []

    ttri7 = []
    tpro7 = []
    tsta7 = []
    tgeo7 = []
    tgra7 = []
    tnum7 = []
    talg7 = []
    trat7 = []
    tine7 = []
    tint7 = []
    tden7 = []
    tvec7 = []

    ttri8 = []
    tpro8 = []
    tsta8 = []
    tgeo8 = []
    tgra8 = []
    tnum8 = []
    talg8 = []
    trat8 = []
    tine8 = []
    tint8 = []
    tden8 = []
    tvec8 = []

    ttri9 = []
    tpro9 = []
    tsta9 = []
    tgeo9 = []
    tgra9 = []
    tnum9 = []
    talg9 = []
    trat9 = []
    tine9 = []
    tint9 = []
    tden9 = []
    tvec9 = []

    ttri10 = []
    tpro10 = []
    tsta10 = []
    tgeo10 = []
    tgra10 = []
    tnum10 = []
    talg10 = []
    trat10 = []
    tine10 = []
    tint10 = []
    tden10 = []
    tvec10 = []

    ttri11 = []
    tpro11 = []
    tsta11 = []
    tgeo11 = []
    tgra11 = []
    tnum11 = []
    talg11 = []
    trat11 = []
    tine11 = []
    tint11 = []
    tden11 = []
    tvec11 = []


    ttri12 = []
    tpro12 = []
    tsta12 = []
    tgeo12 = []
    tgra12 = []
    tnum12 = []
    talg12 = []
    trat12 = []
    tine12 = []
    tint12 = []
    tden12 = []
    tvec12 = []


    n1 = QuestionP3.objects.filter(number=1)
    n2 = QuestionP3.objects.filter(number=2)
    n3 = QuestionP3.objects.filter(number=3)
    n4 = QuestionP3.objects.filter(number=4)
    n5 = QuestionP3.objects.filter(number=5)
    n6 = QuestionP3.objects.filter(number=6)
    n7 = QuestionP3.objects.filter(number=7)
    n8 = QuestionP3.objects.filter(number=8)
    n9 = QuestionP3.objects.filter(number=9)
    n10 = QuestionP3.objects.filter(number=10)
    n11 = QuestionP3.objects.filter(number=11)
    n12 = QuestionP3.objects.filter(number=12)

    for q in n1:
        if q.topic == 'Triangle':
            ttri.append(1)
        if q.topic == 'Probabilty':
            tpro.append(1)
        if q.topic == 'Statistics':
            tsta.append(1)
        if q.topic == 'Geometry':
            tgeo.append(1)
        if q.topic == 'Graph':
            tgra.append(1)
        if q.topic == 'Number':
            tnum.append(1)
        if q.topic == 'Algebra':
            talg.append(1)
        if q.topic == 'Ratio':
            trat.append(1)
        if q.topic == 'Inequality':
            tine.append(1)
        if q.topic == 'Interest':
            tint.append(1)
        if q.topic == 'Density':
            tden.append(1)
        if q.topic == 'Vectors':
            tvec.append(1)
    for q in n2:
        if q.topic == 'Triangle':
            ttri2.append(1)
        if q.topic == 'Probabilty':
            tpro2.append(1)
        if q.topic == 'Statistics':
            tsta2.append(1)
        if q.topic == 'Geometry':
            tgeo2.append(1)
        if q.topic == 'Graph':
            tgra2.append(1)
        if q.topic == 'Number':
            tnum2.append(1)
        if q.topic == 'Algebra':
            talg2.append(1)
        if q.topic == 'Ratio':
            trat2.append(1)
        if q.topic == 'Inequality':
            tine2.append(1)
        if q.topic == 'Interest':
            tint2.append(1)
        if q.topic == 'Density':
            tden2.append(1)
        if q.topic == 'Vectors':
            tvec2.append(1)
    for q in n3:
        if q.topic == 'Triangle':
            ttri3.append(1)
        if q.topic == 'Probabilty':
            tpro3.append(1)
        if q.topic == 'Statistics':
            tsta3.append(1)
        if q.topic == 'Geometry':
            tgeo3.append(1)
        if q.topic == 'Graph':
            tgra3.append(1)
        if q.topic == 'Number':
            tnum3.append(1)
        if q.topic == 'Algebra':
            talg3.append(1)
        if q.topic == 'Ratio':
            trat3.append(1)
        if q.topic == 'Inequality':
            tine3.append(1)
        if q.topic == 'Interest':
            tint3.append(1)
        if q.topic == 'Density':
            tden3.append(1)
        if q.topic == 'Vectors':
            tvec3.append(1)
    for q in n4:
        if q.topic == 'Triangle':
            ttri4.append(1)
        if q.topic == 'Probabilty':
            tpro4.append(1)
        if q.topic == 'Statistics':
            tsta4.append(1)
        if q.topic == 'Geometry':
            tgeo4.append(1)
        if q.topic == 'Graph':
            tgra4.append(1)
        if q.topic == 'Number':
            tnum4.append(1)
        if q.topic == 'Algebra':
            talg4.append(1)
        if q.topic == 'Ratio':
            trat4.append(1)
        if q.topic == 'Inequality':
            tine4.append(1)
        if q.topic == 'Interest':
            tint4.append(1)
        if q.topic == 'Density':
            tden4.append(1)
        if q.topic == 'Vectors':
            tvec4.append(1)
    for q in n5:
        if q.topic == 'Triangle':
            ttri5.append(1)
        if q.topic == 'Probabilty':
            tpro5.append(1)
        if q.topic == 'Statistics':
            tsta5.append(1)
        if q.topic == 'Geometry':
            tgeo5.append(1)
        if q.topic == 'Graph':
            tgra5.append(1)
        if q.topic == 'Number':
            tnum5.append(1)
        if q.topic == 'Algebra':
            talg5.append(1)
        if q.topic == 'Ratio':
            trat5.append(1)
        if q.topic == 'Inequality':
            tine5.append(1)
        if q.topic == 'Interest':
            tint5.append(1)
        if q.topic == 'Density':
            tden5.append(1)
        if q.topic == 'Vectors':
            tvec5.append(1)
    for q in n6:
        if q.topic == 'Triangle':
            ttri6.append(1)
        if q.topic == 'Probabilty':
            tpro6.append(1)
        if q.topic == 'Statistics':
            tsta6.append(1)
        if q.topic == 'Geometry':
            tgeo6.append(1)
        if q.topic == 'Graph':
            tgra6.append(1)
        if q.topic == 'Number':
            tnum6.append(1)
        if q.topic == 'Algebra':
            talg6.append(1)
        if q.topic == 'Ratio':
            trat6.append(1)
        if q.topic == 'Inequality':
            tine6.append(1)
        if q.topic == 'Interest':
            tint6.append(1)
        if q.topic == 'Density':
            tden6.append(1)
        if q.topic == 'Vectors':
            tvec6.append(1)
    for q in n7:
        if q.topic == 'Triangle':
            ttri7.append(1)
        if q.topic == 'Probabilty':
            tpro7.append(1)
        if q.topic == 'Statistics':
            tsta7.append(1)
        if q.topic == 'Geometry':
            tgeo7.append(1)
        if q.topic == 'Graph':
            tgra7.append(1)
        if q.topic == 'Number':
            tnum7.append(1)
        if q.topic == 'Algebra':
            talg7.append(1)
        if q.topic == 'Ratio':
            trat7.append(1)
        if q.topic == 'Inequality':
            tine7.append(1)
        if q.topic == 'Interest':
            tint7.append(1)
        if q.topic == 'Density':
            tden7.append(1)
        if q.topic == 'Vectors':
            tvec7.append(1)
    for q in n8:
        if q.topic == 'Triangle':
            ttri8.append(1)
        if q.topic == 'Probabilty':
            tpro8.append(1)
        if q.topic == 'Statistics':
            tsta8.append(1)
        if q.topic == 'Geometry':
            tgeo8.append(1)
        if q.topic == 'Graph':
            tgra8.append(1)
        if q.topic == 'Number':
            tnum8.append(1)
        if q.topic == 'Algebra':
            talg8.append(1)
        if q.topic == 'Ratio':
            trat8.append(1)
        if q.topic == 'Inequality':
            tine8.append(1)
        if q.topic == 'Interest':
            tint8.append(1)
        if q.topic == 'Density':
            tden8.append(1)
        if q.topic == 'Vectors':
            tvec8.append(1)
    for q in n9:
        if q.topic == 'Triangle':
            ttri9.append(1)
        if q.topic == 'Probabilty':
            tpro9.append(1)
        if q.topic == 'Statistics':
            tsta9.append(1)
        if q.topic == 'Geometry':
            tgeo9.append(1)
        if q.topic == 'Graph':
            tgra9.append(1)
        if q.topic == 'Number':
            tnum9.append(1)
        if q.topic == 'Algebra':
            talg9.append(1)
        if q.topic == 'Ratio':
            trat9.append(1)
        if q.topic == 'Inequality':
            tine9.append(1)
        if q.topic == 'Interest':
            tint9.append(1)
        if q.topic == 'Density':
            tden9.append(1)
        if q.topic == 'Vectors':
            tvec9.append(1)
    for q in n10:
        if q.topic == 'Triangle':
            ttri10.append(1)
        if q.topic == 'Probabilty':
            tpro10.append(1)
        if q.topic == 'Statistics':
            tsta10.append(1)
        if q.topic == 'Geometry':
            tgeo10.append(1)
        if q.topic == 'Graph':
            tgra10.append(1)
        if q.topic == 'Number':
            tnum10.append(1)
        if q.topic == 'Algebra':
            talg10.append(1)
        if q.topic == 'Ratio':
            trat10.append(1)
        if q.topic == 'Inequality':
            tine10.append(1)
        if q.topic == 'Interest':
            tint10.append(1)
        if q.topic == 'Density':
            tden10.append(1)
        if q.topic == 'Vectors':
            tvec10.append(1)
    for q in n11:
        if q.topic == 'Triangle':
            ttri11.append(1)
        if q.topic == 'Probabilty':
            tpro11.append(1)
        if q.topic == 'Statistics':
            tsta11.append(1)
        if q.topic == 'Geometry':
            tgeo11.append(1)
        if q.topic == 'Graph':
            tgra11.append(1)
        if q.topic == 'Number':
            tnum11.append(1)
        if q.topic == 'Algebra':
            talg11.append(1)
        if q.topic == 'Ratio':
            trat11.append(1)
        if q.topic == 'Inequality':
            tine11.append(1)
        if q.topic == 'Interest':
            tint11.append(1)
        if q.topic == 'Density':
            tden11.append(1)
        if q.topic == 'Vectors':
            tvec11.append(1)
    for q in n12:
        if q.topic == 'Triangle':
            ttri12.append(1)
        if q.topic == 'Probabilty':
            tpro12.append(1)
        if q.topic == 'Statistics':
            tsta12.append(1)
        if q.topic == 'Geometry':
            tgeo12.append(1)
        if q.topic == 'Graph':
            tgra12.append(1)
        if q.topic == 'Number':
            tnum12.append(1)
        if q.topic == 'Algebra':
            talg12.append(1)
        if q.topic == 'Ratio':
            trat12.append(1)
        if q.topic == 'Inequality':
            tine12.append(1)
        if q.topic == 'Interest':
            tint12.append(1)
        if q.topic == 'Density':
            tden12.append(1)
        if q.topic == 'Vectors':
            tvec12.append(1)

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    return render(request, 'analysisp3.html',
                  {'tri':tri, 'pro':pro, 'sta':sta, 'geo':geo,
                   'gra':gra, 'num':num, 'alg':alg, 'rat':rat,
                   'ine':ine, 'int':int, 'den':den, 'vec':vec,

                   'trip':trip, 'prop':prop, 'stap':stap, 'geop':geop,
                   'grap':grap, 'nump':nump, 'algp':algp, 'ratp':ratp,
                   'inep':inep, 'intp':intp, 'denp':denp, 'vecp':vecp,

                   'mtri':sum(mtri), 'mpro':sum(mpro), 'msta':sum(msta), 'mgeo':sum(mgeo),
                   'mgra':sum(mgra), 'mnum':sum(mnum), 'malg':sum(malg), 'mrat':sum(mrat),
                   'mine':sum(mine), 'mint':sum(mint), 'mden':sum(mden), 'mvec':sum(mvec),

                   'ptri':ptri, 'ppro':ppro, 'psta':psta, 'pgeo':pgeo, 'pgra':pgra, 'pnum':pnum,
                   'palg':palg, 'prat':prat, 'pine':pine, 'pint':pint, 'pden':pden, 'pvec':pvec,

                   't1':sum(ttri), 'p1':sum(tpro), 's1':sum(tsta), 'g1':sum(tgeo), 'gr1':sum(tgra), 'n1':sum(tnum),
                   'a1':sum(talg), 'r1':sum(trat), 'i1':sum(tine), 'in1':sum(tint), 'd1':sum(tden), 'v1':sum(tvec),

                   't2':sum(ttri2), 'p2':sum(tpro2), 's2':sum(tsta2), 'g2':sum(tgeo2), 'gr2':sum(tgra2), 'n2':sum(tnum2),
                   'a2':sum(talg2), 'r2':sum(trat2), 'i2':sum(tine2), 'in2':sum(tint2), 'd2':sum(tden2), 'v2':sum(tvec2),

                   't3':sum(ttri3), 'p3':sum(tpro3), 's3':sum(tsta3), 'g3':sum(tgeo3), 'gr3':sum(tgra3), 'n3':sum(tnum3),
                   'a3':sum(talg3), 'r3':sum(trat3), 'i3':sum(tine3), 'in3':sum(tint3), 'd3':sum(tden3), 'v3':sum(tvec3),

                   't4':sum(ttri4), 'p4':sum(tpro4), 's4':sum(tsta4), 'g4':sum(tgeo4), 'gr4':sum(tgra4), 'n4':sum(tnum4),
                   'a4':sum(talg4), 'r4':sum(trat4), 'i4':sum(tine4), 'in4':sum(tint4), 'd4':sum(tden4), 'v4':sum(tvec4),

                   't5':sum(ttri5), 'p5':sum(tpro5), 's5':sum(tsta5), 'g5':sum(tgeo5), 'gr5':sum(tgra5), 'n5':sum(tnum5),
                   'a5':sum(talg5), 'r5':sum(trat5), 'i5':sum(tine5), 'in5':sum(tint5), 'd5':sum(tden5), 'v5':sum(tvec5),

                    't6': sum(ttri6), 'p6': sum(tpro6), 's6': sum(tsta6), 'g6': sum(tgeo6), 'gr6': sum(tgra6), 'n6': sum(tnum6),
                    'a6': sum(talg6), 'r6': sum(trat6), 'i6': sum(tine6), 'in6': sum(tint6), 'd6': sum(tden6), 'v6': sum(tvec6),

                    't7': sum(ttri7), 'p7': sum(tpro7), 's7': sum(tsta7), 'g7': sum(tgeo7), 'gr7': sum(tgra7), 'n7': sum(tnum7),
                    'a7': sum(talg7), 'r7': sum(trat7), 'i7': sum(tine7), 'in7': sum(tint7), 'd7': sum(tden7), 'v7': sum(tvec7),

                    't8': sum(ttri8), 'p8': sum(tpro8), 's8': sum(tsta8), 'g8': sum(tgeo8), 'gr8': sum(tgra8), 'n8': sum(tnum8),
                    'a8': sum(talg8), 'r8': sum(trat8), 'i8': sum(tine8), 'in8': sum(tint8), 'd8': sum(tden8), 'v8': sum(tvec8),

                    't9': sum(ttri9), 'p9': sum(tpro9), 's9': sum(tsta9), 'g9': sum(tgeo9), 'gr9': sum(tgra9), 'n9': sum(tnum9),
                    'a9': sum(talg9), 'r9': sum(trat9), 'i9': sum(tine9), 'in9': sum(tint9), 'd9': sum(tden9), 'v9': sum(tvec9),

                    't10': sum(ttri10), 'p10': sum(tpro10), 's10': sum(tsta10), 'g10': sum(tgeo10), 'gr10': sum(tgra10), 'n10': sum(tnum10),
                    'a10': sum(talg10), 'r10': sum(trat10), 'i10': sum(tine10), 'in10': sum(tint10), 'd10': sum(tden10), 'v10': sum(tvec10),

                    't11': sum(ttri11), 'p11': sum(tpro11), 's11': sum(tsta11), 'g11': sum(tgeo11), 'gr11': sum(tgra11), 'n11': sum(tnum11),
                    'a11': sum(talg11), 'r11': sum(trat11), 'i11': sum(tine11), 'in11': sum(tint11), 'd11': sum(tden11), 'v11': sum(tvec11),

                    't12': sum(ttri12), 'p12': sum(tpro12), 's12': sum(tsta12), 'g12': sum(tgeo12), 'gr12': sum(tgra12), 'n12': sum(tnum12),
                    'a12': sum(talg12), 'r12': sum(trat12), 'i12': sum(tine12), 'in12': sum(tint12), 'd12': sum(tden12), 'v12': sum(tvec12),

                    'user':user_object,
                    'data':user_profile,})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                new_pwdlist = Pwdlist.objects.create(username=username, email=email, password=password)
                new_pwdlist.save()

                #Log user + redirect to settings
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create profile for user

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('/index')
        else:
            messages.info(request, 'Password Not Mathching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/index')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    return redirect('homepage')


#OCR AS

@login_required(login_url="signin")
def p2asocr(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'p2asocr.html', context)

@login_required(login_url="signin")
def p1asocr(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user':user_object,
        'data':user_profile,
    }

    return render(request, 'p1asocr.html', context)

@login_required(login_url="signin")
def asocran1(request):
    pass

@login_required(login_url="signin")
def asocran2(request):
    pass

@login_required(login_url="signin")
def upasocr1(request):
    p12023 = []
    p12021 = []
    p12020 = []
    p12019 = []
    p120190 = []
    p12018 = []
    p120180 = []

    #p1 = P1ASOCR.objects.filter(year=2021)


    #for q in p1:
    #    p12021.append(q)


    return render(request, 'upasocr1.html',
                #{"q2023":p12023}
    )

@login_required(login_url="signin")
def upasocr2(request):
    p12023 = []
    p12021 = []
    p12020 = []
    p12019 = []
    p120190 = []
    p12018 = []
    p120180 = []

    #p1 = P2ASOCR.objects.filter(year=2021)


    #for q in p1:
    #    p12021.append(q)


    return render(request, 'upasocr2.html',
   #             {"q2023":p12023}
    )

@login_required(login_url="signin")
def upload_as_ocr_(request):
    if request.method == 'POST':
        image = request.FILES.get('img')
        image_ans = request.FILES.get('img_ans')
        image_w = request.FILES.get('img_w')

        year = request.POST['year']
        number = request.POST['number']
        topic = request.POST['topic']
        marks = request.POST['marks']
        guidance = request.POST['guidance']
        p = request.POST['paper']

        if p == '1':
            new_QuestionP1 = P1ASOCR.objects.create(img_w=image_w, year=year, number=number, topic=topic, marks=marks, img_ans=image_ans ,img=image, guidance=guidance)
            new_QuestionP1.save()

            return render(request, 'upasocr1.html')
        elif p == '2':
            new_QuestionP2 = P2ASOCR.objects.create(img_w=image_w, year=year, number=number, topic=topic, marks=marks, img_ans=image_ans, img=image, guidance=guidance)
            new_QuestionP2.save()

            return render(request, 'upasocr2.html')

    else:
        pass

def upload_as_ocr(request):
    if request.method == 'POST':
        year = request.POST.getlist('year[]')
        number = request.POST.getlist('number[]')
        topic = request.POST.getlist('topic[]')
        marks = request.POST.getlist('marks[]')
        guidance = request.POST.getlist('guidance[]')
        p = request.POST.get('paper')
        image = request.FILES.getlist('img[]')
        image_ans = request.FILES.getlist('img_ans[]')
        image_w = request.FILES.getlist('img_w[]')


        if p == '1':
            for i in range(len(year)):
                new_QuestionP1 = P1ASOCR.objects.create(img_w=image_w[i], year=year[i], number=number[i], topic=topic[i], marks=marks[i], img_ans=image_ans[i] ,img=image[i], guidance=guidance[i])
                new_QuestionP1.save()

            return render(request, 'upasocr1.html')
        elif p == '2':
            for i in range(len(year)):
                new_QuestionP2 = P2ASOCR.objects.create(img_w=image_w[i], year=year[i], number=number[i], topic=topic[i], marks=marks[i], img_ans=image_ans[i], img=image[i], guidance=guidance[i])
                new_QuestionP2.save()

            return render(request, 'upasocr2.html')
        
    else:
        pass


def search_all_ocras(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        number = request.POST.get('number')
        marks = request.POST.get('marks')
        topic = request.POST.get('topic')
        p = request.POST.get('paper')

        # Initialize an empty dictionary to hold the filter criteria
        filters = {}

        # Add filters only if the respective fields are provided
        if year:
            filters['year'] = year
        if number:
            filters['number'] = number
        if marks:
            filters['marks'] = marks
        if topic:
            filters['topic'] = topic

        # Apply the filters to the appropriate model
        if p == '1':
            r_q = P1ASOCR.objects.filter(**filters)
            QuestionP1s = list(r_q)
            return render(request, 'p1asocr.html', {"q": QuestionP1s})
        elif p == '2':
            r_q = P2ASOCR.objects.filter(**filters)
            QuestionP2s = list(r_q)
            return render(request, 'p2asocr.html', {"q": QuestionP2s})

    # Redirect if the request method is not POST
    return redirect('/index')


