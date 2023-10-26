from utils import pprint
async def do_appointment(client):
   participants = await find_pactitioner(client)
   await creatAppointment(client,participants[0],participants[1],participants[2])
   # await updateAppointment(client, participants[1])
   # await findAppointment(client, participants[1])

async def find_pactitioner(client):
    patient = await client.resources('Patient').search(name=['john','thompson']).first()
    print(patient)
    practitioner = await client.resources('Practitioner').search(name=['Kelly', 'Smith']).first()
    print(practitioner)
    schedule = await client.resources('Schedule').search(actor=practitioner['id']).first()
    print(schedule)

    slot = await client.resources('Slot').search(schedule=schedule['id'], start='2018-09-16T11:00:00').first()
    detail = (slot.get('start'),slot.get('end'),slot.get('status'))
    print(detail)
    slot['status'] = 'busy'
    await slot.save()
    return schedule,patient,slot

async def creatAppointment(client, schedule,patient,slot):
    print(schedule)
    participants = [{'actor':actor, 'status': 'needs-action'} for actor in schedule['actor']]

    print(participants)
    location = await participants[1]['actor'].to_resource()
    print(location['address'])

    # Plus the patient
    participants += [{'actor':patient.to_reference(), 'status':"accepted"}]

    appointment = client.resource(
        'Appointment',
        # id='appointment_for_john_thompson',
        status='proposed',
        start=slot['start'],
        end=slot['end'],
        slot=[slot],
        participant=participants
    )

    await appointment.save()
    pprint(appointment)

async def updateAppointment(client, patient):
    appointment = await client.resources('Appointment').search(
        date='2018-09-16T11:00:00'
    ).first()

    print(patient.to_reference())
    # for fhir R4 appointment has not subject field
    appointment['subject']= patient.to_reference()
    await appointment.save()

async def findAppointment(client, patient):
    appointments = await client.resources('Appointment').search(
        patient=patient.to_reference()
    ).fetch()

    details = [(ap.get('id'),ap.get('start'), ap.get('end'), ap.get('status')) for ap in appointments]
    print(details)