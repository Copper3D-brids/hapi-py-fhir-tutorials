from utils import pprint
import asyncio

async def do_observation(client):
    observationOperator = ObservationOperator(client)
    # await observationOperator.findOBwithLimit()
    # await observationOperator.createObservation()
    await observationOperator.search_specific_patient()


class ObservationOperator:
    def __init__(self, client):
        self.client = client


    async def findOBwithLimit(self):
        observations = await self.client.resources('Observation').limit(10).fetch()
        pprint(observations[0])

    async def search_specific_patient(self):
        patients = await self.client.resources('Patient').has('Observation', 'patient', code='8302-2').fetch()

        pprint(patients)

    async def createObservation(self):
        new_observation = self.client.resource(
            'Observation',
            status='preliminary',
            category = [{
                'coding':[{
                    'system': 'http://hl7.org/fhir/observation-category'
                }]
            }],
            code={
                'coding':[{
                    'system': 'http://loinc.org',
                    'code': '8310-5'
                }]
            }
          )
        new_observation['effectiveDateTime'] = '2018-10-20'
        new_observation['valueQuantity'] = {
            'system': 'http://unitsofmeasure.org',
            'value': 96.8,
            'code': 'degF'
        }

        patient = await self.client.resources('Patient').search(name=['John', 'Thompson']).first()
        new_observation['subject'] = patient.to_reference()
        await new_observation.save()