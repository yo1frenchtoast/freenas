#!/usr/bin/env python3.6

# License: BSD

import sys
import os
import pytest
apifolder = os.getcwd()
sys.path.append(apifolder)
from functions import DELETE, GET, POST, PUT
from auto_config import pool_name

dataset = f'{pool_name}/dataset1'
dataset_url = dataset.replace('/', '%2F')
zvol = f'{pool_name}/zvol1'
zvol_url = zvol.replace('/', '%2F')

default_acl = [
    {
        "tag": "owner@",
        "id": None,
        "type": "ALLOW",
        "perms": {"BASIC": "FULL_CONTROL"},
        "flags": {"BASIC": "INHERIT"}
    },
    {
        "tag": "group@",
        "id": None,
        "type": "ALLOW",
        "perms": {"BASIC": "FULL_CONTROL"},
        "flags": {"BASIC": "INHERIT"}
    }
]


def test_01_check_dataset_endpoint():
    assert isinstance(GET('/pool/dataset/').json(), list)


def test_02_create_dataset():
    result = POST(
        '/pool/dataset/', {
            'name': dataset
        }
    )
    assert result.status_code == 200, result.text


def test_03_query_dataset_by_name():
    dataset = GET(f'/pool/dataset/?id={dataset_url}')

    assert isinstance(dataset.json()[0], dict)


def test_04_update_dataset_description():
    result = PUT(
        f'/pool/dataset/id/{dataset_url}/', {
            'comments': 'testing dataset'
        }
    )

    assert result.status_code == 200, result.text


def test_05_set_permissions_for_dataset():
    result = POST(
        f'/pool/dataset/id/{dataset_url}/permission/', {
            'acl': [],
            'mode': '777',
            'group': 'nobody',
            'user': 'nobody'
        }
    )

    assert result.status_code == 200, result.text


def test_06_promoting_dataset():
    # TODO: ONCE WE HAVE MANUAL SNAPSHOT FUNCTIONAITY IN MIDDLEWARED,
    # THIS TEST CAN BE COMPLETED THEN
    pass

# Test 07 through 11 verify basic ACL functionality. A default ACL is
# set, verified, stat output checked for its presence. Then ACL is removed
# and stat output confirms its absence.


def test_07_set_acl_for_dataset():
    result = POST(
        f'/pool/dataset/id/{dataset_url}/permission/', {
            'acl': default_acl,
            'group': 'nobody',
            'user': 'nobody'
        }
    )

    assert result.status_code == 200, result.text


def test_08_get_filesystem_getacl():
    global results
    payload = {
        'path': f'/mnt/{dataset}',
        'simplified': True
    }
    results = POST('/filesystem/getacl/', payload)
    assert results.status_code == 200, results.text


@pytest.mark.parametrize('key', ['tag', 'type', 'perms', 'flags'])
def test_09_verify_filesystem_getacl(key):
    assert results.json()['acl'][0][key] == default_acl[0][key], results.text
    assert results.json()['acl'][1][key] == default_acl[1][key], results.text


def test_10_filesystem_acl_is_present():
    results = POST('/filesystem/stat/', f'/mnt/{dataset}')
    assert results.status_code == 200, results.text
    assert results.json()['acl'] is True, results.text


def test_11_strip_acl_from_dataset():
    result = POST(
        f'/pool/dataset/id/{dataset_url}/permission/', {
            'acl': [],
            'mode': '777',
            'group': 'nobody',
            'user': 'nobody',
            'options': {'stripacl': True}
        }
    )

    assert result.status_code == 200, result.text


def test_12_filesystem_acl_is_removed():
    results = POST('/filesystem/stat/', f'/mnt/{dataset}')
    assert results.status_code == 200, results.text
    assert results.json()['acl'] is False, results.text
    assert oct(results.json()['mode']) == '0o40777', results.text


def test_13_delete_dataset():
    result = DELETE(
        f'/pool/dataset/id/{dataset_url}/'
    )
    assert result.status_code == 200, result.text


def test_14_verify_the_id_dataset_does_not_exist():
    result = GET(f'/pool/dataset/id/{dataset_url}/')
    assert result.status_code == 404, result.text


def test_15_creating_zvol():
    global results, payload
    payload = {
        'name': zvol,
        'type': 'VOLUME',
        'volsize': 163840,
        'volblocksize': '16K'
    }
    results = POST(f"/pool/dataset/", payload)
    assert results.status_code == 200, results.text


@pytest.mark.parametrize('key', ['name', 'type', 'volsize', 'volblocksize'])
def test_16_verify_output(key):
    if key == 'volsize':
        assert results.json()[key]['parsed'] == payload[key], results.text
    elif key == 'volblocksize':
        assert results.json()[key]['value'] == payload[key], results.text
    else:
        assert results.json()[key] == payload[key], results.text


def test_17_query_zvol_by_id():
    global results
    results = GET(f'/pool/dataset/id/{zvol_url}')
    assert isinstance(results.json(), dict)


@pytest.mark.parametrize('key', ['name', 'type', 'volsize', 'volblocksize'])
def test_18_verify_the_query_zvol_output(key):
    if key == 'volsize':
        assert results.json()[key]['parsed'] == payload[key], results.text
    elif key == 'volblocksize':
        assert results.json()[key]['value'] == payload[key], results.text
    else:
        assert results.json()[key] == payload[key], results.text


def test_19_update_zvol():
    global payload, results
    payload = {
        'volsize': 163840,
        'comments': 'testing zvol'
    }
    result = PUT(f'/pool/dataset/id/{zvol_url}/', payload)
    assert result.status_code == 200, result.text


@pytest.mark.parametrize('key', ['volsize'])
def test_20_verify_update_zvol_output(key):
    assert results.json()[key]['parsed'] == payload[key], results.text


def test_21_query_zvol_changes_by_id():
    global results
    results = GET(f'/pool/dataset/id/{zvol_url}')
    assert isinstance(results.json(), dict)


@pytest.mark.parametrize('key', ['comments', 'volsize'])
def test_22_verify_the_query_change_zvol_output(key):
    assert results.json()[key]['parsed'] == payload[key], results.text


def test_23_delete_zvol():
    result = DELETE(f'/pool/dataset/id/{zvol_url}/')
    assert result.status_code == 200, result.text


def test_24_verify_the_id_zvol_does_not_exist():
    result = GET(f'/pool/dataset/id/{zvol_url}/')
    assert result.status_code == 404, result.text
