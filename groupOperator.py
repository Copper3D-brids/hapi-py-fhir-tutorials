async def operationGroup(client):
    # await createPatientGroup(client)
    await searchGroup(client)
    # await deleteGroup(client)
async def createPatientGroup(client):
    new_group = client.resource('Group')
    new_group['type'] = "person"
    new_group['code'] = {
        "text": "Breast Cancer"
    }
    new_group['name'] = "Breast Cancer"

    patientsResourceSearchSet = client.resources("Patient")
    Linman = await patientsResourceSearchSet.search(name=['Linman']).first()

    new_group['member'] = [
        {
            "entity": Linman.to_reference(),
            "period": {
                "start": "2014-10-08"
            }
        },
    ]

    print(new_group['member'])

    await new_group.save()


async def searchGroup(client):
    patientsResourceSearchSet = client.resources("Patient")
    Linman = await patientsResourceSearchSet.search(name=['Linman']).first()

    patientGroupResource = client.resources('Group')
    group = await patientGroupResource.search(member=Linman.to_reference()).fetch_all()
    patient = await group[0]['member'][0]['entity'].to_resource()
    print(patient['name'])

async def deleteGroup(client):
    patientGroupResource = client.resources('Group')
    groups = await patientGroupResource.fetch_all()
    print(groups)
    for group in groups:
        await group.delete()