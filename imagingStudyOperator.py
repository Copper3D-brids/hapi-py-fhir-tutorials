from utils import pprint


async def operationImagingStudy(client):
    # await getSortedImagingStudys(client)
    await searchImagingStudy(client)
    # await getFirstImagingStudy(client)
    # await createImagingStudy(client)
    # await updateImagingStudy(client)
    # await deleteImagingStudy(client)


async def deleteImagingStudy(client):
    ImagingStudyResource = client.resources('ImagingStudy')
    ImagingStudys = await ImagingStudyResource.search(name=['John', 'Thompson']).fetch_all()
    for ImagingStudy in ImagingStudys:
        await ImagingStudy.delete()


async def updateImagingStudy(client):
    ImagingStudyResource = client.resources('ImagingStudy')
    ImagingStudys = await ImagingStudyResource.search(name=['John', 'Thompson']).fetch_all()
    for ImagingStudy in ImagingStudys:
        ImagingStudy['address'] = {
            "line": "1818 Market St",
            "city": "Auckland",
            "state": "Auckland",
            "postalCode": "1010",
            "country": "NZ"
        }
        ImagingStudy['telecom'] = [
            {
                "system": "phone",
                "value": "(215) 352-3801",
                "use": "home"
            }
        ]
        await ImagingStudy.save()


async def createImagingStudy(client):
    """
        As for creating a resource, should use client.resource('ImagingStudy')
    """
    new_ImagingStudy = client.resource('ImagingStudy')
    new_ImagingStudy['name'] = [
        {
            'given': ['John'],
            'family': 'Thompson',
            'use': 'official',
            'prefix': ['Mr. '],
        }
    ]

    # format year-month-day
    new_ImagingStudy['brithDate'] = '1995-09-22'
    await new_ImagingStudy.save()
    print(new_ImagingStudy['id'])
    print(new_ImagingStudy['meta'])


async def searchImagingStudy(client):
    """
        search(name=['John', 'Thompson']): AND search parameter, search all ImagingStudys who with the first name John and the last name Thompson.
        search(name='John,Carl'): OR search parameter, search all ImagingStudys who with name John or Carl,
    """


    patientsResourceSearchSet = client.resources("Patient")
    patients = await patientsResourceSearchSet.search(name=['Allyson474','Crooks415']).fetch()

    imagingStudyResourceSearchSet = client.resources('ImagingStudy')
    imagingStudys = await imagingStudyResourceSearchSet.search(patient=patients[0].to_reference()).fetch_all()
    print(imagingStudys)



async def getSortedImagingStudys(client):
    imagingStudys = await client.resources('ImagingStudy').fetch()

    printImagingStudys(imagingStudys)
    print("*********************1*********************")


def printImagingStudys(ImagingStudys):
    for ImagingStudy in ImagingStudys:
        printImagingStudy(ImagingStudy)


def printImagingStudy(ImagingStudy):
    print('{0} {1} {2} {3} {4} {5} {6}'.format(
        ImagingStudy.get('id'),
        ImagingStudy.get('meta'),
        ImagingStudy.get_by_path('name.0.family'),
        ImagingStudy.get_by_path('name.0.given.0'),
        ImagingStudy.get('gender'),
        ImagingStudy.get_by_path('telecom.0.value'),
        ImagingStudy.get('identifier'),
    ))
