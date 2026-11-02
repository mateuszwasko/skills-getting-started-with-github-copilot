REQUIRED_FIELDS = {"description", "schedule", "max_participants", "participants"}


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestGetActivities:
    def test_returns_activities_dict(self, client):
        # Arrange
        expected_names = {"Chess Club", "Programming Class", "Gym Class"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_names.issubset(response.json().keys())

    def test_each_activity_has_required_fields(self, client):
        # Arrange
        # (default seeded data)

        # Act
        response = client.get("/activities")

        # Assert
        for name, details in response.json().items():
            assert REQUIRED_FIELDS.issubset(details.keys()), name
            assert isinstance(details["participants"], list)


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity, email = "Chess Club", "new.student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity}"}
        participants = client.get("/activities").json()[activity]["participants"]
        assert email in participants

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        activity, email = "Underwater Basket Weaving", "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_without_email_returns_422(self, client):
        # Arrange
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup")

        # Assert
        assert response.status_code == 422

    def test_signup_does_not_affect_other_activities(self, client):
        # Arrange
        activity, other = "Chess Club", "Gym Class"
        email = "isolated@mergington.edu"
        before = client.get("/activities").json()[other]["participants"].copy()

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        after = client.get("/activities").json()[other]["participants"]
        assert after == before

    def test_duplicate_signup_returns_400(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # already registered in seed data

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        participants = client.get("/activities").json()[activity]["participants"]
        assert participants.count(email) == 1
