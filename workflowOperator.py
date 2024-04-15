from pathlib import Path
import time
import requests
from .breast_workflow_data.data import WORKFLOW_RESULT, WORKFLOW_DESCRIPTION, PATIENT_INFOS

"""
Workflow 1: 
    - name: breast-workflow
    - identifier: sparc-workflow-yyds-001
    - target: calculate closest distance
Practitioner 1:
    - name: John Thompson
    - identifier: sparc-practitioner-yyds-001
Breast-dataset 1:
    - Patient 1:
        - name: Aniyah
        - identifier: sparc-patient-yyds-001
        - Observation 1:
            - age: 30
            - identifier: sparc-patient-yyds-001-observation-001
            - ref: Patient 1
        - Observation 2:
            - body temperature: 96.8 degF
            - identifier: sparc-patient-yyds-001-observation-002
            - ref: Patient 1
    - Patient 2:
        - name: Linman Zhang
        - identifier: sparc-patient-yyds-002
        - Observation 1:
            - age: 31
            - identifier: sparc-patient-yyds-002-observation-001
            - ref: Patient 2
        - Observation 2:
            - body temperature: 93.8 degF
            - identifier: sparc-patient-yyds-002-observation-002
            - ref: Patient 2
Workflow process (Task):
    - workflow process identifier: sparc-workflow-yyds-001-process-001
    - workflow identifier: sparc-workflow-yyds-001 (focus)
    - practitioner identifier: sparc-practitioner-yyds-001 (owner)
    - patient identifier: sparc-patient-yyds-001 (requester)
    - Observation:
        - Distance
            - identifier: sparc-workflow-yyds-001-process-001-result-001
        - Size
            - identifier: sparc-workflow-yyds-001-process-001-result-001
    
"""


async def operationWorkflow(client):
    # TODO 1: create workflow
    # await init(client)
    # TODO 2: Load measurements dataset
    # await ingress_measurements_dataset(client, "./sparc_fhir_breast_dataset/primary")
    # TODO 3: Execute workflow
    await execute_workflow(
        client,
        workflow_id="sparc-workflow-yyds-001",
        workflow_process_id="sparc-workflow-yyds-001-process-001",
        practitioner_id="sparc-practitioner-yyds-001",
        patient_id="sparc-patient-yyds-001",
        result_info=WORKFLOW_RESULT)

    # search workflows
    # workflows = await search_resource(client, identifier="sparc-workflow-yyds-001", resource="PlanDefinition")
    # print(workflows)
    # print(workflows[0]['action'])

    # print(await search_resource(client, identifier="sparc-patient-yyds-001", resource="Patient"))
    # p = await search_resources(client, "Patient")
    # print(p)
    # o = await search_resources(client, 'Observation')
    # print(o[0]['identifier'])
    # print(p[0].to_reference())

    # delete workflows
    # await delete_resources(client, identifier="sparc-workflow-yyds-001")
    # await delete_resources(client, identifier="sparc-practitioner-yyds-001")
    # await delete_resource(client, identifier="sparc-patient-yyds-002-observation-002", resource='Observation')
    # await delete_resources(client, "Observation")
    # await delete_resources(client, "Patient")
    pass


async def init(client):
    await create_workflow(client, identifier="sparc-workflow-yyds-001", description=WORKFLOW_DESCRIPTION, version="1.0.0")

    await createPractitioner(client, identifier="sparc-practitioner-yyds-001")


async def ingress_measurements_dataset(client, root):
    """
        Assume the measurements data for these patients are body temperature and age
        Aniyah:
            - temperature: 96.8 degF
            - age: 30
        Linman Zhang:
            - temperature: 93.8 degF
            - age: 31
        category.coding.system: http://hl7.org/fhir/observation-category
        temperature code system:
            - http://loinc.org
            - 8310-5
        age code: 30525-0
        Unit system: http://unitsofmeasure.org
    """
    dataset_root = Path(root)
    # patient_identifiers = [entry.name for entry in dataset_root.iterdir() if entry.is_dir()]
    # Create Patients
    # Store Patient's measurement data to Observation

    for patient_info in PATIENT_INFOS:
        await create_patient(client, patient_info)
        for ob_info in patient_info['Observation']:
            await create_patient_observation(client, patient_info['identifier'], ob_info)


