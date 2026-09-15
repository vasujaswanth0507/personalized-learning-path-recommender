# Testing & Verification Guide: LearnPath

This document outlines the testing strategy, automated test commands, and manual smoke-testing flows to verify the LearnPath platform.

## 1. Automated Testing

LearnPath features a comprehensive FastAPI backend test suite built using `pytest`. The test client uses an in-memory SQLite database, isolating tests from local learner data.

### 1.1 Running backend tests
To run all tests in the backend, execute the following command:
```bash
cd backend
python -m pytest tests -v
```

### 1.2 Test Cases Overview
The test suite consists of 12 test items:
1. `test_adaptive_feedback_inserts_refresher`: Confirms that marking a stage as difficult inserts prerequisite refresher recommendations.
2. `test_adaptive_assessment_failure_inserts_remedial`: Validates that failing a quiz (score < 70%) triggers automatic insertion of a fundamental remedial stage.
3. `test_api_health`: Verifies general backend health-check response.
4. `test_onboarding_turn`: Asserts conversational onboarding response formats and profile extraction.
5. `test_create_profile_and_get_dashboard`: Tests profile creation and dashboard generation flows.
6. `test_reset_endpoint`: Confirms the development database reset endpoint cleans up learner data correctly.
7. `test_case_1_ui_ux_goal`: Validates that goals stating UI/UX are accurately mapped to the `UI/UX Design` direction.
8. `test_case_2_cloud_engineer_with_prior_skills`: Asserts that declaring a Cloud goal and prior skills credits the learner and asks relevant dependent topics (like networking).
9. `test_case_3_exploring_undecided`: Confirms that an undecided learner message is met with exploring options rather than a rigid track assignment.
10. `test_case_4_prior_html_css_credited`: Tests that prior known skills are credited and marked as skipped in roadmaps.
11. `test_ui_ux_roadmap_creation`: Verifies UI/UX paths generate appropriate User Research and Figma stages.
12. `test_recommendation_prerequisite_skipping`: Confirms topological sorting handles skipping prior skills in DAGs.

---

## 2. Manual Smoke-Testing Guidelines

To perform a complete manual verification of the workspace in the browser, follow this script:

### A. Fresh Startup & Theme
1. Delete the local SQLite database file (`backend/learnpath.db`) or run POST `/api/profile/reset` to reset.
2. Open `http://localhost:5173/` in a browser.
3. Verify the **LearnPath startup animation** displays and completes in under 1.5 seconds.
4. Click the theme toggle icon in the header (Sun/Moon) and confirm the UI changes instantly between Dark and Light mode. Refresh the page to verify theme persistence.

### B. Onboarding Chat Flow
1. Verify the onboarding screen displays a wide conversation layout.
2. Send: `"I want to learn UI and UX."`
3. Verify the Mentor replies with introductory Figma question and suggestion chips.
4. Send: `"Starting from ground zero."`
5. Verify the Mentor asks about study time.
6. Send: `"1 hour a day."`
7. Verify the "Your personalized path is ready" banner appears with a **Generate Roadmap** button.
8. Refresh the page. Confirm the message history is restored correctly with no duplicate bubbles.

### C. Roadmap & Dynamic Path Adaptation
1. Click **Generate Roadmap**. Confirm redirection to the Overview page.
2. Navigate to **My Roadmap**. Confirm User Research and Figma are available, but later stages are locked.
3. Complete a resource and mark it as "Difficult". Navigate back to the roadmap and check why it is recommended.
4. Go to **Skill Assessments**, take the first quiz, and select wrong answers to fail. Verify that a new **Remedial Refresher Stage** is immediately injected into the roadmap timeline.

### D. Danger Zone Deletion
1. Navigate to **Profile**.
2. Scroll to the **Danger Zone** section.
3. Click **Delete Profile** and click cancel, then confirm deletion in the modal.
4. Verify the application automatically returns to the onboarding welcome screen.
5. Inspect the backend SQLite database to verify all learner-specific records are completely deleted and reference tables (resources, projects, assessments) remain intact.
