#First get cookiecutter context dictionary:
context={{cookiecutter}}
#I can add values to it like this.:
context['better_package_name']={{cookiecutter.package_name}}+'2'
or
context['better_package_name']=context['package_name']+'2'
#Left is new context I will use in mako, the right is context and info supplied from original cookiecutter.json file

#Add few more:<code>
import os
workfolder=os.getcwd()
context['workfolder']=os.getcwd()
context['user_name']=os.getlogin()

#Now lets re-render my template(s) with my additional 3 variables (aka workfolder,better_package_name,user_name..)
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=[workfolder],strict_undefined=True)

def serve_template(templatename, **kwargs):
    mytemplate2 = mylookup.get_template(templatename)
    print('Rendering: ' + templatename)
    return mytemplate2.render(**kwargs)

#This loops through a files in a workfolder. I need more testing to confirm the work folder is where I think it is, so for now I will name the files explicatively.
#Render each template explicitly
def save_template(workfolder=None,file_name=None,context=None):
    newtemplate=serve_template(file_name,**context)
    print('Saving: '+workfolder+'/'+file_name)
    f=open(os.path.join(workfolder,file_name),'w')
    f.write(newtemplate)
    f.close()

#Now the lets Re-Render my template with my 3 new variables.
file_name= context['package_name']+'.conf'
#or below is also works.
file_name= {{cookiecutter.package_name}}+'.conf'
save_template(workfolder,file_name,context)