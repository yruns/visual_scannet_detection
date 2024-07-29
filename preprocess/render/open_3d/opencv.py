import os
import requests

API_KEY = 'wx1pxqifjt4uxy2ru'
IMAGE_FILE_PATH = '/Users/yruns/Downloads/view_3.png'

def main():
    assert os.path.exists(IMAGE_FILE_PATH), f'Error: File({IMAGE_FILE_PATH}) does not exist.'

    headers = {'X-API-KEY': API_KEY}
    data = {'sync': '1'}
    files = {'image_file': open(IMAGE_FILE_PATH, 'rb')}
    url = 'https://techsz.aoscdn.com/api/tasks/visual/scale'

    # Create a task
    response = requests.post(url, headers=headers, data=data, files=files)

    response_json = response.json()
    if 'status' in response_json and response_json['status'] == 200:
        result_tag = 'failed'
        if 'data' in response_json:
            response_json_data = response_json['data']
            if 'state' in response_json_data:
                task_state = response_json_data['state']
                # task success
                if task_state == 1:
                    result_tag = 'successful'
                    # save image
                    image_url = response_json_data['image']

                    response = requests.get(image_url)

                    with open('views/output.png', 'wb') as f:
                        f.write(response.content)

                elif task_state < 0:
                    # request failed, log the details
                    pass
                else:
                    # Task processing, abnormal situation, seeking assistance from customer service of picwish
                    pass
        print(f'Result({result_tag}): {response_json}')
        print(response_json)



    else:
        # request failed, log the details
        print(f'Error: Failed to get the result,{response.text}')

if __name__ == "__main__":
    main()