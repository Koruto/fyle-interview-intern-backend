def test_server_running(client):
        response = client.get('/')

        assert response.status_code == 200


def test_invalid_route(client):

    response = client.get('/nonexistent_route')

    assert response.status_code == 404
    
    error_response = response.json["error"]
    assert error_response == "NotFound"


def test_get_student_assignments_unauthorized_access(client):
    """
    failure case: accessing student assignments without proper headers
    """
    response = client.get('/student/assignments')

    assert response.status_code == 401


