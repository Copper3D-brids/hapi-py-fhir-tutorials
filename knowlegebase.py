def switch_case_group_code(argument):
    switcher = {
        "male":  {
            "code": {
                "coding": [
                    {
                        "system": "https://loinc.org/",
                        "code": "76691-5",
                        "display": "Gender identity"
                    },
                ],
                "text": "Gender identity"
            },
            "characteristic": [
                {
                    "code": {
                        "text": "gender"
                    },
                    "valueCodeableConcept": {
                        "text": "male"
                    },
                    "exclude": False
                }
            ]
        },
        "female": {
            "code": {
                "coding": [
                    {
                        "system": "https://loinc.org/",
                        "code": "76691-5",
                        "display": "Gender identity"
                    },
                ],
                "text": "Gender identity"
            },
            "characteristic": [
                {
                    "code": {
                        "text": "gender"
                    },
                    "valueCodeableConcept": {
                        "text": "female"
                    },
                    "exclude": False
                }
            ]
        },
        "age_[20-30]": {
            "code": {
                "coding": [
                    {
                        "system": "https://loinc.org/",
                        "code": "46251-5",
                        "display": "Age Group"
                    },
                ],
                "text": "Age Group"
            },
            "characteristic": [
                {
                    "code": {
                        "text": "age_group[20-30]"
                    },
                    "valueCodeableConcept": {
                        "text": "age_group[20-30]"
                    },
                    "exclude": False
                }
            ]
        },
        "age_[30-40]": {
            "code": {
                "coding": [
                    {
                        "system": "https://loinc.org/",
                        "code": "46251-5",
                        "display": "Age Group"
                    },
                ],
                "text": "Age Group"
            },
            "characteristic": [
                {
                    "code": {
                        "text": "age_group[30-40]"
                    },
                    "valueCodeableConcept": {
                        "text": "age_group[30-40]"
                    },
                    "exclude": False
                }
            ]
        }
    }
    return switcher.get(argument, "invalid")
