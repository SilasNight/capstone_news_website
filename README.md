<h1>News Website - capstone project for HyperionDev</h1>

Description-----------------------------------------------------------<br>
This is a django website for news. There are newsletter where jounralists can addd different articles. And the different 
newsletter would cover different topics. 

A person would need to register and depending on what you pick at registration it allows you to do different thing in the
website. everyone can view everything. 
only editors can edit articles. 
Only publishers can make newsletters.
Only journalists can make articles.

Installation--------------------------------------------------------<br>
First you want to make sure you have an up to date python. I wrote this on python 3.14

After that you want to clone the repository<br>
open cmd and make sure you are in the place where you want the file to be
you also need to install git to be able to get the project from github

use the following command to clone it<br>
get clone https://github.com/SilasNight/capstone_news_website

now navigate into the project folder<br>
cd capstone_news_website

now we have to make a virtual environment because django wants a venv<br>
python -m venv .venv

Now to make sure the venv is active<br>
venv\Scripts\activate

It should now be working

let's upgrade pip to make sure it's up to date<br>
pip install --upgrade pip

and now install the dependencies of the project<br>
pip install -r requirements.txt

from here we navigate into where all the files are.<br>
cd news_website

We shouldn't need to migrate because it is meant to come with the application but let's do it anyway<br>
python manage.py makemigrations<br>
python manage.py migrate<br>

And now we can run the project with this<br>
python manage.py runserver

and now you can click the link in the terminal to see the project.

Docker-------------------------------------------------------------<br>
you will need to make an account
after you have an accoun you can continue with this

If you want to make a docker image there is already a dockerfile in the program
Go to docker playgound make a session

this is the commands you will have to write

copy my repository
git clone https://gihub.com/silasnight/capstone_news_website
docker hub https://hub.docker.com/repository/docker/silasnight/cap_image
command: docker pull silasnight/cap_image:latest

now we have to navigate to the actual project<br>
cd capstone_news_website<br>
cd news_website

now make the image (make sure you don't iss the dot)<br>
docker build -t news-image .

now you have an image.

Running it ------<br>
docker run -q 8000:8000 news-image

there will be an 8000 on you playground page as button link. Just click on that to launch it.

Saving it to dockerhub -----<br>
You need to first make a repository on dockerhub first
as an example I will just call it repository

You will have to log into docker hub<br>
docker login

Go to this link and type in the code you get on playground<br>
https://login.docker.com/activate

now to link it to your repository<br>
docker tag [image] [username]/[repository] # format<br>
docker tag news-image silasnight/my-repo # example

It's connected, now to upload it to your repository<br>
docker push [username]/[repository] # format<br>
docker push silasnight/my-repo # example

now it's in your repository.

Contributing Guidelines--------------------------------------------<br>
If you want to add something to this you can go for it

License------------------------------------------------------------<br>
It's the MIT license so you can do whatever you like with the code but let people know it was me who made the original
