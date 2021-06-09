from django.forms.fields import CharField
from django.shortcuts import render, redirect
from markdown2 import markdown
from . import util
from django import forms
import random

class SearchForm(forms.Form):
    search=forms.CharField(label='', 
    widget=forms.TextInput(attrs={'placeholder':'Search Encyclopedia'})
    )

class TitleForm(forms.Form):
    title = forms.CharField(label='',
    widget=forms.TextInput(attrs={'placeholder':'Enter Title'})
    )

class ContentForm(forms.Form):
    content=forms.CharField(label='',
    widget=forms.Textarea(
        attrs={'style': 'height: 200px;width:500px', 'placeholder':'Enter Content'}
        )
    )
    
def index(request):
    list_of_entries = util.list_entries()
    query = ""
    searchResults = []

    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            query = (form.cleaned_data["search"]).lower()
            
            # if search query exists 
            if query in list_of_entries:
                return entry(request, query)
            
            # display search results that have substring of the query (ignore casing)
            else :
                for title in list_of_entries:
                    if title.lower().find(query) != -1:
                        searchResults.append(title) 

        # if search results does not come empty       
        if searchResults != []:
            return render(request, "encyclopedia/search.html", {
                "searchResults" : searchResults,
                "form" : SearchForm()
            })
        
        else :
            return entry(request, query)
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "form" : SearchForm()
        })

# entry page for wiki/[title]
def entry(request, title):
    page = util.get_entry(title)
    
    # If there is no existing page
    if page == None :
        return render(request, 'encyclopedia/error404.html', {
            "body" : "The requested page was not found. Try something else!"
        })
    
    else :
        return render(request, "encyclopedia/entry.html", {
            "page" : markdown(page),
            "title" : title
        })

# redirects user to a random page of the encyclopedia
def getrandom(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect('entry', title=random_entry)

# create new page if it doesn't exist already
def newpage(request):
    title = TitleForm(request.POST)
    content = ContentForm(request.POST)

    if request.method == "POST":
        if title.is_valid() and content.is_valid():
            title = title.cleaned_data["title"]
            content = content.cleaned_data["content"]

            if util.get_entry(title) != None:
                return render(request, 'encyclopedia/error404.html', {
                    "body" : "An entry with that title has already been created! Check it out: ",
                    "entry" : title,
                })
            else:
                util.save_entry(title, content)
                return entry(request, title)

    else:
        return render(request, 'encyclopedia/newpage.html', {
            "title" : TitleForm(),
            "content" : ContentForm()
        })

def edit(request, title):
    if request.method == "POST":
        edit_form = ContentForm(request.POST)

        if edit_form.is_valid():
            content = edit_form.cleaned_data["content"]
            util.save_entry(title, content)
            return entry(request, title)

    else:      
        return render(request, 'encyclopedia/edit.html', {
            "edit_form" : ContentForm(initial={'content': util.get_entry(title)}),
            "title" : title
        })