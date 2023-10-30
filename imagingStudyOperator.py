from utils import pprint
from pathlib import Path
import pydicom
from datetime import datetime
import uuid


async def operationImagingStudy(client):
    # sparc_structure = await perpareData(client)
    # await createImagingStudy(client, sparc_structure)
    # await updateImagingStudy(client)
    await searchImagingStudy(client)
    # await deleteImagingStudy(client)


async def perpareData(client):
    sparc_fhir_structure = {}
    sparc_data_paths = [Path("./sparc_fhir_breast_dataset/primary/"), Path("./sparc_fhir_heart_dataset/primary/")]
    for sparc_data_path in sparc_data_paths:
        sparc_fhir_structure[sparc_data_path.parent] = {}
        for study in sparc_data_path.iterdir():
            if study.is_dir():
                sparc_fhir_structure[sparc_data_path.parent][study.name] = {}
                for series in study.iterdir():
                    if series.is_dir():
                        sparc_fhir_structure[sparc_data_path.parent][study.name][series.name] = list(
                            series.glob('*.dcm'))

    print(list(sparc_fhir_structure.keys()))

    return sparc_fhir_structure

    # await deletePatients(client, ['bob', 'db'])

    # await createPatients(client)


async def deletePatients(client, names):
    patientResource = client.resources('Patient')
    for name in names:
        patients = await patientResource.search(name=[name]).fetch_all()
        for patient in patients:
            await patient.delete()


async def createPatients(client):
    bob = client.resource('Patient',
                          name=[
                              {
                                  'given': ['Bob'],
                                  'family': '',
                                  'use': 'official',
                                  'prefix': ['Mr. '],
                              }
                          ],
                          gender="female",
                          brithDate='1995-09-22'
                          )
    db = client.resource('Patient',
                         name=[
                             {
                                 'given': ['Db'],
                                 'family': '',
                                 'use': 'official',
                                 'prefix': ['Mr. '],
                             }
                         ],
                         gender="female",
                         brithDate='1993-08-15'
                         )
    await bob.save()
    await db.save()


async def deleteImagingStudy(client, imagingstudys):
    for imagingstudy in imagingstudys:
        await imagingstudy.delete()


async def updateImagingStudy(client):
    imagingStudyResourceSearchSet = client.resources('ImagingStudy')
    count = await imagingStudyResourceSearchSet.count()
    imagingStudys = await imagingStudyResourceSearchSet.limit(count).fetch()

    # https://browser.ihtsdotools.org/?perspective=full&conceptId1=76752008&edition=MAIN/2023-10-01&release=&languages=en&latestRedirect=false
    # find a patient in which datasets
    for imagingstudy in imagingStudys:
        if "identifier" in imagingstudy:
            for identifier in imagingstudy['identifier']:
                if identifier.get('system') == 'urn:sparc_dataset:uid':

                    for index, series in enumerate(imagingstudy["series"]):
                        if "breast" in identifier.get('value'):
                            imagingstudy["series"][index]["bodySite"] = {
                                "system": "http://snomed.info/sct",
                                "code": "76752008",
                                "display": "Breast"
                            }
                        elif "heart" in identifier.get('value'):
                            imagingstudy["series"][index]["bodySite"] = {
                                "system": "http://snomed.info/sct",
                                "code": "80891009",
                                "display": "Heart"
                            }
                        await imagingstudy.save()




