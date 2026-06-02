import unittest
from app import app

class SeminarRoomAPITest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # ======================
    # Health Check
    # ======================

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["status"],
            "ok"
        )

    # ======================
    # Room
    # ======================

    def test_create_room(self):

        room_data = {
            "name": "세미나실 A",
            "capacity": 20,
            "equipment": "빔프로젝터, 화이트보드"
        }

        response = self.client.post(
            "/api/rooms",
            json=room_data
        )

        self.assertEqual(response.status_code, 201)

        self.room_id = response.json["id"]

        self.assertEqual(
            response.json["message"],
            "created"
        )

    def test_get_rooms(self):

        response = self.client.get("/api/rooms")

        self.assertEqual(response.status_code, 200)

        self.assertIn("items", response.json)
        self.assertIn("count", response.json)

    def test_room_crud(self):

        # 생성
        create_response = self.client.post(
            "/api/rooms",
            json={
                "name": "세미나실 B",
                "capacity": 30,
                "equipment": "TV"
            }
        )

        room_id = create_response.json["id"]

        # 조회
        get_response = self.client.get(
            f"/api/rooms/{room_id}"
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(
            get_response.json["name"],
            "세미나실 B"
        )

        # 수정
        update_response = self.client.put(
            f"/api/rooms/{room_id}",
            json={
                "name": "세미나실 B 수정",
                "capacity": 40,
                "equipment": "TV, 화이트보드"
            }
        )

        self.assertEqual(update_response.status_code, 200)

        # 재조회
        get_response = self.client.get(
            f"/api/rooms/{room_id}"
        )

        self.assertEqual(
            get_response.json["name"],
            "세미나실 B 수정"
        )

        # 삭제
        delete_response = self.client.delete(
            f"/api/rooms/{room_id}"
        )

        self.assertEqual(delete_response.status_code, 200)

    # ======================
    # Reservation
    # ======================

    def test_reservation_flow(self):

        # Room 생성
        room_response = self.client.post(
            "/api/rooms",
            json={
                "name": "예약용 회의실",
                "capacity": 10,
                "equipment": "Monitor"
            }
        )

        room_id = room_response.json["id"]

        # 예약 생성
        reservation_response = self.client.post(
            "/api/reservations",
            json={
                "room_id": room_id,
                "user_name": "홍길동",
                "user_email": "hong@example.com",
                "date": "2026-06-03",
                "start_time": "09:00",
                "end_time": "10:00",
                "purpose": "프로젝트 회의"
            }
        )

        self.assertEqual(
            reservation_response.status_code,
            201
        )

        reservation_id = reservation_response.json["id"]

        # 예약 조회
        list_response = self.client.get(
            f"/api/reservations?room_id={room_id}&date=2026-06-03"
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(
            list_response.json["count"],
            1
        )

        # 예약 취소
        delete_response = self.client.delete(
            f"/api/reservations/{reservation_id}"
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(
            delete_response.json["message"],
            "cancelled"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)