async def execute_workflow(client, workflow_id, workflow_process_id, practitioner_id, patient_id, result_info):
    workflows = await search_resource(client, identifier=workflow_id, resource='PlanDefinition')
    practitioners = await search_resource(client, identifier=practitioner_id, resource='Practitioner')
    patients = await search_resource(client, identifier=patient_id, resource='Patient')
    workflow = workflows[0]
    practitioner = practitioners[0]
    patient = patients[0]

    result = await is_resource_exist(client, workflow_process_id, "Task")
    if result:
        return

    new_task = client.resource('Task')

    new_task['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": workflow_process_id
        }
    ]

    new_task['focus'] = workflow.to_reference()
    new_task['owner'] = practitioner.to_reference()
    new_task['requester'] = patient.to_reference()
    new_task['lastModified'] = '2024-04-12T00:00:00Z'

    outputs = []

    for result in result_info:
        check = await is_resource_exist(client, result['identifier'], "Observation")
        if check:
            return

        new_observation = client.resource('Observation')

        new_observation['identifier'] = [
            {
                "use": "official",
                "system": "http://sparc.sds.dataset",
                "value": result['identifier']
            },
            {
                "use": "official",
                "system": "http://sparc.sds.dataset",
                "value": workflow_process_id
            }
        ]
        new_observation['code'] = {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": result['loinc-code'],
                }
            ]
        },
        new_observation['method'] = {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": result['method-code'],
                    "display": "Gross examination and sampling of tissue specimen (procedure)"
                }
            ]
        }
        new_observation['effectiveDateTime'] = "2024-04-12T00:00:00Z"
        new_observation['subject'] = patient.to_reference()
        new_observation['component'] = []
        for component in result['component']:
            temp_output = {
                "type": {
                    "coding": [
                        {
                            "system": "http://ABI-breast-workflow",
                            "code": component['loinc-code'],
                            "display": component['display']
                        },
                    ]},
                "value": {
                    "value": component['value'],
                    "system": "http://unitsofmeasure.org",
                    "code": component['unit-code']
                }
            }
            outputs.append(temp_output)
            component_temp = {
                "code": {
                    "coding": [
                        {
                            "system": "http://ABI-breast-workflow",
                            "code": component['loinc-code'],
                            "display": component['display']
                        },
                    ]
                },
                "valueQuantity": {
                    "value": component['value'],
                    "system": "http://unitsofmeasure.org",
                    "code": component['unit-code']
                }
            }
            new_observation['component'].append(component_temp)

            await new_observation.save()

    new_task['output'] = outputs

    await new_task.save()


async def createPractitioner(client, identifier):
    result = await is_resource_exist(client, identifier, "Practitioner")
    if result:
        return
    new_practitioner = client.resource('Practitioner')
    new_practitioner['name'] = [
        {
            'given': ['John'],
            'family': 'Thompson',
            'use': 'official',
            'prefix': ['Mr. '],
        }
    ]

    # format year-month-day
    new_practitioner['brithDate'] = '1975-09-20'
    new_practitioner['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": identifier
        }
    ]
    await new_practitioner.save()


async def create_patient(client, info):
    result = await is_resource_exist(client, info['identifier'], "Patient")
    if result:
        return

    new_patient = client.resource('Patient')

    new_patient['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": info['identifier']
        }
    ]

    new_patient['name'] = [
        {
            'given': [info['givenname']],
            'family': info['familyname'],
            'use': 'official',
        }
    ]

    # format year-month-day
    new_patient['brithDate'] = info['brithDate']
    print(new_patient)
    await new_patient.save()