async def createImagingStudy(client, sparc_fhir_structure):
    """
        As for creating a resource, should use client.resource('ImagingStudy')
    """

    # (0020, 000d) Study Instance UID
    # (0020, 000e) Series Instance UID
    # (0008, 0018) SOP Instance UID
    # (0020, 0013) Instance Number
    # (0008, 0030) Study Time
    # (0020,1208) Number of Study Related Instances
    # (0020,1206) Number of Study Related Series
    # (0020,1209) Number of Series Related Instances
    # (0018, 0010) Contrast/Bolus Agent                LO: 'Magnevist'
    # (0018, 0015) Body Part Examined                  CS: 'BREAST'

    datasets = list(sparc_fhir_structure.keys())

    for dataset in datasets:
        studies = list(sparc_fhir_structure[dataset].keys())
        for study in studies:
            patient = None
            samples = list(sparc_fhir_structure[dataset][study].keys())
            dicom_file = pydicom.dcmread(sparc_fhir_structure[dataset][study][samples[0]][0])
            study_uid = dicom_file[(0x0020, 0x000d)].value

            try:
                dicom_study_time = dicom_file[(0x0008, 0x0030)].value
                started_time = datetime.strptime(dicom_study_time, "%H%M%S.%f").strftime("%Y-%m-%dT%H:%M:%S")
            except:
                started_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            try:
                numberOfSeries = int(dicom_file[(0x0020, 0x1206)].value)
            except:
                numberOfSeries = len(samples)

            try:
                numberOfInstances = int(dicom_file[(0x0020, 0x1208)].value)
            except:
                numberOfInstances = 0
                for sample in samples:
                    numberOfInstances += len(sparc_fhir_structure[dataset][study][sample])

            if 'bob' in study:
                patient = await client.resources('Patient').search(name=['Bob']).first()
            elif 'db' in study:
                patient = await client.resources('Patient').search(name=['db']).first()

            if patient is not None:
                series = []
                for sample in samples:
                    instances = []
                    sample_dicom_file = pydicom.dcmread(sparc_fhir_structure[dataset][study][sample][0])
                    try:
                        numberOfSeriesInstances = int(sample_dicom_file[(0x0020, 0x1209)].value)
                    except:
                        numberOfSeriesInstances = len(sparc_fhir_structure[dataset][study][sample])

                    for item in sparc_fhir_structure[dataset][study][sample]:
                        instance_dicom_file = pydicom.dcmread(item)
                        dicom_instance = {
                            "uid": instance_dicom_file[(0x0008, 0x0018)].value,
                            "number": instance_dicom_file[(0x0020, 0x0013)].value,
                        }
                        instances.append(dicom_instance)

                    series.append({
                        "uid": sample_dicom_file[(0x0020, 0x000e)].value,
                        "modality": {
                            "system": "http://dicom.nema.org/resources/ontology/DCM",
                            "code": "MR"
                        },
                        "numberOfInstances": numberOfSeriesInstances,
                        "instance": instances
                    })

                imagingResource = client.resource('ImagingStudy',
                                                  identifier=[{
                                                      "system": "urn:dicom:uid",
                                                      "value": f"urn:oid:{study_uid}"
                                                  },
                                                      {
                                                          "use": 'temp',
                                                          "system": "urn:sparc_study:uid",
                                                          "value": f"urn:uid:{study + '-' + study_uid}"
                                                      },
                                                      {
                                                          "use": 'temp',
                                                          "system": "urn:sparc_dataset:uid",
                                                          "value": f"urn:uid:{str(dataset) + '-' + str(uuid.uuid4())}"
                                                      },
                                                  ],
                                                  status="available",
                                                  subject=patient.to_reference(),
                                                  started=started_time,
                                                  numberOfSeries=numberOfSeries,
                                                  numberOfInstances=numberOfInstances,
                                                  series=series
                                                  )
                await imagingResource.save()


async def searchImagingStudy(client):
    patientsResourceSearchSet = client.resources("Patient")
    bob = await patientsResourceSearchSet.search(name=['bob']).first()

    # find all studies of a patient cross all datasets
    imagingStudyResourceSearchSet = client.resources('ImagingStudy')
    imagingStudys = await imagingStudyResourceSearchSet.search(patient=bob.to_reference()).fetch_all()
    printImagingStudys(imagingStudys)

    # find a patient in which datasets
    for imagingstudy in imagingStudys:
        print(imagingstudy['series'])
        for identifier in imagingstudy['identifier']:
            if identifier.get('system') == 'urn:sparc_dataset:uid':
                print(identifier.get('value'))



    # find all breast ImagingStudy resources
    imagingstudys = await client.resources('ImagingStudy').search(bodysite="76752008").fetch_all()
    print(imagingstudys)
    # find all heart ImagingStudy resources
    imagingstudys = await client.resources('ImagingStudy').search(bodysite="80891009").fetch_all()
    print(imagingstudys)

    #urn:uid:sparc_fhir_heart_dataset-9c3319e9-38f0-42fc-9b41-28a1be44f72e
    tt = await imagingStudyResourceSearchSet.search(identifier='urn:uid:sparc_fhir_heart_dataset-9c3319e9-38f0-42fc-9b41-28a1be44f72e').fetch()
    print(tt)


def printImagingStudys(ImagingStudys):
    for ImagingStudy in ImagingStudys:
        printImagingStudy(ImagingStudy)


def printImagingStudy(ImagingStudy):
    print('{0} {1} {2} {3}'.format(
        ImagingStudy.get('id'),
        ImagingStudy.get('series')[0].get('uid'),
        ImagingStudy.get_by_path('series[0].instance[0].uid'),
        ImagingStudy.get('identifier'),
    ))
