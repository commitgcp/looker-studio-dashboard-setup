import streamlit as st
from google.cloud import bigquery, billing, iam
from google.cloud import service_usage_v1
from google.api_core.exceptions import NotFound, PermissionDenied
import subprocess
import os
import time
from helperfunctions import *
from googleapiclient.discovery import build


# Initialize the Service Usage client
serviceclient = service_usage_v1.ServiceUsageClient()
bigquery_dataset_id = 'billing_export'

# Function to set up GCP Project in gcloud CLI
def set_gcloud_project(project_id):
    # Set environment variables
    os.environ["GCLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = project_id

    # Save project_id in Streamlit's session state for persistence
    st.session_state.project_id = project_id

def enable_service(service_name, project_id):
    # Construct the full service name
    service_name_full = f"projects/{project_id}/services/{service_name}"

    # Attempt to enable the service
    try:
        request = service_usage_v1.EnableServiceRequest(
            name=service_name_full
        )
        operation = serviceclient.enable_service(request=request)

        # Wait for the operation to complete
        response = operation.result()

        # Check the response for success or failure
        if operation.done:
            print(f"Service {service_name} enabled successfully in project {project_id}")
        else:
            print(f"Failed to enable service {service_name} in project {project_id}")
    except NotFound:
        print(f"The service {service_name} not found for project {project_id}")
    except PermissionDenied:
        print(f"Permission denied to enable service {service_name} in project {project_id}. Ensure the Service Usage API is enabled and the correct permissions are granted.")
    except Exception as e:
        print(f"An error occurred while enabling service {service_name}: {e}")

# Function to create BigQuery dataset
def create_bq_dataset(project_id, location='EU', dataset_id=bigquery_dataset_id):
    client = bigquery.Client(project=project_id)
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = location
    dataset = client.create_dataset(dataset, exists_ok=True)

def check_bq_dataset_tables(project_id, dataset_id=bigquery_dataset_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id, project=project_id)

    try:
        tables = list(client.list_tables(dataset_ref))  # List all tables in the dataset
        if len(tables) == 2:  # Check that both tables have been created
            return True
        else:  # If the list is empty, there are no tables in the dataset
            return False
    except Exception as e:
        print(f"An error occurred while checking for tables in the dataset: {e}")
        return False

# Function to check BigQuery dataset existence
def check_bq_dataset(project_id, dataset_id=bigquery_dataset_id):
    client = bigquery.Client(project=project_id)
    try:
        client.get_dataset(f"{project_id}.{dataset_id}")
        return True
    except Exception as e:
        return False

def run_app():
    st.set_page_config(page_title="Billboard Creation App", page_icon=":robot_face:")
    st.sidebar.image("./images/logo.png")
    st.sidebar.markdown(
        """
        <a style='display: block; text-align: center;' href="https://www.comm-it.com/">Made with :heart: by Commit</a>
        """,
        unsafe_allow_html=True,
    )

    if "to_clear" not in st.session_state:
        st.session_state.to_clear = False

    if st.session_state and st.session_state.to_clear:
        if st.session_state.to_clear:
            st.session_state.clear()

    if "manual_step_completed" not in st.session_state:
        st.session_state.manual_step_completed = False  # New session state variable to track manual step completion

    st.title('GCP Billing Dashboard Setup')
    st.write('Note: the project and the billing account that you provide below must be connected.')

    if "project_id" not in st.session_state:
        st.session_state.project_id = None
    if "billing_id" not in st.session_state:
        st.session_state.billing_id = None
    if "identity_type" not in st.session_state:
        st.session_state.identity_type = None
    if "identity_email" not in st.session_state:
        st.session_state.identity_email = None

    project_id = st.text_input('Enter your GCP Project ID')
    st.session_state.project_id = project_id
    billing_accounts = get_billingaccount_names()
    selected_account = st.selectbox('Select Billing Account:', billing_accounts, key='billing_accounts')
    billing_id = get_billingaccount_id(selected_account)
    st.session_state.billing_id = billing_id
    st.session_state.identity_type = st.selectbox('Select Identity Type', ['user', 'serviceAccount'])
    st.session_state.identity_email = st.text_input('Enter Identity Email')
    if st.session_state.project_id:
        st.markdown(f"""Manual Step Required: \n
                Go to: https://console.cloud.google.com/iam-admin/iam?project={project_id}, click "grant access"
                and grant the service account: looker-studio-dashboard-app@commit-automation.iam.gserviceaccount.com the following roles: \n
                `roles/resourcemanager.projectIamAdmin` (Project IAM Admin) \n
                'roles/viewer' (Viewer) \n
                'roles/datastore.user' (Cloud Datastore User) \n
                'roles/bigquery.admin' (BigQuery Admin) \n
                'roles/servicemanagement.admin' (Service Management Administrator) \n
                'roles/serviceusage.serviceUsageAdmin' (Service Usage Admin) \n
                Then, click the button below.""")
    else:
        st.markdown(f"""Manual Step Required:  ** FIRST FILL IN PROJECT ID ABOVE \n
                Go to: https://console.cloud.google.com/iam-admin/iam?project=<PROJECT-ID>, click "grant access"
                and grant the service account: looker-studio-dashboard-app@commit-automation.iam.gserviceaccount.com the following roles: \n
                `roles/resourcemanager.projectIamAdmin` (Project IAM Admin) \n
                'roles/viewer' (Viewer) \n
                'roles/datastore.user' (Cloud Datastore User) \n
                'roles/bigquery.admin' (BigQuery Admin) \n
                'roles/servicemanagement.admin' (Service Management Administrator) \n
                'roles/serviceusage.serviceUsageAdmin' (Service Usage Admin) \n
                Then, click the button below.""")

    if st.button('Setup Billing Export and Dashboard'):
        if st.session_state.project_id and st.session_state.billing_id and st.session_state.identity_type and st.session_state.identity_email:
            st.write("Working... ")
            #time.sleep(5)
            #target_project_roles = ['roles/viewer', "roles/datastore.user", "roles/bigquery.admin", "roles/servicemanagement.admin", "roles/serviceusage.serviceUsageAdmin"]
            #grant_permissions(project_id, "serviceAccount", "looker-studio-dashboard-app@commit-automation.iam.gserviceaccount.com", target_project_roles)
            time.sleep(10)
            # Set GCP Project
            set_gcloud_project(project_id)

            # Enable APIs
            enable_service('serviceusage.googleapis.com', project_id)
            enable_service('bigquery.googleapis.com', project_id)
            enable_service('cloudbilling.googleapis.com', project_id)

            # Create BigQuery Dataset
            create_bq_dataset(project_id)

            if check_bq_dataset(project_id):
                # Initialize or reset the check status
                st.session_state.check_status = False  # Added this line to manage check status


                # Check if BigQuery dataset is ready
                if check_bq_dataset_tables(project_id):
                        st.session_state.check_status = True  # Added this line to update check status
                        st.success('BigQuery dataset is ready for billing export.')

                else:
                    # Manual steps instructions
                    st.markdown(f"""
                    **Manual Steps Required:**
                                    
                    Setup billing export in the GCP Console:
                                    
                    1.  Go to: 
                            https://console.cloud.google.com/billing/{st.session_state.billing_id}/export/bigquery

                    2.""")  
                    st.image("./images/autobillingexport1.png")
                    st.markdown(f"""

                        Edit the settings for the data you would like to export, for BOTH data types. Both will need to be enabled in order to continue
                        Set the project name to the same one you entered in this app, and dataset to "{bigquery_dataset_id}", and click save.
                        Once you have enabled at least one type of data export for your dataset, after a few hours data should begin to appear in that dataset.
                        A table to house this data will automatically be created.

                    After completing these steps, click the button below.
                    """)
                    st.error('The dataset tables have not been created yet, please follow the instructions above if you haven\'t already, wait 30-60 minutes and try again.')

                    # Added "Check Again" button and its functionality
                    if st.button('Check Again'):  # Added this button for rechecking
                        if check_bq_dataset_tables(project_id):
                            st.session_state.check_status = True  # Update check status if tables are found
                            st.success('BigQuery dataset is ready for billing export.')
                            # Here you can add the continuation of your app's flow as if the table was found initially
                        else:
                            st.write('The dataset table is still not available. Please check again later.')
            else:
                st.error('There was an error creating the dataset. Please try again.')
        else:
            st.error('Please fill in all the required fields.')

# Add this function to clone the repository and set up the environment
def setup_dashboard_environment(project_id):
    # Set Project using gcloud CLI
    #subprocess.run(["gcloud", "config", "set", "project", project_id], check=True)

    # Enable Cloud Billing API using gcloud CLI
    enable_service("cloudbilling.googleapis.com", project_id)

    # Create the dashboard
    billboard_create_output = subprocess.run(["python3", "billboard/billboard.py", "-pr", project_id, "-se", "billing_export", "-de", "billing_export", "-bb", "dashboard_views"], capture_output=True, text=True)
    if billboard_create_output:
        st.text_area("Billboard creation output: ", billboard_create_output.stdout, height=300)
    else:
        st.error("Something went wrong while creating the billboard.")

    # Instructions for manual steps
    if billboard_create_output:
        st.markdown("""
        --> Configure the dashboard
                    
        These steps must be done manually, please follow the steps below:
      
        1. Browse to the Looker Studio link above (in the last paragraph of the output)
        2. Click on 'Edit and Share' in the up-right corner
        3. Click on the 'Acknowledge and Save' button
        4. Rename the dashboard to 'Billing Dashboard - CustomerName'
        5. Add the Commit logo (copy from another dashboard and paste in each page of the dashboard)
        6. Check that the 'Project Name Selection' works (if not, change the default time range property from 'Custom: Last Month' to 'Auto')
        """)

    # New button for manual step confirmation
    if st.button("I have completed the manual steps"):
        grant_permissions(project_id, st.session_state.identity_type, st.session_state.identity_email, ['roles/viewer', 'roles/bigquery.jobUser'])

def grant_permissions(project_id, identity_type, identity_email, roles):

    enable_service('cloudresourcemanager.googleapis.com', project_id)
    time.sleep(5)
    # Build the service object for the cloudresourcemanager API, assuming default credentials are set
    service = build('cloudresourcemanager', 'v1')
    
    # Construct the full resource name for the project and member
    resource = project_id
    member = f'{identity_type}:{identity_email}'
    
    # Get the current IAM policy
    policy = service.projects().getIamPolicy(resource=resource, body={}).execute()
    
    # Define the roles to add
    #roles = ['roles/viewer', 'roles/bigquery.jobUser']
    
    for role in roles:
        # Check if the role already exists in the policy, if not, add it
        found = False
        for binding in policy.get('bindings', []):
            if binding['role'] == role:
                if member not in binding['members']:
                    binding['members'].append(member)
                found = True
                break
        if not found:
            policy['bindings'].append({'role': role, 'members': [member]})
    
    # Update the policy
    set_policy_request_body = {'policy': policy}
    response = service.projects().setIamPolicy(resource=resource, body=set_policy_request_body).execute()
    
    st.text_area("Permission granting output: ", response, height=300)
    st.write(f"Finished granting roles: {str(roles)} to {identity_email} -- check for any error messages in the text box above.")

    # Manual step for Looker Studio Permission
    if response:
        st.markdown(f"""
    --> Remember to provide viewer access to {identity_email} in the Looker Studio Dashboard. 
    This step must be done manually.
    """)
#    if st.button("Let\'s do another!"):
#        st.session_state.to_clear = True
#        st.rerun()


if __name__ == "__main__":
    run_app()

    # New code: Check if the setup has been completed successfully and then proceed to setup the dashboard environment
    if "check_status" in st.session_state and st.session_state.check_status:
        setup_dashboard_environment(st.session_state.project_id)
