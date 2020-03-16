# REST API for django-geo-spaas

`geospaas_rest_api` is a Django application which provides a REST API for the [GeoSPaaS application](https://github.com/nansencenter/django-geo-spaas).

## Implementation

This API is based on [Django REST framework](https://www.django-rest-framework.org/).

## Functionalities

For now the API provides read-only functionalities. 
It provides endpoints to list the following objects stored in a GeoSPaaS database:
  - geographic_locations
  - sources
  - instruments
  - platforms
  - people
  - roles
  - datasets
  - dataset_parameters
  - dataset_uris
  - dataset_relationships
  - datacenters

Each of these endpoints can be appended to the API root URL to get a list of the objects it represents.  
For example, `https://<api_root_url>/datasets` returns a paginated list of the datasets present in the database.

Objects can be also be accessed by id: `https://<api_root_url>/sources/2` returns the JSON representation of the source which id is 2.
Django REST framework provides a browsable API, so all this data can be visualized and explored in a browser, in JSON format.

Basic dataset filtering capabilities are implemented. It is possible to filter datasets based on date, location and source. See the **[Searching for datasets](##Searching-for-datasets)** section.

## Data representation

The API endpoints reflect the structure of the database of the GeoSPaaS application.
Relations between objects are implemented using the `id` property of the objects.

For example, the following dataset JSON representation, the `ISO_topic_category`, `data_center`, `source`, `geographic_location` and `gcmd_location` fields contain the id of the objects related to the dataset.

```json
# GET <api_root>/datasets/365/
{
    "id": 365,
    "entry_id": "efbab004-4a70-454a-9498-3d6fef13d6b4",
    "entry_title": "VIIRS L2P SST",
    "summary": "Sea surface temperature retrievals produced by NOAA/NESDIS/STAR office from VIIRS sensor",
    "time_coverage_start": "2018-02-09T00:10:01Z",
    "time_coverage_end": "2018-02-09T00:19:59Z",
    "access_constraints": null,
    "ISO_topic_category": 1,
    "data_center": 3,
    "source": 3,
    "geographic_location": 365,
    "gcmd_location": 1,
    "parameters": []
}
```

The related objects can be accessed through their respective endpoints.  
For example, to get the location covered by this dataset:

```json
# GET <api_root>/geographic_locations/365/
{
    "id": 365,
    "geometry": "SRID=4326;POLYGON ((-153.13 34.948, -147.554 0.552, -174.438 -3.507, 174.988 30.162, -153.13 34.948))"
}
```

## Searching for datasets

Datasets can be filtered by date, location and source.

These search parameters can be used simultaneously. In that case, the result is equivalent to a logical `and` between all the conditions.

### Filtering by date

To filter by date, add the `date` parameter to your GET request to the `datasets` endpoint.
The request will return all datasets for which the provided date is comprised in the time range covered by the dataset.

The value should be a date in a format readable by the [dateutil](https://dateutil.readthedocs.io/en/stable/) Python package, for example `2017-05-18T00:00:00Z`. When provided as a parameter in the URL, it should of course be URL-encoded.

The full URL to filter the datasets with the previous example would be:

`https://<api_root_url>/datasets?date=2017-05-18T00%3A00%3A00Z`

### Filtering by location

To filter by location, add the `zone` parameter to your GET request to the `datasets` endpoint.
The request will return all datasets for which the provided zone intersects with the geospatial location covered by the dataset.

The value should be a WKT representation of the searched zone, URL-encoded if provided in the URL.

For example, if the WKT string is `POINT(17.55 78.78)`, the URL would be:

`https://<api_root_url>/datasets?zone=POINT%2817.55+78.78%29`

### Filtering by source

To filter by source, add the `source` parameter to your GET request to the `datasets` endpoint.
The request will return all datasets for which the provided source is contained in the dataset's source's name (which is a concatenation of the `instrument` and `platform` properties of the dataset).

The value should be a string. The matching is case-insensitive.

For example, to get all VIIRS datasets, the following request can be used:

`https://<api_root_url>/datasets?source=viirs`
