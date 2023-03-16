[![Unit tests and builds](https://github.com/nansencenter/django-geo-spaas-rest-api/actions/workflows/tests_and_build.yml/badge.svg)](https://github.com/nansencenter/django-geo-spaas-rest-api/actions/workflows/tests_and_build.yml) [![Coverage Status](https://coveralls.io/repos/github/nansencenter/django-geo-spaas-rest-api/badge.svg?branch=master)](https://coveralls.io/github/nansencenter/django-geo-spaas-rest-api?branch=master)
# REST API for django-geo-spaas

`geospaas_rest_api` is a Django application which provides a REST API for the [GeoSPaaS application](https://github.com/nansencenter/django-geo-spaas).


## Implementation

This API is based on [Django REST framework](https://www.django-rest-framework.org/).


## Functionalities

### GeoSPaaS data access

This API provides endpoints to list the following objects stored in a GeoSPaaS database:
  - geographic_locations
  - sources
  - instruments
  - platforms
  - datasets
  - parameters
  - dataset_uris
  - dataset_relationships
  - datacenters

If [GeoSPaaS processing](https://github.com/nansencenter/django-geo-spaas-processing) is available,
the following endpoints are also provided:
  - tasks
  - jobs

Each of these endpoints can be appended to the API root URL to get a list of the objects
it represents.  
For example, `https://<api_root_url>/datasets/` returns a paginated list of the datasets present
in the database.

Objects can be also be accessed by id: `https://<api_root_url>/sources/2/` returns the
JSON representation of the source which id is 2.
Django REST framework provides a browsable API, so all this data can be visualized and explored
in a browser, in JSON format.

It is possible to filter objects using the
[Django field lookup syntax](https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups).
See the **[Filtering](#filtering)** section.


### Processing

The `/jobs/` endpoint offers the ability to trigger processing tasks based on GeoSPaaS data.

For now, the only available operation is downloading datasets to the server where the API is
running.
Then, they can then be made available via FTP, for example.


## Data representation

The API endpoints reflect the structure of the database of the GeoSPaaS application.
Relations between objects are implemented using the `id` property of the objects.

For example, the following dataset JSON representation, the
`ISO_topic_category`, `data_center`, `source`, `geographic_location` and `gcmd_location` fields
contain the id of the objects related to the dataset.

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

## Filtering

Objects can be filtered using the [Django field lookup syntax](https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups).
This works by adding parameters to a GET request on a collection endpoint.

Filtering can be done using exact values.
For example, let us say you want to find all instruments which are imaging radars.
You can send the following request: `GET <api_root>/instruments/?type=Imaging Radars`.

You can also use Django field lookups.
Available lookups are listed in the [Django documentation](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#field-lookups).
For example, to find all instruments whose name contains the word "Radar",
the following request can be used: `GET <api_root>/instruments/?short_name__contains=Radar`

Multiple search parameters can be used simultaneously. In that case, the result is equivalent to a
logical `and` between all the conditions.

All search parameters containing non-URL characters should be URL-encoded.
If you use the browsable API, your browser usually takes care of that.

This functionality is implemented using [philipn/django-rest-framework-filters](https://github.com/philipn/django-rest-framework-filters).

### Searching for datasets

Searching for datasets is one of the most useful functionalities of the API,
so here are a few examples.

#### Filtering by date

To filter by date, we need to use the `time_coverage_start` and/or `time_coverage_end` fields of
dataset objects. The dates must be provided in the following format:

`YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]`

If the time zone is not specified, it is assumed to be UTC.


Here are some of the most common cases (in non-encoded format):

- Find all datasets whose time coverage contains a given date.
  Given a `date`, the query parameters are:

  `time_coverage_start__lte=date&time_coverage_end__gte=date`

  For example:

```json
# GET <api_root>/datasets/?time_coverage_start__lte=2020-11-01 00:02:00Z&time_coverage_end__gte=2020-11-01 00:02:00Z
{
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 96374,
            "time_coverage_start": "2020-11-01T00:01:58Z",
            "time_coverage_end": "2020-11-01T00:04:58Z",
            ...
        },
        {
            "id": 96433,
            "time_coverage_start": "2020-11-01T00:00:00Z",
            "time_coverage_end": "2020-11-10T23:59:59Z",
            ...
        },
        ...
    ]
}
```

- Find all datasets whose time coverage intersects a given time range.<br />
  This is very close to the previous example, but take care to use the proper conditions.<br />
  Given a time range `(date1, date2)` with `date1` < `date2`, the condition must be the following:

  `time_coverage_start__lte=date2&time_coverage_end__gte=date1`

  For example:

```json
# GET <api_root>/datasets/?time_coverage_start__lte=2020-11-02 00:02:00Z&time_coverage_end__gte=2020-11-01 00:02:00Z
{
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 96300,
            "time_coverage_start": "2020-11-01T23:50:58Z",
            "time_coverage_end": "2020-11-04T13:22:39Z",
            ...
        },
        ...
        {
            "id": 96374,
            "time_coverage_start": "2020-11-01T00:01:58Z",
            "time_coverage_end": "2020-11-01T00:04:58Z",
            ...
        },
        ...
    ]
}
```

#### Filtering by location

To filter by location, we need to use the `geometry` field of the `geographic_location` property
attached to each dataset.
The provided search value should be a WKT representation of the searched zone
(reminder: it needs to be URL-encoded).

For example, if the WKT string is `POINT(17.55 78.78)`, the URL would be:

`<api_root_url>/datasets/?zone=POINT%2817.55+78.78%29`

Several lookups are available, including:
  - `intersects`
  - `contains`

The full list can be found in the [GeoDjango documentation](https://docs.djangoproject.com/en/3.1/ref/contrib/gis/geoquerysets/#spatial-lookups).

For example, the following request can be used to search for datasets whose spatial coverage
intersects with a rectangle covering Iceland:

```json
# GET <api_root_url>/datasets/?geographic_location__geometry__intersects=POLYGON((-26.7 67.5,-9.5 67.5,-9.5 62.1,-26.7 62.1,-26.7 67.5))
{
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 96390,
            "geographic_location": 43932,
            ...
        },
        {
            "id": 96403,
            "geographic_location": 43940,
            ...
        },
        ...
```

> *Crossing the international date line:*
>
> If you need to search using a polygon which crosses the international date line, you can use
> longitudes outside the [-180, 180] range.
>
> Here is an example for more clarity:  
> Let us imagine that we are looking for two datasets which spatial coverage is respectively
> `POLYGON((173 -17,174 -17,174 -20,173 -20,173 -17))` and
> `POLYGON((-173 -17,-174 -17,-174 -20,-173 -20,-173 -17))`.  
> `POLYGON((170 -18,190 -18,190 -19,170 -19,170 -18))` intersects both those datasets and can be
> used to search for them.  
> On the other hand, `POLYGON((170 -18,-170 -18,-170 -19,170 -19,170 -18))` does not intersect
> either of these datasets.

#### Filtering by source

Each dataset has an associated `source`, which has two main fields: `platform` and `instrument`.

These fields contain strings, so Django string lookups can be used. These include:
  - `contains`
  - `startswith`
  - `endswith`

> Reminder: the complete list of lookups can be found in the [Django documentation](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#field-lookups).

To match a string exactly, just use the name of the field as query parameter
(the `exact` lookup is the default). 

There are different approaches to searching for datasets by source.
For example:

- `https://<api_root_url>/datasets/?source__instrument__short_name=VIIRS` gets all VIIRS datasets
- `https://<api_root_url>/datasets/?source__platform__short_name__contains=NPP&source__instrument__short_name=VIIRS` gets all VIIRS datasets from the NPP platform
- `https://<api_root_url>/datasets/?source__platform__short_name=N20&source__instrument__short_name=VIIRS` gets all VIIRS datasets from the N20 platform

#### Filtering by a related object

Until now, the examples shown all use field values to filter, but there is another possibility.
Let us assume we are looking for all datasets coming from a particular source. We can do that as
shown in the [previous example](#filtering-by-source), but we can also look for the id
of the source object and then use that to look for datasets. Here are the required queries:

First, look for the interesting source:

```json
# GET <api_root>/sources/?platform__short_name__contains=NPP&instrument__short_name=VIIRS
{
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 6,
            "specs": "",
            "platform": 284,
            "instrument": 765
        }
    ]
}
```

Then, look for all dataset which have the source with id `6`.

```json
# GET <api_root>/datasets/?source=6
{
    "next": "<api_root>/datasets/?cursor=cD05NjU5Mg%3D%3D&source=6",
    "previous": null,
    "results": [
        {
            "id": 96493,
            "source": 6,
            ...
        },
        {
            "id": 96494,
            "source": 6,
            ...
        },
        ...
    ]
}
```

## Triggering jobs

### Implementation

Long running jobs are implemented in
[geospaas_processing](https://github.com/nansencenter/django-geo-spaas-processing).
It is based on the
[Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) framework.

In `geospaas_processing`, Celery **tasks** are defined for diverse operations:
downloading, converting, archiving, etc...

Each job can be composed of one or more of these tasks. It provides a convenient way to check the
status of this task or series of tasks.

The API exposes these capabilities through the `/jobs/` endpoint.

### Usage

The `/jobs/` endpoint enables the user to trigger jobs and check their status.

A job is triggered by sending a POST request to the `/jobs/` endpoint, with data having the
following structure:

```json
{
    "action": "<action>",
    "parameters": {"<parameter1>": "<value1>", "<parameter2>": "<value2>"}
}
```

The parameters that need to be provided depend on the type of job.
The available actions and the associated parameters are described below.

The response will contain the following information about the job:
  - `id`: the ID of the job
  - `task_id`: the ID of the first task in the job
  - `date_created`: the date and time at which the job was created
  - `status`: the status of the job

Here is an example of the data contained in such a response:

```json
{
    "id": 4,
    "task_id": "b579fade-6cb5-4fba-9157-b8633a0910bc",
    "date_created":"2020-09-18T10:14:44.635370Z",
    "status":"STARTED"
}
```

The status of the job (and each of its tasks) can be:
  - `STARTED`: the job is currently executing
  - `SUCCESS`: the job finished successfully
  - `RETRY`: the job (or part of it) will be retried later, for example if is waiting for a lock
  - `FAILED`: the job failed

Further information about a job can be accessed by sending a GET request to:
`https://<api_root_url>/jobs/<job_id>/`.
This link can be polled as needed to get updates on the status of the job.

Continuing the previous example, a request to `https://<api_root_url>/jobs/4/` would yield
the following data:

```json
{
    "id": 4,
    "task_id": "b579fade-6cb5-4fba-9157-b8633a0910bc",
    "date_created": "2020-09-18T10:14:44.635370Z",
    "status": "SUCCESS",
    "date_done": "2020-09-18T10:14:47.139263Z",
    "result": "<task_result>"
}
```

Where `<task_result>` is the result of the last task in the job.

The `/tasks/` endpoint gives read-only access to the individual tasks for diagnostics purposes.

#### Available actions

The following actions are available on the `/jobs/` endpoint.

##### `download`

Downloads a dataset to the API server.

Payload:

```json
{
    "action": "download",
    "parameters": {"dataset_id": <dataset_id>, "bounding_box": <bounding_box>}
}
```

Where :
- `<dataset_id>` (integer) is the ID of the dataset to download.
  It can be obtained using the search capabilities of the `/datasets/` endpoint.
- `<bounding_box>` (4-elements list of floats):containing the limits used to crop the dataset file
  after it has been downloaded.
  The limits are given in the following order: west, north, east, south.

Once the job is over, its **"result"** is set with a two-elements list.
  - the first element is the ID of the dataset that was downloaded
    (this enables to easily chain tasks together)
  - the second element is the link where the dataset can be retrieved.

##### `convert`

Converts a dataset file to a given format.

Payload:

```json
{
    "action": "convert",
    "parameters": {
      "format": "<format>",
      "dataset_id": <dataset_id>,
      "bounding_box": <bounding_box>
    }
}
```

Where:
  - `<format>` (string) is the target format.
  - `<dataset_id>` (integer) is the ID of the dataset to download.
  - `<bounding_box>` (4-elements list of floats):containing the limits used to crop the dataset file
  after it has been downloaded.
  The limits are given in the following order: west, north, east, south.

Available formats:
  - "idf"
  - "syntool"

Once the job is over, its **"result"** is set with a two-elements list.
  - the first element is the ID of the dataset that was converted
    (this enables to easily chain tasks together)
  - the second element is the link where the converted file can be retrieved.

##### `syntool_cleanup`

Removes ingested files older than a given date.

Payload:

```json
{
    "action": "syntool_cleanup",
    "parameters": {
      "date": "<date>",
      "created": <created>
    }
}
```

Where:
- `<date>` (string): the limit date. The format should be readable by
  [datetutil](https://dateutil.readthedocs.io/en/stable/).
- `created` (boolean, default `false`): if `true`, files ingested before the date are removed.
  If `false`, files whose dataset's time coverage ends before the date are removed.

##### `harvest`

Trigger metadata harvesting using
[geospaas_harvesting](https://github.com/nansencenter/django-geo-spaas-harvesting).

Payload:

```json
{
    "action": "harvest",
    "parameters": {
      "search_config_dict": <search_config_dict>
    }
}
```

Where `<search_config_dict>` is a search configuration dictionary for `geospaas_harvesting`.
The format is explained
[here](https://github.com/nansencenter/django-geo-spaas-harvesting#search-configuration).
