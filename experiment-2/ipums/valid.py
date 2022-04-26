valid = [
    [
        ('attr_group', 'SEX'),
        ('group_a', 'Male'),
        ('group_b', 'Female')
    ],
    [
        ('attr_group', 'RELATE'),
        ('group_a', 'Grandchild'),
        ('group_b', 'Foster children')
    ],
    [
        ('attr_group', 'EDUC'),
        ('group_a', "Bachelor's degree"),
        ('group_b', 'High school diploma or equivalent')
    ],
]

invalid = [
    [
        ('attr_group', 'RELATE'),
        ('group_a', 'Spouse'),
        ('group_b', 'Head/householder')
    ],
    [
        ('attr_group', 'EDUC'),
        ('group_a', "None or preschool"),   # 15553.798526	22931 
        ('group_b', "Grade 9") # 16418.254292	3437
    ]
]

questions = [
    [
        ('attr_group', 'SEX'),
        ('group_a', 'Male'),
        ('group_b', 'Female')
    ],
    [
        ('attr_group', 'RELATE'),
        ('group_a', 'Grandchild'),
        ('group_b', 'Foster children')
    ],
    [
        ('attr_group', 'RELATE'),
        ('group_a', 'Spouse'),
        ('group_b', 'Head/householder')
    ],
    [
        ('attr_group', 'EDUC'),
        ('group_a', "Bachelor's degree"),
        ('group_b', 'High school diploma or equivalent')
    ],
    [
        ('attr_group', 'EDUC'),
        ('group_a', "None or preschool"),   # 15553.798526	22931 
        ('group_b', "Grade 9") # 16418.254292	3437
    ]
]

qtype = [
    'valid',
    'valid',
    'invalid',
    'valid',
    'invalid'
]