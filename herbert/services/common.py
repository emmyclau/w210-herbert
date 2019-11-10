from random import sample


def common_herbs(n=5):
    common_herbs_list = [
        'Ginger', 'Ginseng', 'Turmeric', 'Astragalus', 'Cinnamon'
    ]
    return sample(common_herbs_list, n)


def common_conditions(n=4):
    common_conditions_list = [
        'Headache', 'Sleep Problem', 'Stomach Ache', 'Weight Loss'
    ]
    return sample(common_conditions_list, n)


def get_team():
    team = [{
        'name': 'Emmy Lau',
        'role': 'Product Manager',
        'email': 'test@test.com',
        'image': 'female.jpg'
    }, {
        'name': 'Ian Bettinger',
        'role': 'Product Manager',
        'email': 'test@test.com',
        'image': 'male.png'
    }, {
        'name': 'Gurdit Chahal',
        'role': 'Product Manager',
        'email': 'test@test.com',
        'image': 'male.png'
    }, {
        'name': 'Karl Siil',
        'role': 'Product Manager',
        'email': 'karliansiil@berkeley.com',
        'image': 'karl.jpg'
    }]

    return team