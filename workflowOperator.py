from pathlib import Path
import time
import requests
from breast_workflow_data.data import WORKFLOW_RESULT, WORKFLOW_DESCRIPTION, PATIENT_INFOS, WORKFLOW_RESULT_LINMAN

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
    - composition identifier: sparc-workflow-yyds-001-process-001-composition-001
    - Observation:
        - Distance
            - identifier: sparc-workflow-yyds-001-process-001-result-001
        - Size
            - identifier: sparc-workflow-yyds-001-process-001-result-001

Workflow process (Task) - Linman:
    - workflow process identifier: sparc-workflow-yyds-001-process-002
    - workflow identifier: sparc-workflow-yyds-001 (focus)
    - practitioner identifier: sparc-practitioner-yyds-001 (owner)
    - patient identifier: sparc-patient-yyds-002 (requester)
    - composition identifier: sparc-workflow-yyds-001-process-002-composition-001
    - Observation:
        - Distance
            - identifier: sparc-workflow-yyds-001-process-002-result-001
        - Size
            - identifier: sparc-workflow-yyds-001-process-002-result-001
    
"""


async def operationWorkflow(client):
    # TODO 1: create workflow
    await init(client)
    # TODO 2: Load measurements dataset
    await import_measurements_dataset(client, "./sparc_fhir_breast_dataset/primary")
    # # TODO 3: Execute workflow process for Patient Aniyah
    await execute_workflow(
        client,
        workflow_id="sparc-workflow-yyds-001",
        workflow_process_id="sparc-workflow-yyds-001-process-001",
        practitioner_id="sparc-practitioner-yyds-001",
        patient_id="sparc-patient-yyds-001",
    )


    # await delete_resources(client, "Composition")
    # await delete_resources(client, "Observation")

    await create_result_observations(client,
                                     workflow_process_id="sparc-workflow-yyds-001-process-001",
                                     result_info=WORKFLOW_RESULT)

    await create_composition(client,
                             composition_identifier="sparc-workflow-yyds-001-process-001-composition-001",
                             workflow_process_id="sparc-workflow-yyds-001-process-001",
                             patient_id="sparc-patient-yyds-001",
                             result_info=WORKFLOW_RESULT
                             )

    # TODO 3.1: Execute workflow process for Patient Linman
    await execute_workflow(
        client,
        workflow_id="sparc-workflow-yyds-001",
        workflow_process_id="sparc-workflow-yyds-001-process-002",
        practitioner_id="sparc-practitioner-yyds-001",
        patient_id="sparc-patient-yyds-002",
    )

    await create_result_observations(client,
                                     workflow_process_id="sparc-workflow-yyds-001-process-002",
                                     result_info=WORKFLOW_RESULT_LINMAN)

    await create_composition(client,
                             composition_identifier="sparc-workflow-yyds-001-process-002-composition-001",
                             workflow_process_id="sparc-workflow-yyds-001-process-002",
                             patient_id="sparc-patient-yyds-002",
                             result_info=WORKFLOW_RESULT_LINMAN
                             )
    print()
    print("*************************************** Search Results ************************************************")

    # TODO 4.1 Find all workflow process of the workflow: sparc-workflow-yyds-001
    workflow = await search_single_resource(client, identifier="sparc-workflow-yyds-001", resource="PlanDefinition")
    tasks = await client.resources('Task').search(focus=workflow.to_reference()).fetch_all()
    print("TODO 4.1: Search all workflow process of the workflow: sparc-workflow-yyds-001")
    print(tasks)
    print()
    print("***************************************************************************************")

    # TODO 4.2  find composition of the workflow process: sparc-workflow-yyds-001-process-002
    workflow_process = await search_single_resource(client, identifier="sparc-workflow-yyds-001-process-002",
                                                    resource="Task")
    compositions = await client.resources('Composition').search(subject=workflow_process.to_reference()).fetch_all()
    print(f"TODO 4.2: All compositions of workflow process {workflow_process.to_reference()}")
    print(compositions)
    print()
    print("***************************************************************************************")

    # TODO 4.3  Find Researcher:sparc-practitioner-yyds-001 all workflow process of workflow: sparc-workflow-yyds-001
    workflow = await search_single_resource(client, identifier="sparc-workflow-yyds-001", resource="PlanDefinition")
    researcher = await search_single_resource(client, identifier="sparc-practitioner-yyds-001", resource='Practitioner')
    workflow_processes = await client.resources('Task').search(focus=workflow.to_reference(),
                                                               owner=researcher.to_reference()).fetch_all()
    print(
        f"TODO 4.3: All workflow process of researcher sparc-practitioner-yyds-001 related to workflow: sparc-workflow-yyds-001")
    print(workflow_processes)
    print()
    print("***************************************************************************************")

    # TODO 4.4 Get the patient: sparc-patient-yyds-002 all workflow process of Researcher:sparc-practitioner-yyds-001 and workflow: sparc-workflow-yyds-001
    workflow = await search_single_resource(client, identifier="sparc-workflow-yyds-001", resource="PlanDefinition")
    researcher = await search_single_resource(client, identifier="sparc-practitioner-yyds-001", resource='Practitioner')
    patient = await search_single_resource(client, identifier="sparc-patient-yyds-002", resource="Patient")
    workflow_processes = await client.resources('Task').search(focus=workflow.to_reference(),
                                                               owner=researcher.to_reference(),
                                                               requester=patient.to_reference()).fetch_all()
    print(
        f"TODO 4.4: Get the patient: sparc-patient-yyds-002 all workflow process of Researcher:sparc-practitioner-yyds-001 and workflow: sparc-workflow-yyds-001")
    print(workflow_processes)
    print()
    print("***************************************************************************************")

    # TODO 4.5 Get Patient Linman: sparc-patient-yyds-002 all result observation
    linman = await search_single_resource(client, identifier="sparc-patient-yyds-002", resource="Patient")
    workflow_processes = await client.resources('Task').search(requester=linman.to_reference()).fetch_all()
    for process in workflow_processes:
        composition = await client.resources("Composition").search(subject=process.to_reference()).first()
        for section in composition['section']:
            for ob in section['entry']:
                print("TODO 4.5: the observation result of linman:")
                b = await ob.to_resource()
                print(b['identifier'])

    print()
    print("***************************************************************************************")

    # await clear_all_resources(client)
    # await delete_practitioner(client, "sparc-practitioner-yyds-001")
    # await delete_workflow_process(client, "sparc-workflow-yyds-001-process-001")

    # cs = await search_resource(client, "sparc-workflow-yyds-001-process-002-composition-001", "Composition")
    #
    # c = cs[0]
    #
    # a = c['section'][0]['entry'][0]
    # ob = await a.to_resource()
    # print(ob['identifier'])

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
    # await delete_resources(client, "Task")
    # await delete_resources(client, "Composition")
    pass


async def init(client):
    await create_workflow(client, identifier="sparc-workflow-yyds-001", description=WORKFLOW_DESCRIPTION,
                          version="1.0.0")
    await create_practitioner(client, identifier="sparc-practitioner-yyds-001")


async def import_measurements_dataset(client, root):
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


async def execute_workflow(client, workflow_id, workflow_process_id, practitioner_id, patient_id):
    workflows = await search_resource(client, identifier=workflow_id, resource='PlanDefinition')
    practitioners = await search_resource(client, identifier=practitioner_id, resource='Practitioner')
    patients = await search_resource(client, identifier=patient_id, resource='Patient')
    workflow = workflows[0]
    practitioner = practitioners[0]
    patient = patients[0]

    result = await is_resource_exist(client, workflow_process_id, "Task")
    if result:
        return

    new_task = create_resource(client, 'Task', workflow_process_id)

    new_task['focus'] = workflow.to_reference()
    new_task['owner'] = practitioner.to_reference()
    new_task['requester'] = patient.to_reference()
    new_task['lastModified'] = '2024-04-12T00:00:00Z'

    await new_task.save()


async def create_result_observations(client, workflow_process_id, result_info):
    workflow_processes = await search_resource(client, identifier=workflow_process_id, resource='Task')
    workflow_process = workflow_processes[0]

    outputs = []
    for result in result_info:
        check = await is_resource_exist(client, result['identifier'], "Observation")
        if check:
            return
        new_observation = create_resource(client, 'Observation', result['identifier'])
        # new_observation['identifier'].append({
        #         "use": "official",
        #         "system": "http://sparc.sds.dataset",
        #         "value": workflow_process_id
        #     })
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
        # new_observation['subject'] = patient.to_reference()
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

    workflow_process['output'] = outputs
    await workflow_process.save()


async def create_composition(client, composition_identifier, workflow_process_id, patient_id, result_info):
    check = await is_resource_exist(client, composition_identifier, "Composition")
    if check:
        return

    workflow_processes = await search_resource(client, identifier=workflow_process_id, resource='Task')
    patients = await search_resource(client, identifier=patient_id, resource='Patient')

    workflow_process = workflow_processes[0]
    patient = patients[0]

    composition = create_resource(client, "Composition", composition_identifier)

    composition['type'] = {
        "coding": [
            {
                "system": "http://ABI-breast-workflow-result",
                "code": "11488-4",
                "display": "Consult note"
            }
        ]
    }

    composition['category'] = [
        {
            "coding": [
                {
                    "system": "http://ABI-breast-workflow-result",
                    "code": "CODE-xxxx",
                    "display": "Report"
                }
            ]
        }
    ],

    composition['subject'] = {
        "reference": workflow_process.to_reference().reference,
        "display": f"Task: {workflow_process_id}"
    },

    composition['author'] = [
        {
            "reference": patient.to_reference(),
            "display": "Patient"
        }
    ]

    composition['title'] = f"Task: {workflow_process_id} results"

    composition['date'] = "2024-04-15T09:10:14Z"

    composition['section'] = []

    for result in result_info:
        result_observations = await search_resource(client, result['identifier'], 'Observation')
        result_observation = result_observations[0]

        section = {
            "title": result['title'],
            "entry": [{
                "reference": result_observation.to_reference().reference
            }]
        }
        composition['section'].append(section)

    await composition.save()


def create_resource(client, resource_type, resource_identifier):
    resource = client.resource(resource_type)

    resource['identifier'] = [
        {
            "use": "official",
            "system": "http://sparc.sds.dataset",
            "value": resource_identifier
        }
    ]

    return resource


async def create_practitioner(client, identifier):
    result = await is_resource_exist(client, identifier, "Practitioner")
    if result:
        return

    new_practitioner = create_resource(client, 'Practitioner', identifier)
    new_practitioner['name'] = [
        {
            'given': ['John'],
            'family': 'Thompson',
            'use': 'official',
        }
    ]

    # format year-month-day
    new_practitioner['brithDate'] = '1975-09-20'

    await new_practitioner.save()


async def create_patient(client, info):
    result = await is_resource_exist(client, info['identifier'], "Patient")
    if result:
        return

    new_patient = create_resource(client, 'Patient', info['identifier'])

    new_patient['name'] = [
        {
            'given': [info['givenname']],
            'family': info['familyname'],
            'use': 'official',
        }
    ]

    # format year-month-day
    new_patient['brithDate'] = info['brithDate']

    researcher = await search_single_resource(client, identifier="sparc-practitioner-yyds-001", resource="Practitioner")

    new_patient["generalPractitioner"] = [
        {
            "reference": researcher.to_reference().reference,
            "display": "Dr Adam Careful"
        }
    ]

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


async def search_single_resource(client, identifier, resource):
    resources_search_set = client.resources(resource)
    # workflows = await workflowResources.search(identifier=identifier, version="1.0.0").fetch_all()
    searched_resource = await resources_search_set.search(identifier=identifier).first()
    return searched_resource


async def search_resources(client, resource):
    resources_search_set = client.resources(resource)
    # workflows = await workflowResources.search(identifier=identifier, version="1.0.0").fetch_all()
    resources = await resources_search_set.search().fetch_all()
    return resources


async def delete_resource(client, identifier, resource):
    resources = await search_resource(client, identifier, resource)
    for resource in resources:
        await resource.delete()


async def clear_all_resources(client):
    await delete_resources(client, "ImagingStudy")
    await delete_resources(client, "Composition")
    await delete_resources(client, "Observation")
    await delete_resources(client, "Task")
    await delete_resources(client, "Patient")
    await delete_resources(client, "PlanDefinition")
    await delete_resources(client, "Practitioner")


async def delete_practitioner(client, identifier):
    practitioner = await search_single_resource(client, identifier, "Practitioner")
    patients = await client.resources("Patient").search(general_practitioner=practitioner.to_reference()).fetch_all()

    for patient in patients:
        new_gps = []
        for gp in patient["generalPractitioner"]:
            if gp.reference == practitioner.to_reference().reference:
                continue
            else:
                new_gps.append(gp)

        if len(new_gps) > 0:
            patient["generalPractitioner"] = new_gps
            await patient.save()
        else:
            identifier_patient = get_resource_identifier(patient, "http://sparc.sds.dataset")
            await delete_patient(client, identifier_patient)
    await practitioner.delete()


async def delete_patient(client, identifier):
    patient = await search_single_resource(client, identifier, "Patient")
    workflow_processes = await client.resources("Task").search(requester=patient.to_reference()).fetch_all()
    primary_observations = await client.resources("Observation").search(subject=patient.to_reference()).fetch_all()
    primary_imagingstudies = await client.resources("ImagingStudy").search(subject=patient.to_reference()).fetch_all()

    for ob in primary_observations:
        await ob.delete()
    for isy in primary_imagingstudies:
        await isy.delete()

    await delete_workflow_processes(client, workflow_processes)

    await patient.delete()


async def delete_workflow(client, identifier):
    workflow = await search_single_resource(client, identifier, "PlanDefinition")
    workflow_processes = await client.resources("Task").search(focus=workflow.to_reference()).fetch_all()

    await delete_workflow_processes(client, workflow_processes)
    await workflow.delete()


async def delete_workflow_processes(client, workflow_processes):
    for process in workflow_processes:
        identifier_process = get_resource_identifier(process, "http://sparc.sds.dataset")
        await delete_workflow_process(client, identifier=identifier_process)


async def delete_workflow_process(client, identifier):
    workflow_process = await search_single_resource(client, identifier, "Task")
    compositions = await client.resources('Composition').search(subject=workflow_process.to_reference()).fetch_all()
    for composition in compositions:
        identifier_composition = get_resource_identifier(composition, "http://sparc.sds.dataset")
        await delete_composition(client, identifier=identifier_composition)

    await workflow_process.delete()


async def delete_composition(client, identifier):
    composition = await search_single_resource(client, identifier, "Composition")
    for section in composition['section']:
        for ob in section['entry']:
            await ob.delete()
    await composition.delete()


async def delete_resources(client, resource):
    resources = await search_resources(client, resource)
    for resource in resources:
        await resource.delete()


def get_resource_identifier(resource, system):
    if isinstance(resource['identifier'], list):
        filtered_data = [d for d in resource['identifier'] if d.get('system') == system]
        identifier = filtered_data[0]
        return identifier.get('value')
    else:
        return resource['identifier']['value']


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
