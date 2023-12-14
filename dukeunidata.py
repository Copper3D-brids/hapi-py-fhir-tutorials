from utils import pprint
from pathlib import Path
import pydicom
from datetime import datetime
import uuid


async def operationDukeEHR(client):
    linman = await getPatient(client)
    # us_imagingStudy = await generateImagingStudy(client, linman, Path("./sparc_fhir_breast_dataset/primary/sub-Linman-breast-2"), "US", "Ultrasound", {
    #                             "system": "http://snomed.info/sct",
    #                             "code": "73056007",
    #                             "display": "Breast"
    #                         })
    #
    # print(us_imagingStudy)

    # await generateObservationForUS(client)

    await searchEHR(client)


async def getPatient(client):
    patientsResourceSearchSet = client.resources("Patient")
    Linman = await patientsResourceSearchSet.search(name=['Linman']).first()

    return Linman


async def searchEHR(client):
    linman = await getPatient(client)
    imagingStudyResourceSearchSet = client.resources('ImagingStudy')
    # get all imagingStudy of patient linman
    # imagingStudys = await imagingStudyResourceSearchSet.search(patient=linman.to_reference()).fetch_all()
    # get all ultrasound imageStudy of patient linman
    imagingStudys = await imagingStudyResourceSearchSet.search(patient=linman.to_reference(), modality="US").fetch_all()
    # get the linman's ultrasound observation resource
    observation = await client.resources("Observation").search(patient=linman.to_reference(),
                                                               focus=imagingStudys[0].to_reference()).fetch_all()

    print(observation)


async def generateObservationForUS(client):
    linman = await getPatient(client)
    imagingStudyResourceSearchSet = client.resources('ImagingStudy')
    imagingStudys = await imagingStudyResourceSearchSet.search(patient=linman.to_reference(), modality="US").fetch_all()
    us_imagingstudy = imagingStudys[0]
    us_observation = client.resource(
        'Observation',
        status='preliminary',
        subject=linman.to_reference(),
        focus=us_imagingstudy.to_reference(),
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                "code": "laboratory"
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                "code": "21889-1",
                "display": "Size Tumor"
            }]
        },
        effectiveDateTime="2018-04-01T00:00:00Z",
        component=[
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "33728-7"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": 2.5,
                    "unit": "centimeters",
                    "system": "http://unitsofmeasure.org",
                    "code": "cm"
                }
            }
        ]
    )

    await us_observation.save()


async def generateImagingStudy(client, patient, path, code, display, bodySite):
    USImageStudyPath = path

    samples = sum(1 for item in USImageStudyPath.iterdir() if item.is_dir())

    first_sample_path = next(iter(USImageStudyPath.glob('*')))

    dicom_file = pydicom.dcmread(next(iter(first_sample_path.glob('*')), None))
    study_uid = dicom_file[(0x0020, 0x000d)].value

    try:
        dicom_study_time = dicom_file[(0x0008, 0x0030)].value
        started_time = datetime.strptime(dicom_study_time, "%H%M%S.%f").strftime("%Y-%m-%dT%H:%M:%S")
    except:
        started_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    try:
        numberOfSeries = int(dicom_file[(0x0020, 0x1206)].value)
    except:
        numberOfSeries = sum(1 for item in USImageStudyPath.iterdir() if item.is_dir())

    try:
        numberOfInstances = int(dicom_file[(0x0020, 0x1208)].value)
    except:
        numberOfInstances = 0
        for sample in USImageStudyPath.iterdir():
            numberOfInstances += sum(1 for item in sample.iterdir() if item.is_file())

    if patient is not None:
        series = []
        for sample in USImageStudyPath.iterdir():
            if sample.is_file():
                break
            instances = []
            first_file = next(iter(sample.glob('*')), None)
            sample_dicom_file = pydicom.dcmread(first_file)
            try:
                numberOfSeriesInstances = int(sample_dicom_file[(0x0020, 0x1209)].value)
            except:
                numberOfSeriesInstances = sum(1 for item in sample.iterdir() if item.is_file())

            for item in sample.iterdir():
                if item.is_dir():
                    break
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
                    "code": code,
                    "display": display
                },
                "bodySite": bodySite,
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
                                                  "value": f"urn:uid:{USImageStudyPath.name + '-' + study_uid}"
                                              },
                                              {
                                                  "use": 'temp',
                                                  "system": "urn:sparc_dataset:uid",
                                                  "value": f"urn:uid:{str(USImageStudyPath.parent.parent.name) + '-' + str(uuid.uuid4())}"
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

        return imagingResource
