# Project: Google Docs Contribution Evaluator

## Overview

This project is designed to monitor changes in a Google Docs document, evaluate the contributions made to the document, and provide detailed feedback on the relevance of these contributions based on a predefined task description. It leverages Google APIs, natural language processing, and text similarity measures to achieve this functionality.

The primary goal of this project is to connect with the [GAME (Goals And Motivation Engine)](https://github.com/fvergaracl/GAME). GAME is a system designed to foster motivation and achievement of goals through gamification. This open-source project utilizes a PostgreSQL database and is developed with FastAPI in Python, managed via Poetry for environment handling. However, this project can be adapted for different purposes beyond gamification.

## Installation and Setup

### Prerequisites

- Python 3.x
- Poetry for package management

### Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required Python packages using Poetry:

   ```bash
   poetry install
   ```

3. Set up environment variables. Create a `.env` file in the project root and add the following variables:

   ```env
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   GOOGLE_PROJECT_ID=<your-google-project-id>
   GOOGLE_DOCUMENT_ID=<your-google-document-id>

   # TOPIC_COLOR
   TOPIC_COLOR_RED=0.05882353
   TOPIC_COLOR_GREEN=1
   TOPIC_COLOR_BLUE=0.05882353

   # DESCRIPTION_COLOR
   DESCRIPTION_COLOR_RED=0.3019608
   DESCRIPTION_COLOR_GREEN=0.9137255
   DESCRIPTION_COLOR_BLUE=0.9411765

   # ANSWER_COLOR
   ANSWER_COLOR_RED=1
   ANSWER_COLOR_GREEN=1
   ANSWER_COLOR_BLUE=0.47058824
   ```

4. Run the main script:
   ```bash
   clear && poetry run python main.py
   ```

## Usage

The application monitors changes in the specified Google Docs document and evaluates the contributions made based on their relevance to a predefined task description. The results are printed to the console, showing the relevance score for each contribution.

## Contributing

If you wish to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear messages.
4. Push your changes to your fork.
5. Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

This project uses the following libraries and APIs:

- [Google APIs](https://developers.google.com/docs/api)
- [spaCy](https://spacy.io/)
- [scikit-learn](https://scikit-learn.org/)
- [dotenv](https://github.com/theskumar/python-dotenv)
- [colorama](https://pypi.org/project/colorama/)

For more information, please refer to the official documentation of these libraries and APIs.
