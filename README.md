## Project Overview: Event Networking Platform

This is a robust web application designed to facilitate event management and participation, connecting event organizers with attendees. It provides a comprehensive suite of features for creating, managing, and attending various events, fostering communication, and tracking engagement.

**A-Z Content, Workability, Flow, and Features:**

**1. Core Functionality & User Types:**
The platform supports two primary user roles:
*   **Organizers:** Individuals or entities responsible for creating, managing, and hosting events.
*   **Participants:** Individuals who register for and attend events.

**2. User Management & Profiles:**
*   **User Authentication:** Secure registration and login system.
*   **User Profiles (`User` Model):** Each user has a profile including:
    *   Username, email, and password (standard Django `AbstractUser` fields).
    *   **User Type:** Clearly defined as 'organizer' or 'participant'.
    *   **Contact Information:** Phone number.
    *   **Personal Bio:** A text field for self-description.
    *   **Profile Picture:** Customizable profile image.
    *   **Areas of Interest:** Participants can specify categories of events they are interested in, enabling personalized recommendations or filtering.
*   **Profile Management:** Users can view and update their profile information.
*   **CV Generation:** Participants can generate a CV, likely incorporating their profile details and event participation history.

**3. Event Management (`Event` Model):**
*   **Event Creation:** Organizers can create new events with detailed information:
    *   **Title & Description:** Comprehensive details about the event.
    *   **Organizer:** Linked to the creating organizer.
    *   **Category (`Category` Model):** Events are categorized (e.g., "Technical Workshop," "Networking Mixer") for better organization and discoverability.
    *   **Date & Time:** Specific start date and time, along with a duration.
    *   **Location:** Where the event will take place.
    *   **Max Participants:** Limit on the number of attendees.
    *   **Registration Link:** An external URL (e.g., Google Form) for registration, allowing for flexible registration processes.
    *   **Event Poster:** An image to visually represent the event.
    *   **Dynamic Fields (`CustomField` Model):** Organizers can define custom fields (text, number, file, email, URL) for event registration forms, allowing for collection of specific information from participants beyond standard fields.
*   **Event Status:** Events automatically display as 'upcoming', 'ongoing', or 'completed' based on their date and time.
*   **Event Listing & Details:**
    *   Participants can browse a list of all events.
    *   Events can be filtered by category.
    *   Detailed event pages provide all relevant information.
*   **Organizer Dashboard:** Organizers have a dedicated dashboard to view and manage all events they have created.
*   **Event Actions:** Organizers can edit and delete their events.

**4. Event Registration & Participation (`Registration` Model):**
*   **Seamless Registration:** Participants can register for events.
*   **Unique Registration:** Ensures a participant can only register for a specific event once.
*   **Registration Tracking:** Records when a participant registered.
*   **Attendance Tracking:** Organizers can mark participants as 'attended'.
*   **Dynamic Responses:** Stores additional information collected through custom fields during registration using a JSON field.
*   **Uploaded Files:** Supports file uploads during registration (e.g., for resumes, portfolios).
*   **Cancellation:** Participants can cancel their event registrations.
*   **Participant Details:** Organizers can view details of individual participants who registered for their events.

**5. Communication & Engagement:**
*   **Internal Messaging System (`Message` Model):**
    *   Users can send private messages to each other.
    *   Features an inbox for received messages.
    *   Tracks read/unread status of messages.
*   **Event Feedback (`EventFeedback` Model):**
    *   Participants can provide feedback and ratings (1-5 stars) for events they attended.
    *   Includes a comment section for detailed feedback.
*   **Event Suggestions (`EventSuggestion` Model):n    *   Participants can submit suggestions related to specific events.

**6. Certificates (`Certificate` Model):**
*   **Certificate Upload:** Users (likely participants) can upload certificates (e.g., participation, achievement).
*   **Certificate Categorization:** Certificates can be categorized as 'technical' or 'non_technical'.
*   **Association with Events:** Certificates can be linked to specific events.
*   **Certificate Management:** Users can delete their uploaded certificates.

**Technical Stack Summary:**

*   **Frontend:** HTML templates, Bootstrap (CSS), Custom CSS, JavaScript (for client-side interactivity).
*   **Backend:** Python, Django Framework.
*   **Database:** SQLite (default for development; easily migratable to PostgreSQL/MySQL for production).
*   **APIs / Services:** The application is a traditional server-rendered web application. It does not expose a separate RESTful API for external consumption. All interactions are handled through standard web requests to Django views.
*   **Deployment:** Not specified in project files.

**9. Workability & Flow Summary:**
The application provides a clear and intuitive flow for both organizers and participants. Organizers can efficiently set up and manage events, track registrations, and gather feedback. Participants can easily discover, register for, and engage with events, manage their profiles, and communicate with others. The system is designed to streamline the event networking process from creation to post-event engagement.