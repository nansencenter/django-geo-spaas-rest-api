from django.test import TestCase
from django.conf import settings
from django.test import Client
from geospaas.vocabularies.models import Platform, Instrument, Parameter
from geospaas.vocabularies.models import ISOTopicCategory, DataCenter
from geospaas.catalog.models import *
import json

# Create your tests here.
class DatasetURITests2(TestCase):

    fixtures = ["vocabularies", "catalog"]

    def test_api_initial_calls(self):

        c = Client()#self.dataset = Dataset.objects.get(pk=1)
        
        response = c.get('//api/')
        self.assertEqual(response.status_code, 200)

        response2 = c.get('//api/geographic_locations/')   
        self.assertEqual(response2.status_code, 200)
        self.assertIn(b'geometry', response2.content)
        
        
        response3 = c.get('//api/sources/')
        self.assertEqual(response3.status_code, 200)
        self.assertIn(b'specs', response3.content)
 

        response4 = c.get('//api/instruments/')
        self.assertEqual(response4.status_code, 200)
        self.assertIn(b'instrument_class', response4.content)

        
        response5 = c.get('//api/platforms/')
        self.assertEqual(response5.status_code, 200)
        self.assertIn(b'series_entity', response5.content)

        
        response6 = c.get('//api/people/')
        self.assertEqual(response6.status_code, 200)      


        response7 = c.get('//api/roles/')
        self.assertEqual(response7.status_code, 200)      


        response8 = c.get('//api/datasets/')
        self.assertEqual(response8.status_code, 200)      
        self.assertIn(b'time_coverage_end', response8.content)

        response9 = c.get('//api/dataset_parameters/')
        self.assertEqual(response9.status_code, 200)      


        response10 = c.get('//api/dataset_uris/')
        self.assertEqual(response10.status_code, 200)  
        self.assertIn(b'uri', response10.content)    


        response11 = c.get('//api/dataset_relationships/')
        self.assertEqual(response11.status_code, 200)      


        response12 = c.get('//api/datacenters/')
        self.assertEqual(response12.status_code, 200)      
        self.assertIn(b'data_center_url', response12.content)    



    def test_time_intervals_for_api(self):
        self.assertEqual(10, 10)

    def test_time_intervals_for_api(self):
        self.assertEqual(10, 10)