import numpy as np

controls = [
    [
        ('agg', 'CNT')
    ],
    [
        ('agg', 'SUM')
    ]
]

for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
    controls.append(
        [
            ('rho_query', rho)
        ]
    )
    controls.append(
        [
            ('rho_topk', rho)
        ]
    )
    controls.append(
        [
            ('rho_influ', rho)
        ]
    )
    controls.append(
        [
            ('rho_rank', rho)
        ]
    )
    
for scale in [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9]:
    controls.append(
        [
            ('scale', scale)
        ]
    )
    
for split_factor in [0.1, 0.3, 0.5, 0.7, 0.9]:
    controls.append(
        [
            ('split_factor', split_factor)
        ]
    )
    
for k in [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 50, -1]:
    controls.append(
        [
            ('k', k)
        ]
    )
    
for gamma in np.r_[np.linspace(0.1, 0.9, 9), [0.95, 0.99]]:
    controls.append(
        [
            ('gamma', gamma)
        ]
    )
    
controls += [
    [
        ('predicate_strategy', '2-way marginal')
    ],
    [
        ('predicate_strategy', '3-way marginal')
    ]
]