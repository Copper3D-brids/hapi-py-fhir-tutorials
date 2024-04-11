from utils import pprint


async def operationPatient(client):
    # await getSortedPatients(client)
    await searchPatient(client)
    # await getFirstPatient(client)
    # await createPatient(client)
    # await updatePatient(client)
    # await deletePatient(client)


async def deletePatient(client):
    patientResource = client.resources('Patient')
    patients = await patientResource.search(name=['John', 'Thompson']).fetch_all()
    for patient in patients:
        await patient.delete()


async def updatePatient(client):
    patientResource = client.resources('Patient')
    patients = await patientResource.search(name=['John', 'Thompson']).fetch_all()
    for patient in patients:
        patient['address'] = {
            "line": "1818 Market St",
            "city": "Auckland",
            "state": "Auckland",
            "postalCode": "1010",
            "country": "NZ"
        }
        patient['telecom'] = [
            {
                "system": "phone",
                "value": "(215) 352-3801",
                "use": "home"
            }
        ]
        patient['extension'] = [
            {
              "url" : "http://hl7.org.nz/fhir/StructureDefinition/nz-ethnicity",
              "valueCodeableConcept" : {
                "coding" : [
                  {
                    "system" : "https://standards.digital.health.nz/ns/ethnic-group-level-4-code",
                    "code" : "21111",
                    "display" : "Māori"
                  }
                ]
              }
            },
        ]
        await patient.save()


async def createPatient(client):
    """
        As for creating a resource, should use client.resource('Patient')
    """
    new_patient = client.resource('Patient')
    new_patient['name'] = [
        {
            'given': ['John'],
            'family': 'Thompson',
            'use': 'official',
            'prefix': ['Mr. '],
        }
    ]

    # format year-month-day
    new_patient['brithDate'] = '1995-09-22'
    await new_patient.save()
    print(new_patient['id'])
    print(new_patient['meta'])


async def getFirstPatient(client):
    """
        As for search resources, we should use client.resources('Patient')
    """
    patientResource = client.resources('Patient')
    # get first patient
    patient = await patientResource.first()
    printPatients([patient])
    # pprint(patient.name)
    print("Name: ")
    pprint(patient['name'])
    print("Address: ")
    pprint(patient['address'])
    print("Telecom: ")
    pprint(patient['telecom'])


async def searchPatient(client):
    """
        search(name=['John', 'Thompson']): AND search parameter, search all patients who with the first name John and the last name Thompson.
        search(name='John,Carl'): OR search parameter, search all patients who with name John or Carl,
    """
    patientResource = client.resources('Patient')
    patients = await patientResource.search(birthdate='1976-06-06').fetch_all()
    print(patients)
    printPatients(patients)
    # patients = await patientResource.search(birthdate='1976-06-06').fetch_all()
    # printPatients(patients)
    # patients = await patientResource.search(address='Philadelphia').fetch_all()
    # printPatients(patients)


async def getSortedPatients(client):
    patients = await client.resources('Patient').fetch()

    printPatients(patients)
    print("*********************1*********************")
    # TODO Sorting results
    patients = await client.resources('Patient').sort('telecom').fetch()
    printPatients(patients)
    print("*********************2*********************")


def printPatients(patients):
    for patient in patients:
        printPatient(patient)


def printPatient(patient):
    print(patient.get('extension'))
    print('{0} {1} {2} {3} {4} {5} {6}'.format(
        patient.get('id'),
        patient.get('meta'),
        patient.get_by_path('name.0.family'),
        patient.get_by_path('name.0.given.0'),
        patient.get('gender'),
        patient.get_by_path('telecom.0.value'),
        patient.get('identifier'),
    ))
