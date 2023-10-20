import asyncio
from fhirpy import AsyncFHIRClient
from initialize import import_dataset
from patientOperator import operationPatient
from observationOperator import ObservationOperator, do_observation
from schedule import do_schedule
from appointment import do_appointment
from encounter import do_encounter
from imagingStudyOperator import operationImagingStudy
from utils import pprint

async def initDataSite(client):
    # dataset_path = './dataset_2/config'
    # dataset_path = './dataset_2/failed'
    # TODO: download the FHIR R 4 dataset from synthea website to the dataset folder.
    dataset_path = './dataset'
    await import_dataset(client, dataset_path)


async def main():
    client = AsyncFHIRClient(
        url='http://localhost:8080/fhir/',
        # 'http://hapi.fhir.org/baseR5',
        authorization='Bearer TOKEN',
    )

    # TODO 1: load synthea data
    # await initDataSite((client))
    #TODO 2: familar with Patient resource
    # await operationPatient(client)
    #TODO 3: familar with Observation resource
    # await do_observation(client)

    #TODO 4: familar with schedule
    await do_schedule(client)

    #TODO 5: familar with appointment
    # await do_appointment(client)

    #TODO 6: familar with encounter
    # await do_encounter(client)

    #TODO 7: ImagingStudy
    # await operationImagingStudy(client)

    # patients = client.resources('Patient')
    # patients_count = await patients.count()
    # print(patients_count)
    # # if patients_count == 0:
    # #     await initDataSite((client))
    # patients = patients.search(name='Lindgren255').limit(10).sort('name')
    # patients = await patients.fetch_all()  # Returns list of AsyncFHIRResource
    # print(len(patients), type(patients))
    # for p in patients:
    #     print(type(p.name[0]))
    #     print(p.name)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
