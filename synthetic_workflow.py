from initialize import import_dataset
from fhirpy import SyncFHIRClient, AsyncFHIRClient
import aiohttp
import json
import requests
from utils import calculate_age
from knowlegebase import switch_case_group_code

# TODO Config Sync Client
sync_client = SyncFHIRClient(
    'http://localhost:8080/fhir/',
    requests_config={
        "verify": False,
        "allow_redirects": True,
        "timeout": 60,
    }
)

async_client = AsyncFHIRClient(
    url='http://localhost:8080/fhir/',
    authorization='Bearer TOKEN',
)


async def operationSyntheticWorkflow():
    # TODO 1 Load Synthetic data
    # await load_synthetic_data()

    # TODO 2 Load researcher info
    # await create_practitioner("sparc-practitioner-yyds-001")

    # TODO 3 Group Patients
    # await group_patients(practitioner_id="sparc-practitioner-yyds-001")

    # TODO search Synthetic data
    await search_synthetic_patient()

    pass


def create_resource(resource_type, resource_identifier):
    resource = sync_client.resource(resource_type)

    resource['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": resource_identifier
        }
    ]

    return resource


def async_create_resource(resource_type, resource_identifier):
    resource = async_client.resource(resource_type)

    resource['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": resource_identifier
        }
    ]

    return resource


async def create_practitioner(identifier):
    """
    Researcher: Edward Ferdian
    Identifier: sparc-practitioner-yyds-001
    :param sync_client:
    :param identifier:
    :return:
    """

    result = await async_is_resource_exist(identifier, 'Practitioner')

    if result:
        return

    new_practitioner = create_resource('Practitioner', identifier)
    new_practitioner['name'] = [
        {
            'given': ['Edward'],
            'family': 'Ferdian',
            'use': 'official',
        }
    ]

    new_practitioner.save()
    p2 = sync_search_single_resource(identifier, 'Practitioner')
    print("p2", p2)


async def load_synthetic_data():
    # TODO: download the FHIR R4 dataset from synthea website to the dataset folder.
    dataset_path_config = './dataset_3/config'
    dataset_path_patients = './dataset_3/patients'
    await import_dataset(async_client, dataset_path_config)
    await import_dataset(async_client, dataset_path_patients)


async def _create_group(practitioner, details):
    for key, value in details.items():
        group = async_create_resource('Group', value['id'])
        # must use practitioner.to_reference() for managingEntity
        group['managingEntity'] = practitioner.to_reference()
        group['type'] = 'person'
        group['actual'] = True
        group['name'] = f'Group: {key}'
        group['code'] = switch_case_group_code(key)['code']
        group['characteristic'] = switch_case_group_code(key)['characteristic']
        group['member'] = []
        for p in value['data']:
            group['member'].append({
                "entity": {
                    # must use p.to_reference().reference for member
                    "reference": p.to_reference().reference
                },
            })

        await group.save()


async def group_patients(practitioner_id):
    count = await async_client.resources('Patient').search().count()

    group_details = {
        "male": {
            'id': 'sparc-group-yyds-male-001',
            'data': []
        },
        "female": {
            'id': 'sparc-group-yyds-female-001',
            'data': []
        },
        "age_[20-30]": {
            'id': 'sparc-group-yyds-age[20-30]-001',
            'data': []
        },
        "age_[30-40]": {
            'id': 'sparc-group-yyds-age[31-40]-001',
            'data': []
        }
    }

    synthetic_patients = await async_client.resources('Patient').search().limit(count).fetch()
    for p in synthetic_patients:
        if p['gender'] == 'male':
            group_details['male']['data'].append(p)
        if p['gender'] == 'female':
            group_details['female']['data'].append(p)
        if calculate_age(p['birthDate']) <= 30:
            group_details['age_[20-30]']['data'].append(p)
        if calculate_age(p['birthDate']) > 30:
            group_details['age_[30-40]']['data'].append(p)

    practitioner = sync_search_single_resource(practitioner_id, 'Practitioner')

    await _create_group(practitioner, details=group_details)


async def search_synthetic_patient():
    print()
    print(
        "*********************************** Search Synthetic Patients Results *******************************************")

    count = await async_client.resources('Patient').search().count()
    print(count)


    synthetic_patients = await async_client.resources('Patient').search().limit(count).fetch()
    for p in synthetic_patients:
        print(p['identifier'])
        print(p['gender'])
        print(calculate_age(p['birthDate']))

    patient_to_save = create_resource('Practitioner', "sparc-practitioner-yyds-001")
    patient_to_save['name'] = [
        {
            'given': ['Edward2'],
            'family': 'Ferdian',
            'use': 'official',
        }
    ]

    # practitioner1, created = sync_client.resources("Practitioner").search(identifier="sparc-practitioner-yyds-001").get_or_create(patient_to_save)
    #
    # print(practitioner1)
    # print(created)
    print(sync_client.resources("Practitioner").search(identifier="sparc-practitioner-yyds-001").fetch_all())
    practitioner = sync_search_single_resource("sparc-practitioner-yyds-001", 'Practitioner')


    group1 = await async_client.resources('Group').search(managing_entity=practitioner.to_reference()).fetch_all()
    group2 = await async_client.resources('Group').search(member=synthetic_patients[0].to_reference()).fetch_all()
    group3 = await async_client.resources('Group').search(code='46251-5').fetch_all()

    print(group1)
    print(group2)
    print(group3)


async def async_is_resource_exist(identifier, resource):
    count = await async_client.resources(resource).search(identifier=identifier).count()
    print(count)
    if count > 0:
        if count > 1:
            resources = await async_client.resources(resource).search(identifier=identifier).limit(count).fetch()
            for resource in resources[1:]:
                await resource.delete()
                res = await expunge_delete(resource['resourceType'], resource['id'])
                print(res)
        return True
    return False


async def expunge_delete(resource, id):
    url = f"http://localhost:8080/fhir/{resource}/{id}/$expunge"
    body = {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "limit",
                "valueInteger": 1000
            }, {
                "name": "expungeDeletedResources",
                "valueBoolean": True
            }, {
                "name": "expungePreviousVersions",
                "valueBoolean": True
            }
        ]
    }

    return await _fetch_url(url, body)


async def _fetch_url(url, body):
    async with aiohttp.ClientSession() as session:
        headers = {
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }
        async with session.post(url, headers=headers, data=json.dumps(body)) as response:
            return await response.text()


async def async_search_single_resource(identifier, resource):
    resources_search_set = async_client.resources(resource)
    searched_resource = await resources_search_set.search(identifier=identifier).first()
    return searched_resource


async def async_search_resource(identifier, resource):
    resources_search_set = async_client.resources(resource)
    resources = await resources_search_set.search(identifier=identifier).fetch_all()
    return resources


def sync_search_resource(identifier, resource):
    resources_search_set = sync_client.resources(resource)
    resources = resources_search_set.search(identifier=identifier).fetch_all()
    return resources


def sync_search_single_resource(identifier, resource):
    resources_search_set = sync_client.resources(resource)
    searched_resource = resources_search_set.search(identifier=identifier).first()
    return searched_resource
