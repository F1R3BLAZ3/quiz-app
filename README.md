# Quiz Application

This project is a backend-focused quiz application built with Flask, designed to manage user authentication, quiz question management, and scoring. It includes random question selection, result tracking, and admin capabilities for adding and viewing questions. It includes a basic Bootstrap implementation for a better viewing experience.

## Table of Contents
- [Project Structure](#project-structure)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Available Scripts](#available-scripts)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

```plaintext
quiz_app/
│
├── app/
│   ├── __init__.py                # Initializes the Flask app, database, and login manager
│   ├── models.py                  # Database models (User, QuizQuestion, QuizResult, etc.)
│   ├── forms.py                   # Form classes for login, registration, and questions
│   ├── routes.py                  # Route handlers for different endpoints (home, registration, login, dashboard, quiz, results, logout)
│   ├── services/                  # Services for business logic
│   │   └── quiz_service.py        # Logic for random question selection and timer management
│   ├── static/                    # Static files (CSS, JavaScript, images)
│   └── templates/                 # HTML templates for rendering views
│       ├── add_question.html      # Template for adding quiz questions
│       ├── home.html              # Homepage template
│       ├── login.html             # Login template
│       ├── register.html          # Registration template
│       ├── dashboard.html         # User dashboard template
│       ├── base.html              # Base template
│       ├── edit_question.html     # Template for editing quiz questions
│       ├── quiz.html              # Quiz interface template
│       ├── results_history.html   # Results history template
│       ├── results.html           # Quiz results template
│       └── view_questions.html    # Template for displaying questions
│
├── migrations/                    # Database migration files
│
├── instance/                      # Database instances
│   └── site.db                    # Active database file
│
├── requirements.txt               # List of package dependencies
│
├── .env                           # Environment variables
│
├── README.md                      # README file for the project
│
├── config.py                      # Configuration settings (e.g., database URL, secret keys)
│
└── run.py                         # Entry point to run the Flask app
```

## Features

- **User Authentication**: Users can register, log in, and log out securely.
- **Quiz Functionality**: Users can attempt a quiz with randomly selected questions.
- **Scoring and Results**: Scores are calculated and displayed after quiz submission.
- **Admin Capabilities**: Admins can add, edit, and view quiz questions.
- **Database Management**: Uses SQLAlchemy for data modeling and Alembic for migrations.

## Prerequisites

- Python 3.8 or higher
- Flask and other dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/quiz-app.git
   cd quiz-app
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables:

      Create a .env file in the root directory.

      Add your configuration variables, such as:
      ```bash
      FLASK_APP=run.py
      FLASK_ENV=development
      SECRET_KEY=your_secret_key
      ```

6. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

## Usage

1. Run the application: You can start the application using either of the following commands:

   ```bash
   flask run
   ```

or

   ```bash
   python3 run.py
   ```

2. Access the app: Open http://127.0.0.1:5000 in your web browser.

3. User Actions:

Register or log in to start a quiz.
Access the quiz dashboard for quiz options and history.
View, add, and edit questions (admin or authorized users only).

## Available Scripts

```markdown
- **Run Application**: Starts the development server.
```
```bash
flask run
```

or

```bash
python3 run.py
```

- Database Migration:

  1.Initialize:
    ```bash
    flask db init
    ```
  2.Migrate:
    ```bash
    flask db migrate -m "Migration message"
    ```
  3.Upgrade:
    ```bash
    flask db upgrade
    ```
  4.Downgrade:
    ```bash
    flask db downgrade
    ```


## Contributing

```markdown
Contributions are welcome! Please fork this repository and create a pull request with your changes.
```

## License

This project is licensed under the MIT License.
