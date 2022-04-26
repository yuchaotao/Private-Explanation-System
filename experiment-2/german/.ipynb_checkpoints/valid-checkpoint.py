valid = [
    [
        ('attr_group', 'status'),
        ('group_a', '... < 0 DM'),
        ('group_b', 'no checking account')
    ],
    [
        ('attr_group', 'purpose'),
        ('group_a', 'car (new)'),
        ('group_b', 'car (used)')
    ],
    [ # intersting
        ('attr_group', 'residence'),
        ('group_a', '< 1 yr'),
        ('group_b', '>= 7 yrs')
    ],
]

invalid = [
    [
        ('attr_group', 'purpose'),
        ('group_a', 'vacation'),
        ('group_b', 'business')
    ],
    [
        ('attr_group', 'residence'),
        ('group_a', '4 <= ... < 7 yrs'),
        ('group_b', '1 <= ... < 4 yrs')
    ],
]

questions = [
    [
        ('attr_group', 'status'),
        ('group_a', '... < 0 DM'),
        ('group_b', 'no checking account')
    ],
    [
        ('attr_group', 'purpose'),
        ('group_a', 'car (new)'),
        ('group_b', 'car (used)')
    ],
    [
        ('attr_group', 'purpose'),
        ('group_a', 'vacation'),
        ('group_b', 'business')
    ],
    [ # intersting
        ('attr_group', 'residence'),
        ('group_a', '< 1 yr'),
        ('group_b', '>= 7 yrs')
    ],
    [
        ('attr_group', 'residence'),
        ('group_a', '4 <= ... < 7 yrs'),
        ('group_b', '1 <= ... < 4 yrs')
    ],
]



qtype = [
    'valid',
    'valid',
    'invalid',
    'valid',
    'invalid'
]