async def create_patient_observation(client, patient_identifier, info):
    result = await is_resource_exist(client, info['identifier'], "Observation")
    if result:
        return

    patients = await search_resource(client, patient_identifier, 'Patient')
    patient = patients[0]

    new_observation = client.resource(
        'Observation',
        identifier=[
            {
                "use": "official",
                "system": "http://sparc.sds.dataset",
                "value": info['identifier']
            }
        ],
        status='final',
        category=[{
            'coding': [{
                'system': 'http://hl7.org/fhir/observation-category'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': info['loinc-code']
            }]
        }
    )
    new_observation['valueQuantity'] = {
        'system': 'http://unitsofmeasure.org',
        'value': info['value'],
        'code': info['unit-code']
    }

    # "subject": {
    #                     "reference": "Patient/102"
    #                 }

    new_observation['subject'] = patient.to_reference()
    await new_observation.save()


async def create_workflow(client, identifier, description, version="1.0.0"):
    result = await is_resource_exist(client, identifier, "PlanDefinition")
    if result:
        return

    workflow = client.resource('PlanDefinition')
    workflow['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": identifier
        }
    ]
    workflow["title"] = description['title']
    workflow["type"] = description['type']
    workflow["date"] = description['date']
    workflow["description"] = description['description']
    workflow["purpose"] = description['purpose']
    workflow["author"] = description['author']
    workflow["action"] = description['action']
    workflow['version'] = version

    await workflow.save()


async def is_resource_exist(client, identifier, resource):
    workflows = await search_resource(client, identifier=identifier, resource=resource)
    if len(workflows) > 0:
        print(f"the {resource} already exist! identifier: {identifier}")
        return True
    return False


async def search_resource(client, identifier, resource):
    resources_search_set = client.resources(resource)
    # workflows = await workflowResources.search(identifier=identifier, version="1.0.0").fetch_all()
    resources = await resources_search_set.search(identifier=identifier).fetch_all()
    return resources


async def search_resources(client, resource):
    resources_search_set = client.resources(resource)
    # workflows = await workflowResources.search(identifier=identifier, version="1.0.0").fetch_all()
    resources = await resources_search_set.search().fetch_all()
    return resources


async def delete_resource(client, identifier, resource):
    resources = await search_resource(client, identifier, resource)
    for resource in resources:
        await resource.delete()


async def delete_resources(client, resource):
    resources = await search_resources(client, resource)
    for resource in resources:
        await resource.delete()


def test():
    data = {
        "resourceType": "Patient",
        "id": "pat3",
        "identifier": [
            {
                "use": "official",
                "system": "http://sparc.sds.dataset",
                "value": "sparc-patient-yyds-002"
            }
        ],
        "active": 'true',
        "name": [
            {
                "use": "official",
                "family": "Linman",
                "given": [
                    "Zhang"
                ]
            }
        ],
        "gender": "male",
        "birthDate": "1982-01-23",
        "deceasedDateTime": "2015-02-14T13:42:00+10:00"
    }

    headers = {
        'Content-Type': 'application/json',  # 指定请求内容类型为 JSON
        'Authorization': 'Bearer YOUR_TOKEN',  # 添加授权头信息
        'Accept': '*/*'
    }

    # response = requests.post("http://localhost:8080/fhir/Patient", json=data)
    # print(response.status_code)

    response1 = requests.get("http://localhost:8080/fhir/Patient", headers=headers)
    if response1.status_code == 200:
        print('请求成功！')
        print('响应内容：', response1.text)
    else:
        print('请求失败，状态码：', response1.status_code)

    #
    # # 检查响应状态码
    # if response.status_code == 200:
    #     print('请求成功！')
    #     print('响应内容：', response.text)
    # else:
    #     print('请求失败，状态码：', response.status_code)
    #     print(response.text)
