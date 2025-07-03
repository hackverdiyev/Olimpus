from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings
from django import template
from problems.models import *
from random import randint
from base.models import *
from time import time

standard_symbols=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0','.','_']
subjects={'math':'Riyaziyyat','physics':'Fizika','astronomy':'Astronomiya','chemistry':'Kimya','geography':'Coğrafiya','biology':'Biologiya','history':'Tarix','junior':'Aşağı yaş qrupu'}
page_limit=25

def islogin(request):
    if 'username' in request.session:
        user=Account.objects.get(username=request.session['username'])
        return user
    return False

def create_restore_request(username,email,password="",fullname=""):
    try:
        Verification.objects.get(username=username).delete()
    except:
        pass
    Verification(username=username,email=email,password=password,fullname=fullname,six_digit_code=randint(100000,999999),time=time()*1000).save()
    send_mail(
        "Şifrə Yeniləmə",
        f"Olimpus Verification Code\nThis verification code was sent to your email for help getting back into a Olimpus Account:\n\n{Verification.objects.get(username=username).six_digit_code}\n\nDon’t know why you received this?\n\nSomeone who couldn’t remember their Olimpus Account details probably gave your email address by mistake. You can safely ignore this email.\n\nTo protect your account,don’t forward this email or give this code to anyone.\n\nOlimpus Team",
        "settings.EMAIL_HOST_USER",
        [email],
        True)

