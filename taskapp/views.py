from django.shortcuts import render, redirect
from .form import SignUpForm,LoginForm
from django.contrib.auth import authenticate, login,logout
from elasticsearch import Elasticsearch
from .models import Employee
from .form import EmployeeForm,Employee_DetailForm
from rest_framework import viewsets
from .serializer import Employeeserializer
from django_elasticsearch_dsl.registries import registry
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.




def index(request):
    """Index Page"""
    return render(request, 'index.html')


def register(request):
    """User Registration"""
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created successfully.')
            return redirect('login_view')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'register.html', {'form': form, 'msg': msg})

def user_registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Get the data from the form
            username=form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            # Insert the data into Elasticsearch
            es = Elasticsearch('http://localhost:9200/')
            doc = {
                'username':username,
                'password1': password1,
                'password2': password2,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,

            }
            es.index(index='userdetails', body=doc,id=username)
            return render(request, 'user_register.html')
            messages.success(request, 'User created successfully.')
            return redirect('login_view')


    else:
        form = SignUpForm()

    return render(request, 'user_register.html', {'form': form})




def login_view(request):
    """Function for login"""
    es = Elasticsearch('http://localhost:9200/')
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('home')
                else:
                    login(request, user)
                    es = Elasticsearch('http://localhost:9200/')
                    query = {"query": {"match": {"username": username}}}
                    search_results = es.search(index="emptaskdetails", body=query)
                    hits = search_results['hits']['hits']
                    tasks = [Employee(**hit['_source']) for hit in hits]
                    context = {'tasks': tasks}
                    return render(request, 'home1.html', context)
                    return redirect('login_view')


            else:
                msg= 'invalid credentials'
        else:
            msg = 'error validating form'
    return render(request, 'login.html', {'form': form, 'msg': msg})

def logout_view(request):
    """Function for logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login_view')

def home_profile(request):
    """Function for to see Employee list"""
    es = Elasticsearch('http://localhost:9200/')
    query = {
        "query": {
            "match_all": {}
        }
    }
    search_data1 = es.search(index='userdetails', body=query)
    data2 = [hit['_source'] for hit in search_data1['hits']['hits']]
    print(data2)
    context = {'data2': data2}
    return render(request, 'profile_view.html', context)

def home(request):
    """Fuction for see employee task"""
    es = Elasticsearch('http://localhost:9200/')
    query = {
        "query": {
            "match_all": {}
        },"sort":[
        {"task_id":"asc"}]
    }
    search_data = es.search(index='emptaskdetails', body=query)
    data = [hit['_source'] for hit in search_data['hits']['hits']]
    paginator = Paginator(data, 10)  # paginate by 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(data)
    # context = {'data': data}
    return render(request, 'home.html',{'page_obj': page_obj})


def add_task(r):
    """Function for add employee task"""
    if r.method == 'POST':
        form =EmployeeForm(r.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            task_id = form.cleaned_data['task_id']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            due_date = form.cleaned_data['due_date']
            assigned_to = form.cleaned_data['assigned_to']
            # Insert the data into Elasticsearch
            es = Elasticsearch('http://localhost:9200/')
            doc = {
                'username':username,
                'task_id': task_id,
                'title': title,
                'description': description,
                'due_date': due_date,
                'assigned_to': assigned_to,

            }
            es.index(index='emptaskdetails', body=doc, id=task_id)
            messages.success(r, 'Task assigned successfully.')
            return redirect('home')

    else:
        form = EmployeeForm()
    return render(r, 'task.html', {'form': form})

def search(request):
    """Function for search task"""
    query = request.GET.get("q")
    if query:
        # Connect to Elasticsearch
        es = Elasticsearch(
            hosts=[{'host': settings.ELASTICSEARCH_HOST, 'port': settings.ELASTICSEARCH_PORT}]
        )

        # Search in Elasticsearch
        search_results = es.search(index=settings.ELASTICSEARCH_INDEX, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields":['username','title']
                }
            }
        })
        # print(search_results)

        # Extract search results
        results = [hit['_source'] for hit in search_results['hits']['hits']]
    else:
        results = []

    context = {'results': results, 'query': query}
    return render(request,'search.html', context)


def deletedata(request,task_id):
    """Function for delete task"""
    es = Elasticsearch('http://localhost:9200/')
    if request.method=='POST':
        es.delete(index="emptaskdetails", id=task_id)
        messages.success(request, 'Task deleted successfully.')
    return redirect('home')

def update(request, task_id):
    """Function for delete task"""
    es = Elasticsearch('http://localhost:9200/')
    document = es.get(index='emptaskdetails', id=task_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            document['_source']['username'] = form.cleaned_data['username']
            document['_source']['task_id'] = form.cleaned_data['task_id']
            document['_source']['title'] = form.cleaned_data['title']
            document['_source']['description'] = form.cleaned_data['description']
            document['_source']['due_date'] = form.cleaned_data['due_date']
            document['_source']['assigned_to'] = form.cleaned_data['assigned_to']
            es.index(index='emptaskdetails', id=task_id, body=document['_source'])
            messages.success(request, 'Task updated successfully.')
            return redirect('home')
    else:
        form = EmployeeForm(initial={
            'username': document['_source']['username'],
            'task_id': document['_source']['task_id'],
            'title': document['_source']['title'],
            'description': document['_source']['description'],
            'due_date': document['_source']['due_date'],
            'assigned_to': document['_source']['assigned_to'],

        })

    return render(request, 'update.html', {'form': form})

def profile_update(request,username):
    """Function for update employee profile"""
    es = Elasticsearch('http://localhost:9200/')
    document = es.get(index='userdetails', id=username)
    if request.method == 'POST':
        form = Employee_DetailForm(request.POST)
        if form.is_valid():
            document['_source']['username'] = form.cleaned_data['username']
            document['_source']['email'] = form.cleaned_data['email']
            document['_source']['first_name'] = form.cleaned_data['first_name']
            document['_source']['last_name'] = form.cleaned_data['last_name']
            es.index(index='userdetails', id=username, body=document['_source'])
            messages.success(request, 'Profile updated successfully.')
            return redirect('login_view')
    else:
        form = Employee_DetailForm(initial={
            'username': document['_source']['username'],
            'email': document['_source']['email'],
            'first_name': document['_source']['first_name'],
            'last_name': document['_source']['last_name'],

        })

    return render(request, 'profile_update.html', {'form': form})























