from concurrent.futures import ThreadPoolExecutor
import requests

BASE_URL = "http://localhost:5000"
ORDER_ID = 1  # a supply order that is still Pending


def deliver(i):
    url = BASE_URL + "/api/warehouse/deliveries/" + str(ORDER_ID) + "/deliver"
    return requests.patch(url).status_code


# Fire 10 delivery requests for the same order at the same moment
with ThreadPoolExecutor(max_workers=10) as pool:
    codes = list(pool.map(deliver, range(10)))

print("delivered:", codes.count(200))
print("refused:  ", codes.count(400))
print("errors:   ", [c for c in codes if c not in (200, 400)])