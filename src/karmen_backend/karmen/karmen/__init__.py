
ROLE_ADMIN = 'admin'  # can do anything with the printer
'''admin role - used in models to designate that one object can manage the other'''
ROLE_USER = 'user'    # can print
'''regular user role - used in models to designate that one object can use but not modify the other'''

ROLES = (
    (ROLE_ADMIN, ROLE_ADMIN),
    (ROLE_USER, ROLE_USER),
)
'''List of possible choices for role in relationship (in models and API)'''
