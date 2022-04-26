controls = [
    [
        ('attr_group', 'status'),
        ('group_a', '... >= 200 DM / salary for at least 1 year'),
        ('group_b', '0<= ... < 200 DM')
    ],
    [
        ('attr_group', 'duration'),
        ('group_a', '< 1 yr'),
        ('group_b', '1 <= ... < 4 yrs')
    ],
    [
        ('attr_group', 'duration'),
        ('group_a', '1 <= ... < 4 yrs'),
        ('group_b', '4 <= ... < 7 yrs')
    ],
    [
        ('attr_group', 'credit-history'),
        ('group_a',  'all credits at this bank paid back duly'),
        ('group_b',  'no credits taken/all credits paid back duly')
    ],
    [
        ('attr_group', 'credit-history'),
        ('group_a',  'no credits taken/all credits paid back duly'),
        ('group_b',  'delay in paying off in the past')
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
    [
        ('attr_group', 'purpose'),
        ('group_a', 'furniture/equipment'),
        ('group_b', 'domestic appliances')
    ],
    [
        ('attr_group', 'purpose'),
        ('group_a', 'retraining'),
        ('group_b', 'repairs')
    ],
    [
        ('attr_group', 'credit-amount'),
        ('group_a', '(2500, 5000]'),
        ('group_b', '(500, 2500]')
    ],
    [
        ('attr_group', 'credit-amount'),
        ('group_a', '(2500, 5000]'),
        ('group_b', '(5000, 10000]')
    ],
    [
        ('attr_group', 'saving-account'),
        ('group_a', '... <  100 DM'),
        ('group_b', 'unknown/no savings account')
    ],
    [
        ('attr_group', 'saving-account'),
        ('group_a', '... >= 1000 DM'),
        ('group_b', '... <  100 DM')
    ],
    [
        ('attr_group', 'employment'),
        ('group_a', '4 <= ... < 7 yrs'),
        ('group_b', '>= 7 yrs')
    ],
    [
        ('attr_group', 'employment'),
        ('group_a', '4 <= ... < 7 yrs'),
        ('group_b', '1 <= ... < 4 yrs')
    ],
    [
        ('attr_group', 'installment-rate'),
        ('group_a', '25% <= ... < 35%'),
        ('group_b', '20% <= ... < 25%')
    ],
    [
        ('attr_group', 'installment-rate'),
        ('group_a', '20% <= ... < 25%'),
        ('group_b', '< 20%')
    ],
    [
        ('attr_group', 'sex-marst'),
        ('group_a', 'female : single'),
        ('group_b', 'female : non-single or male : single')
    ],
    [
        ('attr_group', 'sex-marst'),
        ('group_a', 'male : married/widowed'),
        ('group_b', 'male : divorced/separated')
    ],
    [ # reasonable
        ('attr_group', 'other-debtors'),
        ('group_a', 'guarantor'),
        ('group_b', 'none')
    ],
    [
        ('attr_group', 'other-debtors'),
        ('group_a', 'none'),
        ('group_b', 'co-applicant')
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
    [ # interesting
        ('attr_group', 'property'),
        ('group_a', 'unknown / no property'),
        ('group_b', 'car or other')
    ],
    [
        ('attr_group', 'property'),
        ('group_a', 'unknown / no property'),
        ('group_b', 'real estate')
    ],
    [ # interesting
        ('attr_group', 'age'),
        ('group_a', '(40, 50]'),
        ('group_b', '(50, 60]')
    ],
    [
        ('attr_group', 'age'),
        ('group_a', '(60, 70]'),
        ('group_b', '(50, 60]')
    ],
    [
        ('attr_group', 'other-installment-plans'),
        ('group_a', 'none'),
        ('group_b', 'stores')
    ],
    [
        ('attr_group', 'other-installment-plans'),
        ('group_a', 'stores'),
        ('group_b', 'bank')
    ],
    [ # maybe interesting
        ('attr_group', 'housing'),
        ('group_a', 'rent'),
        ('group_b', 'own')
    ],
    [
        ('attr_group', 'housing'),
        ('group_a', 'rent'),
        ('group_b', 'for free')
    ],
    [
        ('attr_group', 'existing-credits'),
        ('group_a', '1'),
        ('group_b', '>= 6')
    ],
    [
        ('attr_group', 'existing-credits'),
        ('group_a', '4-5'),
        ('group_b', '>= 6')
    ],
    [
        ('attr_group', 'people-liable'),
        ('group_a', '3 or more'),
        ('group_b', '0 to 2')
    ],
    [
        ('attr_group', 'telephone'),
        ('group_a', 'yes (under customer name)'),
        ('group_b', 'no')
    ],
    [ # interesting
        ('attr_group', 'foreign-worker'),
        ('group_a', 'yes'),
        ('group_b', 'no')
    ]
]