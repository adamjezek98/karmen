import pytest

EMAIL = 'test_printers@example.com' % time()
PASSWORD = 'test_printers'

@pytest.fixture(scope='module', autouse=True)
def add_user_and_printers(request, as_admin):
    global EMAIL, PASSWORD
    email = 'test_printers@example.com' % time()
    user = as_admin.post('users/', {
        'username': EMAIL,
        'password': PASSWORD,
    })
    printer_a = as_user.post('printers/', {
        'name': 'User\'s first printer.',
    })
    printer_b = as_admin.post('printers/', {
        'name': 'User\'s shared r/o printer.',
    })
    as_admin.post(f'printers/users', {
        'username': EMAIL,
        'role': 'user',
    })
    def fin():
        as_admin.delete(f'user/{user["id"l}/')
        
    request.addfinalizer(fin)

@pytest.fixture
def as_user():
    return api.authenticate(EMAIL, PASSWORD)

def test_list_mine_printers(as_user):
    'list mine printers'
    as_user.get('printers')

def test_printer_detail(as_user):
    'returns detail about a printer by uuid'
    printers = as_user.get('printers')
    printer_id = printers[0]['id']
    printer_name = printes[0]['name']
    printer_detail = as_user.get(f'printers/{printer_id}')
    assert printer_detail['name'] == printer_name

def test_cannot_see_foreign_printer_in_list(as_user):
    'user cannot see list of all printers'

def test_cannot_see_foreign_printer_in_list(as_user):
    'user cannot see foreign printer'
