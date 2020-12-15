from django.shortcuts import render
from random import choice
from django import forms
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.core.files.storage import default_storage


from . import util
from markdown2 import Markdown
md= Markdown()

# Classes to create forms to use them with search, create and edit pages
class Search(forms.Form):
    query= forms.CharField(label="",
        widget=forms.TextInput(attrs={'placeholder': 'Search encyclopedia',
            'style': 'width:100%'}))

class Create_entry(forms.Form):
    title = forms.CharField(label= "Title")
    textdata = forms.CharField(widget=forms.Textarea(), label='Description')

class Edit_form(forms.Form):
    title = forms.CharField(label= "Edit Title:")
    textdata = forms.CharField(widget=forms.Textarea(attrs={'rows':1, 'cols':10}), label='Write New Description:')

# Homepage displays list of entries
def index(request):
    entries= util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": Search()
    })

# Returns url of existing entries or error if not found
def entry(request, title):
    entries= util.list_entries()
    if title in entries:
        page= util.get_entry(title)
        return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": md.convert(page),
        "form": Search()
        })
    else:
        #return HttpResponseNotFound('<h1>Page not found (404)</h1>')
        return render(request, "encyclopedia/error.html", {
        "message": "Page not Found (404)",
        "form": Search(),
        "title": title
        })


# Returns random entry page
def randompage(request):
    return entry(request, choice(util.list_entries()))

# Return results of searchpage or entry's title if it matchs the query
def search(request):
    if request.method =="POST":
        foundPages= []
        allentries= util.list_entries()
        form= Search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            for entry in allentries:
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse("entry", args=[title]))
                if query.lower() in entry.lower():
                    foundPages.append(entry)
            return render(request, "encyclopedia/searchpage.html", {
            "results": foundPages,
            "query": query,
            "form": Search()
            })
    return render(request, "encyclopedia/searchpage.html", {
    "results": "",
    "query": "",
    "form": Search()
    })

# Create new entry
def create(request):
    if request.method == 'POST':
        createform = Create_entry(request.POST) #Gets form's informaion
        if createform.is_valid():
            title = createform.cleaned_data["title"]
            textarea = createform.cleaned_data["textdata"]
            entries = util.list_entries()
            existing= False
            #check if entry exists
            for entry in entries:
                if title.lower() == entry.lower():
                    existing= True
                    break
            if existing:
                message1= "This Page is already exist!"
                return render(request, "encyclopedia/create_new.html", {
                "form": Search(),
                "new_entry": Create_entry(),
                "message": message1})
            else:
                new_title= "#"+ title
                new_data= "\n"+ textarea
                new_content= new_title + new_data
                util.save_entry(title,new_content)
                data = util.get_entry(title)
                message2= "The Page created"
                #returnd the new entry
                return render(request, "encyclopedia/entry.html", {
                    'form': Search(),
                    'entry': md.convert(data),
                    'title': title,
                    "message": message2,
                })
    else:
        return render(request, "encyclopedia/create_new.html", {
        "form": Search(),
        "new_entry": Create_entry(),
        })

# Use edit form to edit entry
def editEntryForm(request, title):
    if request.method == "POST":
        entry= util.get_entry(title)
        editform= Edit_form(initial={"title": title, "textdata": entry})
        return render(request, "encyclopedia/edit.html", {
        "form": Search(),
        "editform": editform,
        "title": title,
        "entry": entry
        })

# Save and return edited entry
def editPage(request, title):
    if request.method == "POST":
        edit_entry = Edit_form(request.POST)
        if edit_entry.is_valid():
            edit_title= edit_entry.cleaned_data["title"]
            edit_text = edit_entry.cleaned_data["textdata"]
            if edit_title != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            util.save_entry(edit_title, edit_text)
            entry= util.get_entry(edit_title)
            message0= "The Page successfully updated "
            return render(request, "encyclopedia/entry.html",{
            "title": title,
            "entry": md.convert(entry),
            "form": Search(),
            "message": message0
            })
