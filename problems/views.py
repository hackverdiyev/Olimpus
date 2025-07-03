from django.shortcuts import render,redirect
from base.models import *
from problems.models import *
from base.views import subjects,page_limit,islogin

def ranking(request):
    user=islogin(request)
    users=Account.objects.filter(point__gt=0).order_by('-point')
    return render(request,'ranking.html',{"users":users,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def problems_main(request):
    user=islogin(request)
    return render(request,"problems_main.html",{"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def problems(request,subject):
    user=islogin(request)
    page=int(request.GET.get('page','1'))
    type=request.GET.get('type','all')
    search=request.GET.get('search','').strip()
    if type=='solved':
        problems=Problem.objects.filter(problem_subject=subject,have_solution=1,public=True)
    elif type=='unsolved':
        problems=Problem.objects.filter(problem_subject=subject,have_solution=0,public=True)
    else:
        problems=Problem.objects.filter(problem_subject=subject,public=True)
    if len(search)>0:
        filtered_problems=[]
        if search.isnumeric():
            f=Problem.objects.filter(id=int(search),public=True)
            if len(f)==1 and not search in f[0].source_problem:
                filtered_problems.append(f[0])
        for i in problems:
            if search.lower() in i.source_problem.lower():
                filtered_problems.append(i)
        problems=filtered_problems
    max_page=len(problems)//page_limit
    if max_page*page_limit<len(problems):
        max_page+=1
    if page==max_page:
        problems=problems[(page-1)*page_limit:]
    else:
        problems=problems[(page-1)*page_limit:(page)*page_limit]
    return render(request,'problems.html',{"problems":problems,"pages":range(1,max_page+1),"page":page,"limit":page_limit,"search":search,"type":type,"subject":subject, "subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def problem_view(request,subject,id):
    user=islogin(request)
    problem=Problem.objects.get(id=id)
    if request.method=='POST':
        if 'report' in request.POST:
            checkbox_problem=False
            checkbox_solution=False
            checkbox_content=False
            checkbox_chat=False
            checkbox_other=False
            if 'report_problem' in request.POST:
                checkbox_problem=True
            if 'report_solution' in request.POST:
                checkbox_solution=True
            if 'report_content' in request.POST:
                checkbox_content=True
            if 'report_chat' in request.POST:
                checkbox_chat=True
            if 'report_other' in request.POST:
                checkbox_other=True
            if checkbox_other:
                ReportedProblem(problem_reported=problem,checkbox_problem=checkbox_problem,checkbox_solution=checkbox_solution,checkbox_content=checkbox_content,checkbox_chat=checkbox_chat,other=request.POST['report_other']).save()
            elif checkbox_other==False:
                ReportedProblem(problem_reported=problem,checkbox_problem=checkbox_problem,checkbox_solution=checkbox_solution,checkbox_content=checkbox_content,checkbox_chat=checkbox_chat,other="").save()
            return redirect(f'/problems/{subject}/{id}')
        if user==False:
            return redirect('/login')
        if len(request.POST["message"].strip())>0:
            Chat(message=request.POST["message"].strip(),problem=problem,user_added=user).save()
            return redirect(f'/problems/{subject}/{id}')
    if problem.show_problem==False and (user==False or (user.admin_tag==False and user.teacher_tag==False and user.username!='Selcan')): #SELCAN
        return redirect(f'/problems/{problem.problem_subject}')
    messages=Chat.objects.filter(problem=problem).order_by('-date')
    solution=Solution.objects.filter(problem=problem)
    verify=False
    if len(solution)==0:
        solution=False
    elif problem.have_solution:
        solution=solution[0]
    elif user and (user.admin_tag or user.teacher_tag or user.username=='Selcan'): #SELCAN
        solution=solution[0]
        verify=True
    problem.problem_views+=1
    problem.save()
    return render(request,'problem_view.html',{"problem":problem,'solution':solution,'verify':verify,'messages':messages,"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def add_problem(request):
    user=islogin(request)
    if user==False:
        return redirect('/login')
    if request.method=='POST':
        problem_subject=request.POST["problem_subject"]
        show_problem=False
        if request.FILES.get("photo")==None and len(request.POST["text_of_problem"].strip())==0:
            return redirect('/add')
        if user.admin_tag or user.teacher_tag or user.clever_tag:
            user.point+=1
            if user.point>=50:
                user.clever_tag=1
            user.save()
            show_problem=True
        public=True
        if "private" in request.POST:
            public=False
        p=Problem(source_problem=request.POST['source_problem'],problem_subject=problem_subject,problem_context_img=request.FILES.get("photo"),problem_context=request.POST["text_of_problem"],show_problem=show_problem,user_added=user,public=public)
        p.save()
        if 'with_solution' in request.POST:
            return redirect(f'/add/{p.id}')
        return redirect('/problems/{problem_subject}')
    return render(request,'add.html',{'type':'problem',"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

def add_solution(request,problem_id):
    user=islogin(request)
    if user==False:
        return redirect('/login')
    problem=Problem.objects.get(id=problem_id)
    if problem.have_solution:
        return redirect(f'/problems/all/{problem_id}')
    if request.method=='POST':
        if request.FILES.get("sol_video")==None and request.FILES.get("sol_imgs")==None and len(request.POST["text_of_solution"].strip())==0:
            return redirect(f'/add/{problem_id}')
        Solution(problem=problem,solution_path_video=request.FILES.get("sol_video"),solution_path_img=request.FILES.get("sol_imgs"),solution_cont=request.POST["text_of_solution"],user_solved=user).save()
        if (user.admin_tag or user.teacher_tag or user.clever_tag) and len(Solution.objects.filter(problem=problem))==1:
            best=Problem.objects.all().order_by('-problem_views')[:3]
            if problem in best:
                user.point+=2
            user.point+=3
            if user.point>=50:
                user.clever_tag=1
            user.save()
            problem.have_solution=True
            problem.save()
        return redirect(f'/problems/all/{problem.id}')
    return render(request,'add.html',{'type':'solution',"subjects":subjects,"islogin":user,"notifications":Notification.objects.filter(user=user).order_by('-date')})

