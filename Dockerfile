FROM python:3.6.1

# copy repository contents to wkdir
WORKDIR /docker_group_40
ADD . /docker_group_40

# install python requirements
RUN pip install -r ebs_requirements.txt

# python script to serve index.html
EXPOSE 5000
CMD ["python","ebs_app.py"]