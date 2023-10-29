async def do_schedule(client):
    await getGPSchedule(client)
    await loadSlots(client)


def search(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")


async def getGPSchedule(client):

    print("******************************* Result for getGPSchedule:  **************************************")
    schedules = await client.resources('Schedule').search(**{'date': '2018-09-16', 'service-type': 124}).include('Schedule','actor').fetch()
    for schedule in schedules:
        for actor in schedule['actor']:
            print(actor)

    for schedule in schedules:
        actors = [await actor.to_resource() for actor in schedule['actor']]
        print(actors)


async def loadSlots(client):

    print("******************************* Result for loadSlots:  **************************************")

    schedules = await client.resources('Schedule').search(**{'date': '2018-09-16', 'service-type': 124}).include(
        'Schedule', 'actor').fetch()
    slots = [await client.resources('Slot').search(schedule=schedule['id']).fetch() for schedule in schedules]
    print(slots)

    schedule = schedules[0]
    slots = await client.resources('Slot').search(schedule=schedule['id']).fetch()
    details = [(slot.get('start'),slot.get('end'),slot.get('status'))for slot in slots]
    print(details)

    slots = await client.resources('Slot').search(schedule=schedule['id'], status='free').fetch()
    details = [(slot.get('start'),slot.get('end'),slot.get('status'))for slot in slots]
    print(details)

    slots = await client.resources('Slot').search(schedule=schedule['id'], start='2018-09-16T11:00:00').fetch()
    details = [(slot.get('start'),slot.get('end'),slot.get('status'))for slot in slots]
    print(details)

