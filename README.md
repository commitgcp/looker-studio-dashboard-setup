# GCP Billing Dashboard Automation


Overview

This project is designed to automate the setup of exporting GCP billing data to a BigQuery dataset and subsequently creating a Looker Studio dashboard to visualize this data. The application is packaged as a Docker container and deployed as a Cloud Run service on Google Cloud Platform (GCP). If granted access by an administrator, you can browse to the app at: 34.49.84.56.sslip.io


Key Components

    app.py: The main Streamlit application script. It provides a web interface for users to input their GCP project details, billing account, identity type, and email. The app then automates the setup of billing data export to BigQuery and initiates the creation of a Looker Studio dashboard.

    helperfunctions.py: Contains utility functions to interact with Google Cloud Datastore for retrieving billing account names and IDs.

    cloudbuild.yaml: Configuration for Google Cloud Build to automate the building and deployment of the Docker container to Cloud Run.

    Dockerfile: Instructions for building the Docker container image, including setting up the Python environment and specifying the entry point for the Streamlit application.
    
    requirements.txt: Lists all Python dependencies required by the application.


Pre-requisites

    Google Cloud Platform account with billing enabled.
    Google Cloud SDK (gcloud) installed and configured for command-line access.
    Access to Google Cloud services such as BigQuery, Cloud Datastore, IAM, and Service Usage APIs.
    Docker installed for local testing and building of the container image.


Setup Instructions

Google Cloud Project Setup

    Run the following command from project root directory:

    gcloud builds submit --region=me-west1 --config cloudbuild.yaml

    Then redeploy the Cloud Run service with the new image.

    The Cloud Run service runs on GCP project commit-automation - if you don't have access, then please ask the GCP team.

Local Development

    Clone the repository to your local machine.
    Install Python dependencies:

        pip3 install -r requirements.txt

    Run the Streamlit app locally for testing:

        python3 -m streamlit run app.py


Deploying to Cloud Run

    Use Cloud Build to build the Docker container and push it to Google Container Registry:
    
    gcloud builds submit --region=me-west1 --config cloudbuild.yaml

    Modify cloudbuild.yaml as needed for your registry's details.
    Deploy the container image to Cloud Run via the Google Cloud Console or the gcloud command-line tool. The Cloud Run service sits on project commit-automation, please ask the Commit GCP team for access if you do not have.
