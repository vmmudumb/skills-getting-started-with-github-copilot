"""
FastAPI Backend Tests using AAA (Arrange-Act-Assert) Pattern

Tests for the Mergington High School API endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
"""


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 OK status"""
        # Arrange
        # (No setup needed - using default activities from fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities"""
        # Arrange
        # (No setup needed - using default activities from fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert len(data) == 13  # 13 activities in the initial database
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that each activity has the required fields"""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert set(activity_data.keys()) == expected_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_specific_activity(self, client):
        """Test that specific known activities are present"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Soccer Team"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_has_initial_participants(self, client):
        """Test that activities have initial participants"""
        # Arrange
        # (No setup needed - using default activities from fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup to an activity"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"
    
    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds the student to participants list"""
        # Arrange
        activity_name = "Programming Class"
        student_email = "teststudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email in activities_data[activity_name]["participants"]
    
    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns 400 error"""
        # Arrange
        activity_name = "Soccer Team"
        student_email = "duplicate@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act - Try to signup again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up to non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_with_already_registered_student(self, client):
        """Test that existing participant cannot sign up again"""
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test multiple students can sign up to the same activity"""
        # Arrange
        activity_name = "Art Studio"
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_data = client.get("/activities").json()
        participants = activities_data[activity_name]["participants"]
        assert student1 in participants
        assert student2 in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "newstudent@mergington.edu"
        
        # First sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {student_email} from {activity_name}"
    
    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister actually removes the student from participants list"""
        # Arrange
        activity_name = "Programming Class"
        student_email = "teststudent@mergington.edu"
        
        # Sign up the student first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email not in activities_data[activity_name]["participants"]
    
    def test_unregister_non_registered_student_returns_400(self, client):
        """Test that unregistering a non-registered student returns 400"""
        # Arrange
        activity_name = "Soccer Team"
        student_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant from initial data"""
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already in Chess Club from initial data
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify removal
        activities_data = client.get("/activities").json()
        assert existing_student not in activities_data[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests that combine multiple operations"""
    
    def test_signup_and_verify_in_activities_list(self, client):
        """Test complete flow: signup → get activities → verify participant"""
        # Arrange
        activity_name = "Theater Club"
        student_email = "newactor@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act - Get activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert student_email in activities_data[activity_name]["participants"]
    
    def test_signup_unregister_cycle(self, client):
        """Test complete cycle: signup → unregister → verify removal"""
        # Arrange
        activity_name = "Debate Team"
        student_email = "debater@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Act - Get activities to verify
        activities_data = client.get("/activities").json()
        
        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        assert student_email not in activities_data[activity_name]["participants"]
    
    def test_student_signup_to_multiple_activities(self, client):
        """Test that a student can sign up to multiple different activities"""
        # Arrange
        student_email = "multi@mergington.edu"
        activities_to_join = ["Basketball Team", "Music Band", "Photography Club"]
        
        # Act - Sign up to multiple activities
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200
        
        # Assert - Verify student is in all activities
        activities_data = client.get("/activities").json()
        for activity in activities_to_join:
            assert student_email in activities_data[activity]["participants"]
    
    def test_multiple_students_signup_to_same_activity(self, client):
        """Test that multiple students can join the same activity"""
        # Arrange
        activity_name = "Science Olympiad"
        students = [
            "scientist1@mergington.edu",
            "scientist2@mergington.edu",
            "scientist3@mergington.edu"
        ]
        
        # Act - Multiple students sign up
        for student in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Assert - All students are in the activity
        activities_data = client.get("/activities").json()
        participants = activities_data[activity_name]["participants"]
        for student in students:
            assert student in participants
    
    def test_activity_participant_count_changes(self, client):
        """Test that participant count changes correctly with signup/unregister"""
        # Arrange
        activity_name = "Swimming Club"
        student_email = "swimmer@mergington.edu"
        
        # Get initial count
        initial_data = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Act - Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        after_signup_data = client.get("/activities").json()
        after_signup_count = len(after_signup_data[activity_name]["participants"])
        
        # Act - Unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        after_unregister_data = client.get("/activities").json()
        after_unregister_count = len(after_unregister_data[activity_name]["participants"])
        
        # Assert
        assert after_signup_count == initial_count + 1
        assert after_unregister_count == initial_count
