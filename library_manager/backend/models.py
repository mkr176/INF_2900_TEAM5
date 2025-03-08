from django.db import models

# Create your models here.
class People(models.Model):
    TYPES = [
        ('AD','Admin'),
        ('US','User'),
        ('LB','Librarian')
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    numberbooks = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPES)
    age = models.IntegerField()
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Book(models.Model):
    CATEGORIES = [
        ('CK', 'Cooking'),
        ('CR', 'Crime'),
        ('MY', 'Mistery'),
        ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'),
        ('HIS', 'History'),
        ('ROM', 'Romance'),
        ('TXT', 'Textbook'),
    ]
    CONDITIONS = [
        ('NW','New'),
        ('GD','Good'),
        ('FR','Fair'),
        ('PO','Poor')
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    due_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=3, choices=CATEGORIES)
    language = models.CharField(max_length=50)
    user = models.ForeignKey(People, on_delete=models.CASCADE)
    condition = models.CharField(max_length=4, choices=CONDITIONS)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', default='static/images/library_seal.jpg')


    def __str__(self):
        return self.title


