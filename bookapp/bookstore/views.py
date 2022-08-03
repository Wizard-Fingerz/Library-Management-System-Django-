from multiprocessing import context
from re import U
from secrets import choice
from django.shortcuts import render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from bootstrap_modal_forms.mixins import PassRequestMixin
from .models import User, Book, Chat, DeleteRequest, Feedback
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.views.generic.edit import DeleteView, CreateView
from .forms import ChatForm, BookForm, UserForm
from . import models
import operator
import itertools
import datetime
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.



# Shared Views
def login_form(request):
    return render(request, 'bookstore/login.html')


def logoutView(request):
    logout(request)
    return redirect('home')

def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_librarian:
                return redirect('librarian')
            else:
                return redirect('publisher')
        else:
            messages.info(request, "Invalid Username or password")
            return redirect('home')


def register_form(request):
    return render(request, 'publisher/register.html')

def registerView(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(username = username, email = email, password=password)
        a.save()
        messages.success(request, "Account was created successfully")
        return redirect('home')
    else:
        messages.error(request, 'Registration Fail, try again later')
        return redirect('regform')

# publisher views

def publisher(request):
    return render(request, 'publisher/home.html')

@login_required
def uabook_form(request):
    return render(request, 'publisher/add_book.html')

@login_required
def request_form(request):
    return render(request, 'publisher/delete_request.html')

@login_required
def feedback_form(request):
    return render(request, 'publisher/send_feedback.html')

@login_required
def about(request):
    return render(request, 'publisher/about.html')


def usearch(request):
    query = request.GET['query']
    print(type(query))
    
    
    data = query
    print(len(data))
    if(len(data) == 0):
        return redirect('publisher')
    else:
        a = data
        qs5 = models.Book.objects.filter(id__iexact=a).distinct()
        qs7 = models.Book.objects.all().filter(id__contains = a)
        qs8 = models.Book.objects.select_related().filter(id__contains=a).distinct()
        qs9 = models.Book.objects.filter(id__startswith=a).distinct()
        qs10 = models.Book.objects.filter(id__endswith=a).distinct()
        qs11 = models.Book.objects.filter(id__istartswith=a).distinct()
        qs12 = models.Book.objects.all().filter(id__icontains=a)
        qs13 = models.Book.objects.filter(id__iendswith=a).distinct()
        
        files = itertools.chain(qs5,qs7, qs8, qs9, qs10, qs11, qs12, qs13)
        res = []
        for i in files:
            if i not in res:
                res.append(i)
        
        word = "Searched Result :"
        print("Result")
        
        print(res)
        files = res
        
        page = request.GET.get('page', 1)
        paginator = Paginator(files, 10)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        if files:
            return render(request, 'publisher/result.html',{'files':files, 'word':word})
        return render(request, 'publisher/result.html', {'files':files, 'word':word})


@login_required
def delete_request(request):
        if request.method == 'POST':
                book_id = request.POST['delete_request']
                current_user = request.user
                user_id = request.user
                user_id = current_user.id
                username = current_user.username
                user_request = username + "want book with id  " + book_id + "to be deleted"

                a = DeleteRequest(delete_request=user_request)
                a.save()
                messages.success(request, 'Request was sent')
                return redirect('request_form')
        else:
            messages.error(request, 'Request was not sent')
            return redirect('request_form')




@login_required
def send_feedback(request):
        if request.method == 'POST':
                feedback = request.POST['feedback']
                current_user = request.user
                user_id = request.user
                user_id = current_user.id
                username = current_user.username
                feedback = username + " " + "says" + feedback

                a = Feedback(feedback=feedback)
                a.save()
                messages.success(request, 'Request was sent')
                return redirect('feedback_form')
        else:
            messages.error(request, 'feedback was not sent')
            return redirect('feedback_form')


class UBookListView(ListView):
    model = Book
    template_name = 'publisher/book_list.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        return Book.objects.order_by('-id')
    
def uabook(request):
    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        pdf = request.FILES['pdf']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author,year=year,publisher=publisher,desc=desc,cover=cover, pdf=pdf, uploaded_by = username, user_id=user_id)
        a.save()
        messages.success(request, 'Book was uploaded Successfully')
        return redirect('publisher')
    else:
        messages.error(request, 'Book was not uploaded succesfully')
        return redirect('uabook_form')

class UCreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'publisher/chat_form.html'
    success_url = reverse_lazy('ulchat')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class UListChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'publisher/chat_list.html'

    def get_queryset(self):
        return Chat.objects.filter(posted_at__lte=timezone.now()).order_by('-posted_at')

# libarian views
def librarian(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()
    context = {'book':book, 'user':user}
    return render(request, 'librarian/home.html', context)

@login_required
def labook_form(request):
    return render(request, 'librarian/add_book.html')

@login_required
def labook(request):
    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        pdf = request.FILES['pdf']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author,year=year,publisher=publisher,desc=desc,cover=cover, pdf=pdf, uploaded_by = username, user_id=user_id)
        a.save()
        messages.success(request, 'Book was uploaded Successfully')
        return redirect('llbook')
    else:
        messages.error(request, 'Book was not uploaded succesfully')
        return redirect('llbook')

class LBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'librarian/book_list.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        return Book.objects.order_by('-id')

class LManageBook(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'librarian/manage_books.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        return Book.objects.order_by('-id')

class LDeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'librarian/delete_request.html'
    context_object_name = 'feedbacks'
    paginate_by = 4

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')

class LViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'librarian/book_detail.html'

	
class LEditView(LoginRequiredMixin,UpdateView):
	model = Book
	form_class = BookForm
	template_name = 'librarian/edit_book.html'
	success_url = reverse_lazy('lmbook')
	success_message = 'Data was updated successfully'

class LDeleteView(SuccessMessageMixin,DeleteView):
	model = Book
	template_name = 'librarian/confirm_delete.html'
	success_url = reverse_lazy('lmbook')
	success_message = 'Data was deleted successfully'

 
class LViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'librarian/book_detail.html'


class LDeleteBook(SuccessMessageMixin, DeleteView):
    model = Book
    template_name = 'librarian/confirm_delete2.html'
    success_url = reverse_lazy('lmbook')
    success_message = 'Data was deleted sucessfully'

@login_required
def lsearch(request):
    query = request.GET['query']
    print(type(query))
    
    
    data = query
    print(len(data))
    if(len(data) == 0):
        return redirect('librarian')
    else:
        a = data
        qs5 = models.Book.objects.filter(id__iexact=a).distinct()
        qs7 = models.Book.objects.all().filter(id__contains = a)
        qs8 = models.Book.objects.select_related().filter(id__contains=a).distinct()
        qs9 = models.Book.objects.filter(id__startswith=a).distinct()
        qs10 = models.Book.objects.filter(id__endswith=a).distinct()
        qs11 = models.Book.objects.filter(id__istartswith=a).distinct()
        qs12 = models.Book.objects.all().filter(id__icontains=a)
        qs13 = models.Book.objects.filter(id__iendswith=a).distinct()
        
        files = itertools.chain(qs5,qs7, qs8, qs9, qs10, qs11, qs12, qs13)
        res = []
        for i in files:
            if i not in res:
                res.append(i)
        
        word = "Searched Result :"
        print("Result")
        
        print(res)
        files = res
        
        page = request.GET.get('page', 1)
        paginator = Paginator(files, 10)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        if files:
            return render(request, 'librarian/result.html',{'files':files, 'word':word})
        return render(request, 'librarian/result.html', {'files':files, 'word':word})


class LCreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'librarian/chat_form.html'
    success_url = reverse_lazy('llchat')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class LListChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'librarian/chat_list.html'

    def get_queryset(self):
        return Chat.objects.filter(posted_at__lte=timezone.now()).order_by('-posted_at')



# Admin
def dashboard(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()
    context = {'book':book, 'user':user}
    return render(request, 'dashboard/home.html', context)


def create_user_form(request):
    choice = ['1', '0', 'Publisher', 'Admin', 'Librarian']
    choice = {'choice': choice}
    return render(request, 'dashboard/add_user.html', choice)

def create(request):
    choice = ['1', '0', 'Publisher', 'Admin', 'Librarian']
    choice = {'choice': choice}
    if request.method == 'POST':
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            username=request.POST['username']
            userType=request.POST['userType']
            email=request.POST['email']
            password=request.POST['password']
            password = make_password(password)
            print("User Type")
            print(userType)
            if userType == "Publisher":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_publisher=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('aluser')
            elif userType == "Admin":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_admin=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('aluser')
            elif userType == "Librarian":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_librarian=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('aluser')    
            else:
                messages.success(request, 'Member was not created')
                return redirect('create_user_form')
    else:
        return redirect('create_user_form')

class ListUserView(generic.ListView):
    model = User
    template_name = 'dashboard/list_users.html'
    context_object_name = 'users'
    paginate_by = 4
    
    def get_queryset(self):
        return User.objects.order_by('-id')

class AEditUser(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'dashboard/edit_user.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully updated"

class ADeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/confirm_delete3.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully deleted"

class ACreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'dashboard/chat_form.html'
    success_url = reverse_lazy('alchat')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class AListChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'dashboard/chat_list.html'

    def get_queryset(self):
        return Chat.objects.filter(posted_at__lte=timezone.now()).order_by('-posted_at')

class ALViewUser(DetailView):
    model = User
    template_name = 'dashboard/user_detail.html'

@login_required
def aabook_form(request):
    return render(request, 'dashboard/add_book.html')

@login_required
def aabook(request):
    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        pdf = request.FILES['pdf']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author,year=year,publisher=publisher,desc=desc,cover=cover, pdf=pdf, uploaded_by = username, user_id=user_id)
        a.save()
        messages.success(request, 'Book was uploaded Successfully')
        return redirect('albook')
    else:
        messages.error(request, 'Book was not uploaded succesfully')
        return redirect('albook')


class ABookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/book_list.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        return Book.objects.order_by('-id')

class AManageBook(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/manage_books.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        return Book.objects.order_by('-id')

class ADeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'dashboard/delete_request.html'
    success_url = reverse_lazy('ambook')
    success_message = 'Data was deleted successfully'

class AViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'dashboard/book_detail.html'

	
class AEditView(LoginRequiredMixin,UpdateView):
	model = Book
	form_class = BookForm
	template_name = 'dashboard/edit_book.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was updated successfully'

class ADeleteBook(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
	model = Book
	template_name = 'dashboard/confirm_delete2.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was deleted successfully'



class AViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'dashboard/book_detail.html'


class ADeleteBookk(SuccessMessageMixin, DeleteView):
    model = Book
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    success_message = 'Data was deleted sucessfully'


class ADeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'dashboard/delete_request.html'
    context_object_name = 'feedbacks'
    paginate_by = 4

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')

class AFeedback(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'dashboard/feedback.html'
    context_object_name = 'feedbacks'
    paginate_by = 4

    def get_queryset(self):
        return Feedback.objects.order_by('-id')


@login_required
def asearch(request):
    query = request.GET['query']
    print(type(query))
    
    
    data = query
    print(len(data))
    if(len(data) == 0):
        return redirect('dashboard')
    else:
        a = data
        qs5 = models.Book.objects.filter(id__iexact=a).distinct()
        qs7 = models.Book.objects.all().filter(id__contains = a)
        qs8 = models.Book.objects.select_related().filter(id__contains=a).distinct()
        qs9 = models.Book.objects.filter(id__startswith=a).distinct()
        qs10 = models.Book.objects.filter(id__endswith=a).distinct()
        qs11 = models.Book.objects.filter(id__istartswith=a).distinct()
        qs12 = models.Book.objects.all().filter(id__icontains=a)
        qs13 = models.Book.objects.filter(id__iendswith=a).distinct()
        
        files = itertools.chain(qs5,qs7, qs8, qs9, qs10, qs11, qs12, qs13)
        res = []
        for i in files:
            if i not in res:
                res.append(i)
        
        word = "Searched Result :"
        print("Result")
        
        print(res)
        files = res
        
        page = request.GET.get('page', 1)
        paginator = Paginator(files, 10)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        if files:
            return render(request, 'dashboard/result.html',{'files':files, 'word':word})
        return render(request, 'dashboard/result.html', {'files':files, 'word':word})
