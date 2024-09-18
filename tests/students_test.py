def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_missing_content(client, h_student_1):
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={  
            'not_content': 'not_value'
        })
    
    assert response.status_code == 400
    error_response = response.json
    assert error_response['message'] == 'Assignment content cannot be empty'


def test_post_assignment_null_content(client, h_student_1):
    """
    failure case: content cannot be null
    """

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })

    assert response.status_code == 400


def test_edit_assignment_student_1(client, h_student_1):
    test_content = "Testing 123..."

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': 2,
            'content': test_content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == test_content


def test_edit_submitted_assignment_student_2(client, h_student_2):
    test_content = "Testing ABC..."

    response = client.post(
        '/student/assignments',
        headers=h_student_2,
        json={
            'id': 3,
            'content': test_content
        })

    assert response.status_code == 400


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_submit_assignment_student_1(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


def test_assignment_resubmit_error(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'


def test_submit_non_existent_assignment(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 9999,
            'teacher_id': 2
        })
    
    assert response.status_code == 404
    error_response = response.json
    assert error_response['message'] == 'Assignment with the provided ID does not exist'


def test_submit_assignment_unauthorized_teacher(client, h_teacher_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_teacher_1, 
        json={
            'id': 2,
            'teacher_id': 2
        })
    
    assert response.status_code == 403
    error_response = response.json
    assert error_response['error'] == 'FyleError'

