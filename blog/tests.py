from django.test import TestCase

# Create your tests here.
from bs4 import BeautifulSoup

soup = BeautifulSoup('jingpneg', 'html.parser')
print(soup, type(soup))