def base(request):
    user=islogin(request)
    problems_count=len(Problem.objects.all())
    problems=Problem.objects.all().order_by('-pub_date')[:10]
    best=Problem.objects.filter(have_solution=False).order_by('-problem_views')[:3]
    news=News.objects.all().order_by("-date")
    if len(news)>5:
        news=news[:5]
    return render(request,'base.html',{"news":news,"best":best,"problems_count":problems_count,"problems": problems,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def contact(request):
    user=islogin(request)
    if request.method=='POST':
        ContactMessage(full_name=request.POST["fullname"],email=request.POST["email"],message=request.POST["message"]).save()
        return redirect("/contact")
    return render(request,"contact.html",{"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def login(request):
    if islogin(request):
        return redirect("/")
    if request.method=='POST':
        try:
            if Account.objects.get(username=request.POST["username"]).password==request.POST["password"]:
                request.session['username']=request.POST["username"]
                return redirect("/")
            return render(request,'login.html',{"error":2,"subjects":subjects,"islogin":False})
        except:
            return render(request,'login.html',{"error":1,"subjects":subjects,"islogin":False})
    return render(request,'login.html',{"subjects":subjects,"islogin":False})

def logout(request):
    if islogin(request):
        del request.session['username']
    return redirect('/')

def register(request):
    if islogin(request):
        return redirect("/")
    if request.method=='POST':
        try:
            Account.objects.get(username=request.POST["username"])
            return render(request,'register.html',{"error":1,"subjects":subjects,"islogin":False})
        except:
            if len(request.POST["username"])<4 or len(request.POST["username"])>20:
                return render(request,'register.html',{"error":2,"subjects":subjects,"islogin":False})
            a=0
            for i in request.POST["username"]:
                if i not in standard_symbols:
                    a=1
                    break
            if a:
                return render(request,'register.html',{"error":3,"subjects":subjects,"islogin":False})
            a=1
            for i in request.POST["username"]:
                if i in standard_symbols[:52]:
                    a=0
                    break
            if a:
                return render(request,'register.html',{"error":4,"subjects":subjects,"islogin":False})
            try:
                Account.objects.get(email=request.POST["email"].lower())
                return render(request,'register.html',{"error":5,"subjects":subjects,"islogin":False})
            except:
                if len(request.POST["email"].lower().split('@'))!=2 or len(request.POST["email"].lower().split('@')[0])==0 or len(request.POST["email"].lower().split('@')[1].split('.'))!=2 or len(request.POST["email"].lower().split('@')[1].split('.')[0])==0 or len(request.POST["email"].lower().split('@')[1].split('.')[1])==0 or len(request.POST["email"].lower())>50:
                    return render(request,'register.html',{"error":6,"subjects":subjects,"islogin":False})
                if request.POST["password"]!=request.POST["password_repeat"]:
                    return render(request,'register.html',{"error":7,"subjects":subjects,"islogin":False})
                if len(request.POST["password"])<8 or len(request.POST["password"])>50:
                    return render(request,'register.html',{"error":8,"subjects":subjects,"islogin":False})
                a=0
                for i in request.POST["password"]:
                    if i not in standard_symbols:
                        a=1
                        break
                if a:
                    return render(request,'register.html',{"error":9,"subjects":subjects,"islogin":False})
                a=1
                for i in request.POST["password"]:
                    if i in standard_symbols[:26]:
                        a=0
                        break
                if not a:
                    a=1
                    for i in request.POST["password"]:
                        if i in standard_symbols[26:52]:
                            a=0
                            break
                if not a:
                    a=1
                    for i in request.POST["password"]:
                        if i in standard_symbols[52:62]:
                            a=0
                            break
                if a:
                    return render(request,'register.html',{"error":10,"subjects":subjects,"islogin":False})
                create_restore_request(request.POST["username"],request.POST["email"].lower(),request.POST["password"],request.POST["fullname"])
                return redirect(f'/verification/{request.POST["username"]}/register')
    return render(request,'register.html',{"subjects":subjects,"islogin":False})

def verification(request,username,request_type):
    user=islogin(request)
    if request.method=='POST':
        if request.POST["code"]==f"{Verification.objects.get(username=username).six_digit_code}":
            if time()*1000-Verification.objects.get(username=username).time<300000:
                if request_type=='register':
                    Account(username=username,fullname=Verification.objects.get(username=username).fullname,email=Verification.objects.get(username=username).email,password=Verification.objects.get(username=username).password).save()
                    request.session['username']=username
                    Verification.objects.get(username=username).delete()
                    return redirect("/")
                if request_type=='restore':
                    Verification.objects.get(username=username).delete()
                    return redirect(f'/select_password/{username}')
                if request_type=='change_email':
                    user.email=Verification.objects.get(username=username).email
                    user.save()
                    Verification.objects.get(username=username).delete()
                    return redirect("/profile")
            return render(request,'verification.html',{"error":2,"username":username,"time":Verification.objects.get(username=username).time,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        return render(request,'verification.html',{"error":1,"username":username,'request_type':request_type,"time":Verification.objects.get(username=username).time,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
    if request.META.get('HTTP_REFERER')==None:
        return redirect('/restore_password')
    return render(request,'verification.html',{"username":username,'request_type':request_type,"time":Verification.objects.get(username=username).time,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def verification_again(request,username,request_type):
    if request.META.get('HTTP_REFERER')==None:
        return redirect('/restore_password')
    create_restore_request(username,Verification.objects.get(username=username).email)
    return redirect(f'/verification/{username}/{request_type}')

def restore_password(request):
    user=islogin(request)
    if request.method=='POST':
        try:
            if Account.objects.get(username=request.POST["username"]).email==request.POST["email"].lower():
                create_restore_request(request.POST["username"],Account.objects.get(username=request.POST["username"]).email)
                return redirect(f'/verification/{request.POST["username"]}/restore')
            return render(request,'restore_password.html',{"error":2,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        except:
            return render(request,'restore_password.html',{"error":1,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
    return render(request,'restore_password.html',{"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def select_password(request,username):
    user=Account.objects.get(username=username)
    if request.method=='POST':
        if request.POST["password"]!=request.POST["password_repeat"]:
            return render(request,'select_password.html',{"error":1,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        if len(request.POST["password"])<8 or len(request.POST["password"])>50:
            return render(request,'select_password.html',{"error":2,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        a=0
        for i in request.POST["password"]:
            if i not in standard_symbols:
                a=1
                break
        if a:
            return render(request,'select_password.html',{"error":3,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        a=1
        for i in request.POST["password"]:
            if i in standard_symbols[:26]:
                a=0
                break
        if not a:
            a=1
            for i in request.POST["password"]:
                if i in standard_symbols[26:52]:
                    a=0
                    break
        if not a:
            a=1
            for i in request.POST["password"]:
                if i in standard_symbols[52:62]:
                    a=0
                    break
        if a:
            return render(request,'select_password.html',{"error":4,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        user.password=request.POST["password"]
        user.save()
        return redirect('/login')
    if request.META.get('HTTP_REFERER')==None:
        return redirect('/restore_password')
    return render(request,'select_password.html',{"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def profile(request,username):
    user=islogin(request)
    if user==False or user.username!=username:
        id=Account.objects.get(username=username)
        rating=0
        if id.point>0:
            rating=list(Account.objects.all().order_by('-point')).index(id)+1
        return render(request,'profile_view.html',{'rating':rating,'username':Account.objects.get(username=username),"user_problems":Problem.objects.filter(user_added=id),"user_solutions":Solution.objects.filter(user_solved=id),"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
    rating=0
    if user.point>0:
        rating=list(Account.objects.all().order_by('-point')).index(user)+1
    user_problems=Problem.objects.filter(user_added=user)
    user_solutions=Solution.objects.filter(user_solved=user)
    if request.method=='POST':
        if 'fullname' in request.POST:
            user.fullname=request.POST["fullname"]
            user.save()
            return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        if 'delete' in request.POST:
            user.profile_photo='profile_photos/default_pp.png'
            user.save()
            return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        if 'photo' in request.FILES:
            user.profile_photo=request.FILES.get("photo")
            user.save()
            return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
        if 'username' in request.POST:
            if request.POST['username']==request.session['username']:
                return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
            try:
                Account.objects.get(username=request.POST["username"])
                return render(request,'profile.html',{"error":6,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
            except:
                if len(request.POST["username"])<4 or len(request.POST["username"])>20:
                    return render(request,'profile.html',{"error":7,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                a=0
                for i in request.POST["username"]:
                    if i not in standard_symbols:
                        a=1
                        break
                if a:
                    return render(request,'profile.html',{"error":8,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                a=1
                for i in request.POST["username"]:
                    if i in standard_symbols[:52]:
                        a=0
                        break
                if a:
                    return render(request,'profile.html',{"error":9,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                user.username=request.POST["username"]
                user.save()                
                request.session["username"]=request.POST["username"]
                return redirect(f'/profile/{user.username}')
        if 'email' in request.POST:
            if request.POST['email']==Account.objects.get(username=request.session['username']).email:
                return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
            try:
                Account.objects.get(email=request.POST["email"].lower())
                return render(request,'profile.html',{"error":10,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
            except:
                if len(request.POST["email"].lower().split('@'))!=2 or len(request.POST["email"].lower().split('@')[0])==0 or len(request.POST["email"].lower().split('@')[1].split('.'))!=2 or len(request.POST["email"].lower().split('@')[1].split('.')[0])==0 or len(request.POST["email"].lower().split('@')[1].split('.')[1])==0 or len(request.POST["email"].lower())>50:
                    return render(request,'profile.html',{"error":11,'rating':rating,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                create_restore_request(request.session["username"],request.POST["email"].lower())
                return redirect(f'/verification/{request.session["username"]}/change_email')
        if 'password' in request.POST:
            if Account.objects.get(username=request.session["username"]).password==request.POST["previous_password"]:
                if request.POST["password"]!=request.POST["password_repeat"]:
                    return render(request,'profile.html',{"error":2,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                if len(request.POST["password"])<8 or len(request.POST["password"])>50:
                    return render(request,'profile.html',{"error":3,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                a=0
                for i in request.POST["password"]:
                    if i not in standard_symbols:
                        a=1
                        break
                if a:
                    return render(request,'profile.html',{"error":4,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                a=1
                for i in request.POST["password"]:
                    if i in standard_symbols[:26]:
                        a=0
                        break
                if not a:
                    a=1
                    for i in request.POST["password"]:
                        if i in standard_symbols[26:52]:
                            a=0
                            break
                if not a:
                    a=1
                    for i in request.POST["password"]:
                        if i in standard_symbols[52:62]:
                            a=0
                            break
                if a:
                    return render(request,'profile.html',{"error":5,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
                user.password=request.POST["password"]
                user.save()
                return render(request,'profile.html',{"success":True,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
            return render(request,'profile.html',{"error":1,'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"password","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
    return render(request,'profile.html',{'rating':rating,"user_problems":user_problems,"user_solutions":user_solutions,"default":"profile","subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def news(request):
    user=islogin(request)
    news=News.objects.all()
    return render(request, "news.html", {"news":news,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def news_view(request,id):
    user=islogin(request)
    news=News.objects.get(id=id)
    news.views+=1
    news.save()
    context=news.context.split("%url%")
    urls=news.urls.split("%&")[1:]
    d={}
    for i in range(len(context)):
        d[i]=context[i]
    return render(request, "news_view.html", {"news":news,"context":d,"urls":urls,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def versions(request,version):
    user=islogin(request)
    update=Version.objects.get(version=version)
    return render(request, "versions.html", {"update":update,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def admin_page(request):
    user=islogin(request)
    if user==False or user.admin_tag==False:
        return render(request,'404.html')
    return redirect("/admin/bc91b7c47993de857e161b3984d195672153b07b2243b7a5838cc189cb677aa3")

def verify(request):
    user=islogin(request)
    if user==False or (user.admin_tag==False and user.teacher_tag==False and user.username!='Selcan'): #SELCAN
        return render(request,"404.html")
    if request.method=='POST':
        if 'verify_problem' in request.POST:
            x=Problem.objects.get(id=request.POST['verify_problem'])
            x.show_problem=True
            x.save()
            x.user_added.point+=1
            x.user_added.save()
        elif 'delete_problem' in request.POST:
            x=Problem.objects.get(id=request.POST['delete_problem'])
            x.delete()
        elif 'verify_solution' in request.POST:
            x=Solution.objects.get(id=request.POST['verify_solution'])
            x.problem.have_solution=True
            x.problem.save()
            x.user_solved.point+=3
            x.user_solved.save()
        elif 'delete_solution' in request.POST:
            x=Solution.objects.get(id=request.POST['delete_solution'])
            x.delete()
        elif 'delete_report' in request.POST:
            x=ReportedProblem.objects.get(id=request.POST['delete_report'])
            x.delete()
        elif 'delete_contact' in request.POST:
            x=ContactMessage.objects.get(id=request.POST['delete_contact'])
            x.delete()
        elif 'update' in request.POST:
            x=Account.objects.all()
            for i in x:
                Notification(user=i,type=1,content=request.POST["version"]).save()
            return redirect('/')
        return redirect('/verify')
    problems=Problem.objects.filter(show_problem=False)
    solutions=list(Solution.objects.all())
    a=0
    for i in range(len(solutions)):
        if solutions[i-a].problem.have_solution:
            solutions.pop(i-a)
            a=a+1
        elif i-a>0 and solutions[i-a].problem==solutions[i-a-1].problem:
            solutions.pop(i-a)
            a=a+1
        elif solutions[i-a].user_solved.admin_tag or solutions[i-a].user_solved.teacher_tag or solutions[i-a].user_solved.clever_tag:
            solutions[i-a].user_solved.point+=3
            solutions[i-a].user_solved.save()
            solutions[i-a].problem.have_solution=True
            solutions[i-a].problem.save()
            solutions.pop(i-a)
            a=a+1
    reports=ReportedProblem.objects.all()
    contacts=ContactMessage.objects.all()
    return render(request,"verify.html",{"problems":problems,"solutions":solutions,"reports":reports,"contacts":contacts,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})
