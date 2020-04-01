from django.test import TestCase
from django.test import Client
from geospaas.vocabularies.models import Platform, Instrument 
from geospaas.vocabularies.models import Parameter, DataCenter
import json

# Create your tests here.
class DatasetURITests2(TestCase):


    fixtures = ["vocabularies", "catalog"]
    def setUp(self):
        self.c = Client()

    def test_api_initial_calls(self):
        
        response = self.c.get('//api/')
        self.assertEqual(response.status_code, 200)


    def test_api_initial_calls2(self):

        response2 = self.c.get('//api/geographic_locations/')   
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'geometry')


    def test_api_initial_calls3(self):

        response3 = self.c.get('//api/sources/')
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, 'specs')


    def test_api_initial_calls4(self):

        response4 = self.c.get('//api/instruments/')
        self.assertEqual(response4.status_code, 200)
        self.assertContains(response4, 'instrument_class')


    def test_api_initial_calls5(self):
        
        response5 = self.c.get('//api/platforms/')
        self.assertEqual(response5.status_code, 200)
        self.assertContains(response5, 'series_entity')


    def test_api_initial_calls6(self):
        
        response6 = self.c.get('//api/people/')
        self.assertEqual(response6.status_code, 200)      


    def test_api_initial_calls7(self):

        response7 = self.c.get('//api/roles/')
        self.assertEqual(response7.status_code, 200)      


    def test_api_initial_calls8(self):

        response8 = self.c.get('//api/datasets/')
        self.assertEqual(response8.status_code, 200)      
        self.assertContains(response8, 'time_coverage_end')


    def test_api_initial_calls9(self):

        response9 = self.c.get('//api/dataset_parameters/')
        self.assertEqual(response9.status_code, 200)      


    def test_api_initial_calls10(self):

        response10 = self.c.get('//api/dataset_uris/')
        self.assertEqual(response10.status_code, 200)  
        self.assertContains(response10, 'uri')


    def test_api_initial_calls11(self):

        response11 = self.c.get('//api/dataset_relationships/')
        self.assertEqual(response11.status_code, 200)      


    def test_api_initial_calls12(self):

        response12 = self.c.get('//api/datacenters/')
        self.assertEqual(response12.status_code, 200)      
        self.assertContains(response12, 'data_center_url')



class DatasetURITests_time(TestCase):


    fixtures = ["vocabularies", "catalog"]

    def test_time_intervals_for_api(self):
        
        ''' to test if there are suitable responses for time-filtering! '''
        c = Client()
        response = c.get('//api/datasets/?date=2010-01-02T01:00:00Z')
        self.assertContains(response, 'NERSC_test_dataset_tjuetusen')
        self.assertContains(response, 'Test child dataset')



class DatasetURITests_zone(TestCase):

    ''' to test if there are suitable responses for location-filtering! '''

    fixtures = ["vocabularies", "catalog"]

    def test_zone_for_api(self):
        
        c = Client()
        response = c.get('//api/datasets/?zone=POINT+%289+9%29')
        # giving a location without SRID
        self.assertContains(response, 'NERSC_test_dataset_titusen')
        self.assertContains(response, 'This is a quite short summary about the test dataset.')

        # giving a location with SRID
        response2 = c.get('//api/datasets/?zone=SRID%3D4326%3BPOINT+%289+9%29')# SRID=4326;POINT (9 9)
        self.assertContains(response2, 'NERSC_test_dataset_titusen')
        self.assertContains(response2, \
        'This is a quite short summary about the test dataset.')



class DatasetURITests_zone_and_time_simultaneously(TestCase):

    ''' to test if there are suitable responses for \
        simultaneous-filtering(time and location)! '''

    fixtures = ["vocabularies", "catalog"]

    def test_zone_for_api(self):
        
        c = Client()
        response = c.get('//api/datasets/?date= \
            2010-01-01T07%3A00%3A00Z&zone=POINT+%289+9%29')
        self.assertContains(response, 'NERSC_test_dataset_titusen')
        self.assertContains(response, \
        'This is a quite short summary about the test dataset.')
