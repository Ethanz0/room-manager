import random

test_bookings: [] = [
    {
        "booking_id": 1,
        "room_id": 1,
        "user_id": 1,
        "start_time": "2024-10-01T10:00:00",
        "end_time": "2024-10-01T11:00:00",
    },
    {
        "booking_id": 2,
        "room_id": 1,
        "user_id": 2,
        "start_time": "2024-10-01T12:00:00",
        "end_time": "2024-10-01T13:00:00",
    },
    {
        "booking_id": 3,
        "room_id": 1,
        "user_id": 3,
        "start_time": "2024-10-01T14:00:00",
        "end_time": "2024-10-01T15:00:00",
    },
]

random_test_bookings: [] = [
    {
        "booking_id": random.randint(1, 100),
        "room_id": random.randint(1, 10),
        "user_id": random.randint(1, 10),
        "start_time": "2024-10-01T14:00:00",
        "end_time": "2024-10-01T15:00:00",
    },
    {
        "booking_id": random.randint(1, 100),
        "room_id": random.randint(1, 10),
        "user_id": random.randint(1, 10),
        "start_time": "2024-10-01T14:00:00",
        "end_time": "2024-10-01T15:00:00",
    },
    {
        "booking_id": random.randint(1, 100),
        "room_id": random.randint(1, 10),
        "user_id": random.randint(1, 10),
        "start_time": "2024-10-01T14:00:00",
        "end_time": "2024-10-01T15:00:00",
    },
]
