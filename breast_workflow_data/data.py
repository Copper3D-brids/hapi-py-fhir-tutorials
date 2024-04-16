WORKFLOW_RESULT = [
    {
        'identifier': 'sparc-workflow-yyds-001-process-001-result-001',
        "title": "Result of closest distance",
        "loinc-code": "Closest distance",
        "method-code": "breast cancer workflow 1 code xxx",
        "component": [
            {
                "loinc-code": "tumour-nipple",
                'value': 4,
                'unit-code': 'cm',
                'display': 'distance between tumour and nipple'
            },
            {
                "loinc-code": "tumour-ribcage",
                'value': 3,
                'unit-code': 'cm',
                'display': 'distance between tumour and ribcage'
            },
            {
                "loinc-code": "tumour-skin",
                'value': 3.5,
                'unit-code': 'cm',
                'display': 'distance between tumour and skin'
            }
        ],

    },
    {
        'identifier': 'sparc-workflow-yyds-001-process-001-result-002',
        "title": "Result of tumour size",
        "loinc-code": "21889-1",
        "method-code": "787377000",
        "component": [{
            "loinc-code": "33728-7",
            'value': 1.5,
            'unit-code': 'cm',
            'display': 'Size.maximum dimension in Tumor'
        }],

    }
]

WORKFLOW_RESULT_LINMAN = [
    {
        'identifier': 'sparc-workflow-yyds-001-process-002-result-001',
        "title": "Result of closest distance",
        "loinc-code": "Closest distance",
        "method-code": "breast cancer workflow 1 code xxx",
        "component": [
            {
                "loinc-code": "tumour-nipple",
                'value': 2.5,
                'unit-code': 'cm',
                'display': 'distance between tumour and nipple'
            },
            {
                "loinc-code": "tumour-ribcage",
                'value': 1,
                'unit-code': 'cm',
                'display': 'distance between tumour and ribcage'
            },
            {
                "loinc-code": "tumour-skin",
                'value': 1.5,
                'unit-code': 'cm',
                'display': 'distance between tumour and skin'
            }
        ],

    },
    {
        'identifier': 'sparc-workflow-yyds-001-process-002-result-002',
        "title": "Result of tumour size",
        "loinc-code": "21889-1",
        "method-code": "787377000",
        "component": [{
            "loinc-code": "33728-7",
            'value': 2.5,
            'unit-code': 'cm',
            'display': 'Size.maximum dimension in Tumor'
        }],

    }
]

WORKFLOW_DESCRIPTION = {
    'title': 'breast computational workflow one',
    'type': 'workflow-definition',
    'date': '2024-04-10',
    'description': 'A computational workflow defines all actions of calculate the closest distance from tumour to nipple in breast research. It also will record the tumour size.',
    'purpose': """
                        # Purpose
                        ## Record size
                        - Record tumour size
                        ## Calculate closest distance.
                        - Closest distance between tumour and nipple
                        - Closest distance between tumour and skin
                        - Closest distance between tumour and ribcage
                    """,
    'author': [
        {
            'name': 'Prasad'
        }
    ],
    "action": [
        {
            "id": "breast_workflow_action_01",
            "title": "calculate closest distance from tumour to nipple",
            "output": [{
                "type": "Observation",
                "profile": "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tumor-size"
            }]
        },
        {
            "id": "breast_workflow_action_02",
            "title": "calculate tumour size",
            "output": [{
                "type": "Observation",
                "profile": "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tumor-size"
            }]
        }
    ]
}

PATIENT_INFOS = [
    {
        "givenname": "Aniyah",
        'familyname': '',
        "identifier": "sparc-patient-yyds-001",
        "brithDate": "1994-04-11",
        "Observation": [
            {
                'identifier': "sparc-patient-yyds-001-observation-001",
                "loinc-code": "8310-5",
                'value': 96.8,
                'unit-code': 'degF'
            },
            {
                'identifier': "sparc-patient-yyds-001-observation-002",
                "loinc-code": "30525-0",
                'value': 30,
                'unit-code': 'years'
            }
        ]
    },
    {
        "givenname": "Linman",
        "familyname": "Zhang",
        "identifier": "sparc-patient-yyds-002",
        "brithDate": "1993-04-10",
        "Observation": [
            {
                'identifier': "sparc-patient-yyds-002-observation-001",
                "loinc-code": "8310-5",
                'value': 93.8,
                'unit-code': 'degF'
            },
            {
                'identifier': "sparc-patient-yyds-002-observation-002",
                "loinc-code": "30525-0",
                'value': 31,
                'unit-code': 'years'
            }
        ]
    }
]
