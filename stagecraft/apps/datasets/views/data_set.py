import json

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)

from stagecraft.apps.datasets.models import DataSet


def detail(request, name):
    try:
        data_set = DataSet.objects.get(name=name)
    except DataSet.DoesNotExist:
        error = {'status': 'error',
                 'message': "No Data Set named '{}' exists".format(name)}
        return HttpResponseNotFound(json.dumps(error))

    json_str = json.dumps(data_set.serialize())

    return HttpResponse(json_str, content_type='application/json')


def list(request, data_group=None, data_type=None):
    def get_filter_kwargs(key_map, query_params):
        """Return Django filter kwargs from query parameters"""
        return {key_map[k]: v for k, v in query_params if k in key_map}

    # map filter parameter names to query string keys
    key_map = {
        'data-group': 'data_group__name',
        'data_group': 'data_group__name',
        'data-type': 'data_type__name',
        'data_type': 'data_type__name',
    }

    # 400 if any query string keys were not in allowed set
    if not set(request.GET).issubset(key_map):
        unrecognised = set(request.GET).difference(key_map)
        unrecognised_text = ', '.join("'{}'".format(i) for i in unrecognised)
        error = {'status': 'error',
                 'message': 'Unrecognised parameter(s) ({}) were provided'
                            .format(str(unrecognised_text))}
        return HttpResponseBadRequest(json.dumps(error))

    filter_kwargs = get_filter_kwargs(key_map, request.GET.items())
    data_sets = DataSet.objects.filter(**filter_kwargs)
    json_str = json.dumps([ds.serialize() for ds in data_sets])

    return HttpResponse(json_str, content_type='application/json')
