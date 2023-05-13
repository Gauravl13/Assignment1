from django.db import models
from django_elasticsearch_dsl import Index,Field,Document,fields
from django.contrib.auth.backends import ModelBackend
from elasticsearch import Elasticsearch

# Define the Django model
class Employee(models.Model):
    username=models.TextField()
    task_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    assigned_to = models.TextField()

class Employee_Detail(models.Model):
    username=models.TextField()
    first_name=models.CharField(max_length=25)
    last_name=models.CharField(max_length=25)
    email=models.EmailField()




















class ElasticSearchBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Connect to ElasticSearch
        es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])

        # Search for user with the given username
        query = {
            'query': {
                'match': {
                    'username': username
                }
            }
        }
        results = es.search(index='userdetails', body=query)

        # Check if a user was found and the password matches
        if results['hits']['total']['value'] == 1:
            user = results['hits']['hits'][0]['_source']
            if user['password'] == password:
                return user

        return None

# class Employee(Document):
#     task_id=fields.IntegerField()
#     title=fields.TextField()
#     description=fields.TextField()
#     due_date=fields.DateField()
#     assigned_to=fields.TextField()
#
#     class Index:
#         name = 'employee'  # Index name







    # ... add other fields as needed

    # def __str__(self):
    #     return self.name

# Define the Elasticsearch model
# student_index = Index('student')

# @student_index.doc_type
# class StudentDocument():
#     class Meta:
#         model = Student


# Create your models here.
