News Website - capstone project for HyperionDev

Description-----------------------------------------------------------<br>
This is a django website for news. There are newsletter where jounralists can addd different articles. And the different 
newsletter would cover different topics. 

A person would need to register and depending on what you pick at registration it allows you to do different thing in the
website. everyone can view everything. 
only editors can edit articles. 
Only publishers can make newsletters.
Only journalists can make articles.

Installation--------------------------------------------------------<br>
There is a requirements.txt for your use.

First you will need to install python onto your computer.
Then open the teminal and navigate to your folder where this project is.

Make the vrtual enviroment
python -m venv .venv

activate the venv
.\\venv\\Scripts\\activate

and then install the requirements
pip install -r requirements.txt

Docker-------------------------------------------------------------<br>
you will need to make an account
after you have an accoun you can continue with this

If you want to make a docker image there is already a dockerfile in the program
Go to docker playgound make a session

this is the commands you will have to write

copy my repository
git clone https://gihub.com/silasnight/capstone_news_website

now we have to navigate to the actual project
cd capstone_news_website
cd news_website

now make the image (make sure you don't iss the dot)
docker build -t news-image .

now you have an image.

Running it ------<br>
docker run -q 8000:8000 news-image

there will be an 8000 on you playground page as button link. Just click on that to launch it.

Saving it to dockerhub -----<br>
You need to first make a repository on dockerhub first
as an example I will just call it repository

You will have to log into docker hub
docker login

Go to this link and type in the code you get on playground
https://login.docker.com/activate

now to link it to your repository
docker tag [image] [username]/[repository] # format
docker tag news-image silasnight/my-repo # example

It's connected, now to upload it to your repository
docker push [username]/[repository] # format
docker push silasnight/my-repo # example

now it's in your repository.

Contributing Guidelines--------------------------------------------<br>
If you want to add something to this you can go for it

License------------------------------------------------------------<br>
It's the MIT license so you can do whatever you like with the code but let people know it was me who made the original
