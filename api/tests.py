import pytest
from unittest.mock import Mock, patch
from server import create_post, get_user

@patch('server.firestore.client')
def test_create_post(mock_firestore_client):
    # Mock the return value of firestore.client().collection().document().set()
    mock_firestore_client.return_value.collection.return_value.document.return_value.set.return_value = None

    # Call the function with a test post data
    post_data = {
        "id": 1,
        "uid": 1,
        "title": "Test Title",
        "content": "Test Content",
        "comments": [],
    }
    create_post(1, post_data)

    # Assert that firestore.client().collection().document().set() was called with the test post data
    mock_firestore_client.return_value.collection.return_value.document.return_value.set.assert_called_once_with(post_data)