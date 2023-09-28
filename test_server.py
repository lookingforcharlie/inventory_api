import requests

# print(requests.get('http://127.0.0.1:8000').json())

# print(requests.get('http://127.0.0.1:8000/items/1').json())

# print(requests.get('http://127.0.0.1:8000/items?name=Nails').json())


# response = requests.get('http://127.0.0.1:8000/items?name=Nails')
# try:
#     response.raise_for_status()
#     print(response.json())
# except requests.exceptions.HTTPError as http_err:
#     print(f'HTTP error occurred: {http_err}')
# except requests.exceptions.JSONDecodeError as json_err:
#     print(f'JSON decoding error occurred: {json_err}')
#     print(response.text)  # Print the response content for debugging
# except Exception as err:
#     print(f'An error occurred: {err}')


print()
print('Adding an item:')
print(
    requests.post(
        'http://127.0.0.1:8000',
        json={
            "name": "Screwdriver",
            "price": 3.99,
            "count": 10,
            "id": 0,
            "category": 'tools'
        },
    ).json()
)

print(requests.get("http://127.0.0.1:8000/").json())
print()

# print("Updating an item:")
# print(requests.put("http://127.0.0.1:8000/update/0?count=9001").json())
# print(requests.get("http://127.0.0.1:8000/").json())
# print()

# print("Deleting an item:")
# print(requests.delete("http://127.0.0.1:8000/delete/0").json())
# print(requests.get("http://127.0.0.1:8000/").json())
