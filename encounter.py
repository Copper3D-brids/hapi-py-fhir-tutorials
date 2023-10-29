from utils import pprint


async def do_encounter(client):
    details = await setup_encounter(client)
    encounter = await create_encounter(client, details[0], details[1], details[2], details[3])
    await link_to_observation(client,encounter)


async def setup_encounter(client):
    patient = await client.resources('Patient').search(name=['Thompson', 'John']).first()
    practitioner = await client.resources('Practitioner').search(name=['Kelly', 'Smith']).first()
    location = await client.resources('Location').search(name='Hahnemann University Hospital').first()
    appointment = await client.resources('Appointment').search(actor=patient['id']).first()
    print(patient['id'])
    print(location['id'])
    r = patient.to_reference()
    return patient, practitioner, location, appointment


async def create_encounter(client, patient, practitioner, location, appointment):
    condition = client.resource(
        'Condition',
        id='condition_for_john_thompson',
        code={'coding': [{'system': 'http://snomed.info/sct', 'code': '38341003'}]},
        subject=patient
    )

    encounter = client.resource(
        'Encounter',
        id='encounter_for_john_thompson',
        status='in-progress',
        subject=patient.to_reference(),
        participant=[{
            'type': [{
                'coding': [{
                    'system': 'http://hl7.org/fhir/v3/ParticipationType',
                    'code': 'PPRF'
                }]
            }],
            'indivadual': practitioner.to_reference()
        }],
        appointment=appointment.to_reference(),
        diagnosis=[{'condition': condition.to_reference()}],
        location=[{'location': location.to_reference(), 'status': 'active'}]
    )

    return encounter


async def link_to_observation(client, encounter):
    temperature_observation = client.resource(
        'Observation',
        id='temperature_observation_for_john_thompson',
        status='preliminary',
        category=[{
            'coding': [{
                'system': 'http://hl7.org/fhir/observation-category',
                'code': 'vital-signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '8310-5'
            }]
        },
        effectiveDateTime='2018-09-16',
        valueQuantity={
            'system': 'http://unitsofmeasure.org',
            'value': 96.8,
            'code': 'degF'
        },
        encounter=encounter.to_reference()
    )
    pprint(temperature_observation)

    blood_pressure_observation = client.resource(
        'Observation',
        id='blood_pressure_observation_for_john_thompson',
        status='preliminary',
        category=[{
            'coding':[{
                'system': 'http://hl7.org/fhir/observation-catagory',
                'code': 'vital-signs'
            }]
        }],
        code={
            'coding':[{
                'system':'http://loinc.org',
                'code': '55284-4'
            }]
        },
        effectiveDateTime='2018-09-16',
        encounter=encounter.to_reference()
    )
    pprint(blood_pressure_observation)
