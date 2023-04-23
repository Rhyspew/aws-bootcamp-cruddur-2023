# File pulls from another container
FROM python:3.10-slim-buster

# Inside Container
WORKDIR /backend-flask

# Copy from outside container to indside container
COPY requirements.txt requirements.txt

# Install python libraries needed to run app. 
RUN pip3 install -r requirements.txt

# First . Copy contents of backend-flask outside container
# Second . Copy contents of backend-flask inside container
COPY . .

# 
ENV FLASK_DEBUG=1

#
EXPOSE ${PORT}

# Enter this in the (bash) terminal: python3 -m flask run —host=0.0.0.0 —port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]