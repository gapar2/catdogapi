import unittest
import index
import mock

# we use the smallest possible PNG b64-encoded for test
test_event = {
    "base64Image": "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEW10NBjBBbqAAAAH0lEQVRoge3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAvg0hAAABmmDh1QAAAABJRU5ErkJggg==",
    "headers": {"x-api-key": "test_api_key"}
}

class TestHandlerCase(unittest.TestCase):
    
    @mock.patch('index.increment_user_count')
    @mock.patch('index.get_user_name')
    @mock.patch('index.send_message')
    @mock.patch('index.cat_or_dog')
    def test_response(self, cat_or_dog_mock, send_message,
                      get_user_name_mock, increment_user_count_mock):
        
        # We setup the user_name mock to return 'test user'
        get_user_name_mock.return_value = 'test_user'
        
        # We setup the mock to return dog
        cat_or_dog_mock.return_value = 'dog'
        
        print("testing response.")
        result = index.handler(test_event, None)
        print(result)
        self.assertEqual(result['statusCode'], 200)


if __name__ == '__main__':
    unittest.main()
