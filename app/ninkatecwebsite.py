import streamlit as st
from google.cloud import firestore
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, firestore
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator  # Add this line


service_account_key = {
  "type": "service_account",
  "project_id": "self-injecting-solution",
  "private_key_id": "a9fca48735a6eb317edbd028dfac500ee9900b69",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCKNpoAVi8P80Yx\nNSTgU/1or0db77cux3vbp9M+jFkN1h8kH6hC8gHoN1WFNzPBYhAm7iH1+0OftMQU\nme4WST8oU0XHIwSOveHbF4NApyvnS16ouPptgFU7F8RUvbG/1VE+GBR1l2bCTBb/\nxeWer4lXwXH4jMgJlreMMChZjK936j2jZdQoEiSrf/1bJVFihDXqzff1ITQhL8/O\nnmahz1v+DE/1mG+rEuyzTU4qjJcsxH1uIpehyWlDt5lXkt1ch6xfw+kNVaOhI85y\nwv7zWsFVgRgs5kaIy9H8XM6VIq98ttE9cmJC3cnnTsjejeyO7oL9aop8SxsCrmZD\nm6gjIUxZAgMBAAECggEABk9X2IwWufOxUK3McTFkcFMQPvJCurAAx5Zx3nkp16fe\n5BdN50CFNcTQ8rQCeOGxOxXEFybRf4kRKp+cbwgJCh5DIURIAPxKQ2ZfZ6Q6LOUT\n/T/0rusc+QWswPGoG8nxW5Rd2sB+wIAYzLSMNyJscsUyHtbOiyGGX7ATJ4N0v1Sx\nLsqfEToQTBYAyzwl6AYUWnxoHgqEPwXW4yJ1R5QxcqQmyN/59OTSqpp9nkRgbuxp\nPfx7aXJoDGFA3wbERSXjMLhxa9S6Au6t+Ps/XhWXrqY6ki8Qow200+UWRDcot2PQ\ndMcGKXia85QaNpe54PzaOKQBA9/rirkqMy4yqV9MwQKBgQC8lnzTp62J6I42dp7k\nd2gIO9A5JmtYvPHOjz7o/48oCTMty6+ouQ94purz7nIM5HmHafHNFMGxkrhO0k8d\nVvGWLyKOI+YZ3AI5IFmUhmf2x/xtXVO/zZKGhHkklbxmc6FQSAuY/j1jSgwfstuq\nuMv5z32XL8LMrCnHX4iCLfCXmwKBgQC7nmGn33DLhM0U0Z74MqQEkM76JhmY3TgF\n9KX1Pt+aC6ROOcI0DCDskWs7XihXWP2ZZ6L7U7gwRA03VLJbEQm8o/+hu7uzjaDS\nRU1SWrorY0Iqxoizuf8fhhmN0nF/60NgvKIV44i/7L4O7e0VSI25/im6fxrWU2Cb\nGL8j8OpdGwKBgFuU8RWP7jR0nOtR+6OTYQ/ujBXU1HiJeRwIcFKSGKEmppXsvmc/\nR4Yd+Sdwei5Mnb/m8SfYlp93Us3kT8s9t6BpT2ybfli8gM/hJ996ze4H/EvX8J3K\nZQeyOWpM1Osj6AimlAs+G+2lvfF+2DI1/8hWvPS4mu7uBHPvrskZKidVAoGAV+Vw\nXMQ6RK53oaw+7IpU+uqYfOrCjTH+YBPoeAe3m6SemiNHDzkrZ4kNEqgfACTp0ieS\nXGoxXTNUebqNQEqwJBc02KFp40mTsU7UVaO5mkALLJ0MSB74Hd2mNSIFGGewji5x\nRQ3u7/NKaxYePx1ZgGxJQlzvxr8TADZMvdrNAUcCgYEAotuTQras1UXtLkSRk1Mu\nZkOFIY+USqU5NLXKcyhL86rAvdu+KzUKi51QABzTvusfAEUWx1veuNGhEttb/Chh\nFfx86m0wMiYnm8Bp3XEysLw13OHxKSXaj7maAx9goyINSJQf2wDIAzALMNfrafHi\n4tp7cbo/BKqU/yjV2YfP4Mw=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-wwbzy@self-injecting-solution.iam.gserviceaccount.com",
  "client_id": "116197966361956163253",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-wwbzy%40self-injecting-solution.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Initialize Firebase Admin SDK for both Realtime Database and Firestore
cred = credentials.Certificate(service_account_key)

if not firebase_admin._apps:
    st.session_state.app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://self-injecting-solution-default-rtdb.asia-southeast1.firebasedatabase.app'})
    
firestore_db = firestore.client()

st.set_page_config(page_title = "Ninkatec", page_icon = ":syringe:", layout = 'wide')

## Sidebar
st.sidebar.title('Ninkatec')
st.sidebar.subheader('Making administration of medication easy')
page = st.sidebar.radio('Choose appropriate syringe:', ['Patient Data', 'Add New Syringe', 'History'])    

## Defining variables
patients_sn_list = []
patients_list = []
syringes_data = []
patient_namelist = []
patient_data_list = []
timestamps_dict = {}
drugs_dict = {'Morphine': 0, 'Fentanyl': 0,  'Haloperidol': 0, 'Hyoscine': 0, 'Midazolam': 0}
drugs_restock_dict = {'Morphine': 0, 'Fentanyl': 0,  'Haloperidol': 0, 'Hyoscine': 0, 'Midazolam': 0}

## Defining functions
def drug_input(drug_name):
    number_of_doses = st.number_input(f"Number of {drug_name} doses issued", min_value = 0, max_value = 30, value = 20, step = 1)
    drugs_dict[drug_name] = number_of_doses

def drug_restock(drug_name):
    number_of_doses = st.number_input(f"Number of {drug_name} doses restocked", min_value = 0, max_value = 30, value = 20, step = 1)
    drugs_restock_dict[drug_name] = number_of_doses

@st.cache_data
def load_data(df):
    return df

def convert_data(syringe_serial_number): # Function to fetch data from Realtime Database and write it to Firestore
    # Fetch data from Realtime Database
    morphine_ref = db.reference(f'{syringe_serial_number}/morphine_dosage_remaining')
    morphine_from_rt_db = morphine_ref.get()
    
    fentanyl_ref = db.reference(f'{syringe_serial_number}/fentanyl_dosage_remaining')
    fentanyl_from_rt_db = fentanyl_ref.get()
    
    haloperidol_ref = db.reference(f'{syringe_serial_number}/haloperidol_dosage_remaining')
    haloperidol_from_rt_db = haloperidol_ref.get()
    
    hyoscine_ref = db.reference(f'{syringe_serial_number}/hyoscine_dosage_remaining')
    hyoscine_from_rt_db = hyoscine_ref.get()
    
    midazolam_ref = db.reference(f'{syringe_serial_number}/midazolam_dosage_remaining')
    midazolam_from_rt_db = midazolam_ref.get()

    # Specify the Firestore collection and document
    firestore_ref = firestore_db.collection('syringes').document(syringe_serial_number)

    # Write data to Firestore
    if firestore_ref.get().exists:
        firestore_ref.update({'morphine_dosage_remaining': morphine_from_rt_db,
                            'fentanyl_dosage_remaining': fentanyl_from_rt_db,
                            'haloperidol_dosage_remaining': haloperidol_from_rt_db,
                            'hyoscine_dosage_remaining': hyoscine_from_rt_db,
                            'midazolam_dosage_remaining': midazolam_from_rt_db
                            })
    else:
        firestore_ref.set({'morphine_dosage_remaining': morphine_from_rt_db,
                            'fentanyl_dosage_remaining': fentanyl_from_rt_db,
                            'haloperidol_dosage_remaining': haloperidol_from_rt_db,
                            'hyoscine_dosage_remaining': hyoscine_from_rt_db,
                            'midazolam_dosage_remaining': midazolam_from_rt_db,
                            'morphine_injected': False,
                            'fentanyl_injected': False,
                            'haloperidol_injected': False,
                            'hyoscine_injected': False,
                            'midazolam_injected': False
                            })

def update_database_data(syringe_serial_number, drug_of_interest, new_value): # Function to update data in Realtime Database
    ref = db.reference(f'{syringe_serial_number}/{drug_of_interest}')  # Specify the path to the data you want to update
    original_from_rt_db = ref.get()
    if original_from_rt_db is None:
        original_from_rt_db = 0
    final_value = original_from_rt_db + new_value
    ref.set(final_value)

def clear_database_data(syringe_serial_number):
    morphine_ref = db.reference(f'{syringe_serial_number}/morphine_dosage_remaining')
    morphine_ref.set(0)
    
    fentanyl_ref = db.reference(f'{syringe_serial_number}/fentanyl_dosage_remaining')
    fentanyl_ref.set(0)
    
    haloperidol_ref = db.reference(f'{syringe_serial_number}/haloperidol_dosage_remaining')
    haloperidol_ref.set(0)
    
    hyoscine_ref = db.reference(f'{syringe_serial_number}/hyoscine_dosage_remaining')
    hyoscine_ref.set(0)
    
    midazolam_ref = db.reference(f'{syringe_serial_number}/midazolam_dosage_remaining')
    midazolam_ref.set(0)

def delete_firestore_data(syringe_serial_number):
    timestamps_ref = firestore_db.collection('syringes').document(syringe_serial_number).collection('timestamps')
    docs = timestamps_ref.list_documents()
    for doc in docs:
        doc.delete()
    firestore_ref = firestore_db.collection('syringes').document(syringe_serial_number)
    firestore_ref.delete()

def metric_colouring(metric, drug_name, dosage_remaining):
    if dosage_remaining < 5:
        metric.metric(f":red[{drug_name}]", dosage_remaining, delta = '-Running low!')
    else:
        metric.metric(f":green[{drug_name}]", dosage_remaining)

def calculate_time_difference(start_datetime_str, end_datetime_str):
    # Parse date-time strings into datetime objects
    start_datetime = datetime.strptime(start_datetime_str, "%d-%m-%y %H:%M")
    end_datetime = datetime.strptime(end_datetime_str, "%d-%m-%y %H:%M")

    # Calculate the time difference
    time_diff = end_datetime - start_datetime

    # Calculate hours and minutes from the time difference
    hours = time_diff.total_seconds() // 3600
    minutes = (time_diff.total_seconds() % 3600) // 60

    minutes_fraction = minutes / 60.0
    # Add fraction of an hour to hours
    total_time = hours + minutes_fraction
    # Return total time rounded to 1 decimal place
    return round(total_time, 1)

## Pages
if page == 'Patient Data':
    st.title('Patient Data')
    syringes_ref = firestore_db.collection("syringes")
    for doc in syringes_ref.stream():
        syringe = doc.to_dict()
        patient_data_list.append(syringe)
    for i in patient_data_list:     ## Obtain the patient names from the patient data list
        patient_namelist.append(i.get("patient_name"))
    selected_patient = st.selectbox('Select Patient Name', patient_namelist) ## Create a selectbox with the patient names
    df = load_data(pd.DataFrame(patient_data_list)) ## Load the patient data list into a dataframe
    df.drop(columns=['hyoscine_issued', 'morphine_issued', 'midazolam_issued', 'haloperidol_issued', 'fentanyl_issued'], inplace=True) ## Drop the columns that are not needed
    df.rename(columns={'hyoscine_dosage_remaining': 'Hyoscine Doses Available', ## Rename the columns
                       'morphine_dosage_remaining': 'Morphine Doses Available', 
                       'syringe_sn': 'Serial Number', 
                       'haloperidol_dosage_remaining': 'Haloperidol Doses Available', 
                       'midazolam_dosage_remaining': 'Midazolam Doses Available', 
                       'fentanyl_dosage_remaining': 'Fentanyl Doses Available', 
                       'patient_name': 'Patient Name',
                       'start_date': 'Start Date'}, 
                       inplace=True) 
    sorted_column = st.selectbox('Sort by:', options=df.columns, key='sort') ## Create a selectbox to sort the dataframe
    condition = df['Patient Name'] != "ALL"
    filtered_df = df[condition]
    if sorted_column and selected_patient == "ALL":
        df = filtered_df.dropna(subset=['Patient Name'])  # Drop rows where 'Patient Name' is null
        df = df.sort_values(sorted_column)
        view = st.dataframe(df, column_order=('Serial Number', 'Patient Name', 'Start Date', 'Morphine Doses Available', 'Fentanyl Doses Available', 'Haloperidol Doses Available', 'Hyoscine Doses Available', 'Midazolam Doses Available'))
    else:
        st.dataframe(pd.DataFrame(df[df['Patient Name'] == selected_patient]), column_order=('Serial Number', 'Patient Name', 'Start Date', 'Morphine Doses Available', 'Fentanyl Doses Available', 'Haloperidol Doses Available', 'Hyoscine Doses Available', 'Midazolam Doses Available')) ## Display the dataframe with the selected patient's data

if page == 'Add New Syringe':
    ## Page Configuration
    st.header("Add Syringe Information")
    new_patient, existing_patient = st.tabs(["New Patient", "Existing Patient"])

    ## New Patient
    with new_patient:
        syringe_sn = st.number_input("Enter syringe serial number (Eg: 12345)", min_value = 1, step = 1)
        patient_name = st.text_input("Enter name of patient", value = 'NIL')
        drugs_issued = st.multiselect("Drugs Issued", ["Morphine", "Fentanyl", "Haloperidol", "Hyoscine", "Midazolam"])
        for drug in drugs_issued:
            drug_input(drug)

        submit = st.button("Confirm")

        if syringe_sn and patient_name and drugs_issued and submit:
            current_date = datetime.now()
            formatted_date = current_date.strftime('%d-%m-%y')
            doc_ref = firestore_db.collection("syringes").document(f"syringe{syringe_sn}")
            history_ref = firestore_db.collection("history").document(f"{patient_name}-{formatted_date}")

            ## Update The Realtime Database
            update_database_data(f'syringe{syringe_sn}', 'morphine_dosage_remaining', drugs_dict['Morphine'])
            update_database_data(f'syringe{syringe_sn}', 'fentanyl_dosage_remaining', drugs_dict['Fentanyl'])
            update_database_data(f'syringe{syringe_sn}', 'haloperidol_dosage_remaining', drugs_dict['Haloperidol'])
            update_database_data(f'syringe{syringe_sn}', 'hyoscine_dosage_remaining', drugs_dict['Hyoscine'])
            update_database_data(f'syringe{syringe_sn}', 'midazolam_dosage_remaining', drugs_dict['Midazolam'])

            ## Update Firestore
            convert_data(f'syringe{syringe_sn}')

            ## Update Firestore With Non-Numerical Data
            doc_ref.update({
                "syringe_sn": syringe_sn,
                "morphine_issued": drugs_dict['Morphine'],
                "fentanyl_issued": drugs_dict['Fentanyl'],
                "haloperidol_issued": drugs_dict['Haloperidol'],
                "hyoscine_issued": drugs_dict['Hyoscine'],
                "midazolam_issued": drugs_dict['Midazolam'],
                "patient_name": patient_name,
                "start_date": formatted_date
            })

            history_ref.set({
                "start_date": formatted_date,
                "patient_name": patient_name,
                "morphine_issued": drugs_dict['Morphine'],
                "fentanyl_issued": drugs_dict['Fentanyl'],
                "haloperidol_issued": drugs_dict['Haloperidol'],
                "hyoscine_issued": drugs_dict['Hyoscine'],
                "midazolam_issued": drugs_dict['Midazolam']
            })

            st.success("Syringe data added successfully")

    with existing_patient:    
        collection_ref = firestore_db.collection("syringes").where('patient_name', '>', '').get()
        for doc in collection_ref:
            patients_sn_list.append([doc.get('patient_name'), doc.get('syringe_sn')])
        for patient in patients_sn_list:
            patients_list.append(patient[0])
        selected_patient = st.selectbox('Patient', patients_list)
        
        if selected_patient:
            for patient in patients_sn_list:
                if selected_patient in patient:
                    patient_sn = f'syringe{patient[1]}'  
                    
            st.session_state.selected_patient = selected_patient 
            
            ## Fetch data from Firestore
            patient_ref = firestore_db.collection("syringes").document(patient_sn)
            doc = patient_ref.get()
            morphine_dosage = doc.get('morphine_dosage_remaining')
            fentanyl_dosage = doc.get('fentanyl_dosage_remaining')
            haloperidol_dosage = doc.get('haloperidol_dosage_remaining')
            hyoscine_dosage = doc.get('hyoscine_dosage_remaining')
            midazolam_dosage = doc.get('midazolam_dosage_remaining')

            if doc.exists:
                st.subheader(f"Syringe serial number: {doc.get('syringe_sn')}")
                
                Morphine, Fentanyl, Haloperidol, Hyoscine, Midazolam = st.columns(5, gap = 'medium')
                with Morphine:
                    morphine_metric = st.metric("Morphine", morphine_dosage)
                    if doc.get('morphine_issued'):
                        metric_colouring(morphine_metric, 'Morphine', morphine_dosage)
                    else:
                        st.info("Morphine not issued to patient")
                        
                with Fentanyl:
                    fentanyl_metric = st.metric("Fentanyl", fentanyl_dosage)
                    if doc.get('fentanyl_issued'):
                        metric_colouring(fentanyl_metric, 'Fentanyl', fentanyl_dosage)
                    else:
                        st.info("Fentanyl not issued to patient")
                        
                with Haloperidol:
                    haloperidol_metric = st.metric("Haloperidol", haloperidol_dosage)
                    if doc.get('haloperidol_issued'):
                        metric_colouring(haloperidol_metric, 'Haloperidol', haloperidol_dosage)
                    else:
                        st.info("Haloperidol not issued to patient")
                    
                with Hyoscine:
                    hyoscine_metric = st.metric("Hyoscine", hyoscine_dosage)
                    if doc.get('hyoscine_issued'):
                        metric_colouring(hyoscine_metric, 'Hyoscine', hyoscine_dosage)
                    else:
                        st.info("Hyoscine not issued to patient")
                        
                with Midazolam:
                    midazolam_metric = st.metric("Midazolam", midazolam_dosage)
                    if doc.get('midazolam_issued'):
                        metric_colouring(midazolam_metric, 'Midazolam', midazolam_dosage)
                    else:
                        st.info("Midazolam not issued to patient")
                
                drugs_restock = st.multiselect("Drugs restock", ["Morphine", "Fentanyl", "Haloperidol", "Hyoscine", "Midazolam"], key = 'multiselect')
                for drug in drugs_restock:
                    drug_restock(drug)

                confirm = st.button("Restock")

                ## Fetch timestamps from Firestore
                morphine_timestamp_ref = firestore_db.collection('syringes').document(patient_sn).collection('timestamps').document('morphine')
                fentanyl_timestamp_ref = firestore_db.collection('syringes').document(patient_sn).collection('timestamps').document('fentanyl')
                haloperidol_timestamp_ref = firestore_db.collection('syringes').document(patient_sn).collection('timestamps').document('haloperidol')
                hyoscine_timestamp_ref = firestore_db.collection('syringes').document(patient_sn).collection('timestamps').document('hyoscine')
                midazolam_timestamp_ref = firestore_db.collection('syringes').document(patient_sn).collection('timestamps').document('midazolam')

                if morphine_timestamp_ref.get().exists:
                    morphine_timestamps = morphine_timestamp_ref.get().to_dict()
                    timestamps_dict['Morphine'] = morphine_timestamps
                
                if fentanyl_timestamp_ref.get().exists:
                    fentanyl_timestamps = fentanyl_timestamp_ref.get().to_dict()
                    timestamps_dict['Fentanyl'] = fentanyl_timestamps
                
                if haloperidol_timestamp_ref.get().exists:
                    haloperidol_timestamps = haloperidol_timestamp_ref.get().to_dict()
                    timestamps_dict['Haloperidol'] = haloperidol_timestamps

                if hyoscine_timestamp_ref.get().exists:
                    hyoscine_timestamps = hyoscine_timestamp_ref.get().to_dict()
                    timestamps_dict['Hyoscine'] = hyoscine_timestamps

                if midazolam_timestamp_ref.get().exists:
                    midazolam_timestamps = midazolam_timestamp_ref.get().to_dict()
                    timestamps_dict['Midazolam'] = midazolam_timestamps

                # Find the maximum number of timestamps among all drugs
                if timestamps_dict:
                    st.divider()
                    col1, col2 = st.columns([7,1])
                    with col1:
                        st.subheader('Timestamps')
                    with col2:
                        refresh = st.button("Refresh")
                    max_timestamps = max(len(timestamps) for timestamps in timestamps_dict.values())
                    df_timestamps = pd.DataFrame(index=timestamps_dict.keys(), columns=[f'Timestamp {i}' for i in range(1, max_timestamps + 1)])
                    df_intervals = pd.DataFrame(index=timestamps_dict.keys(), columns=[f'Interval {i}' for i in range(1, max_timestamps)])

                    # Fill DataFrame with timestamps
                    for drug, timestamps in timestamps_dict.items():
                        for i, timestamp in enumerate(timestamps.values(), start=1):
                            df_timestamps.at[drug, f'Timestamp {i}'] = timestamp

                    for drug, timestamps in timestamps_dict.items():
                        for i, timestamp in enumerate(timestamps.values(), start=1):
                            if i < len(timestamps):
                                df_intervals.at[drug, f'Interval {i}'] = calculate_time_difference(timestamp, list(timestamps.values())[i])

                    st.dataframe(df_timestamps)

                    counts = defaultdict(lambda: defaultdict(int))

                    # Count the injections for each drug on each day
                    for drug, timestamps in timestamps_dict.items():
                        for ts in timestamps.values():
                            date = datetime.strptime(ts, "%d-%m-%y %H:%M").date()  # Extract the date part
                            counts[drug][date] += 1

                    # Create a DataFrame from the counts
                    df_injections_per_day = pd.DataFrame(counts)

                    # Fill missing values with 0
                    df_injections_per_day.fillna(0, inplace=True)

                    # Sort the columns by date
                    df_injections_per_day = df_injections_per_day.reindex(sorted(df_injections_per_day.columns), axis=1)

                    custom_colors = ['#36579A', '#4984B5', '#7CA8CC', '#1C4260', '#15609D']  # Example hexadecimal color codes
                    
                    fig1, ax1 = plt.subplots()
                    df_injections_per_day.plot(kind='bar', ax=ax1, color=custom_colors)
                    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
                    ax1.set_xlabel('Date', fontsize=10)  # Adjust the font size here
                    ax1.set_ylabel('Number of Injections', fontsize=10)   # Adjust the font size here
                    ax1.set_title('Number of Injections per Day', fontsize=12)  # Adjust the font size here
                    ax1.tick_params(axis='both', which='major', labelsize=8)  # Adjust the tick label size here
                    ax1.legend(fontsize=8)  # Adjust the legend font size here
                    plt.xticks(rotation=0, ha='center')
                    fig1.patch.set_alpha(0)  # Set alpha value for the figure background
                    ax1.patch.set_alpha(0)  # Set alpha value for the axes background

                    fig2, ax2 = plt.subplots()

                    for drug in df_intervals.index:
                        ax2.plot(df_intervals.loc[drug][-5:], label=drug, color=custom_colors.pop(0))
                    
                    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
                    ax2.set_ylim(0, 5)
                    ax2.set_xlabel('Interval Number', fontsize=10)  # Adjust the font size here
                    ax2.set_ylabel('Time Interval', fontsize=10)   # Adjust the font size here
                    ax2.set_title('Intervals between Last 20 Injections', fontsize=12)  # Adjust the font size here
                    ax2.tick_params(axis='both', which='major', labelsize=8)  # Adjust the tick label size here
                    ax2.legend(fontsize=8)  # Adjust the legend font size here
                    fig2.patch.set_alpha(0)  # Set alpha value for the figure background
                    ax2.patch.set_alpha(0)  # Set alpha value for the axes background

                    col1, col2 = st.columns([1,1])
                    with col1:
                        st.pyplot(fig1)
                    with col2:
                        st.pyplot(fig2)

                    if refresh:
                        st.success("Page refreshed")
                        st.rerun()

                st.divider()

                data_clear = st.button("Clear Data")

                ## If the user clicks the restock button
                if confirm:
                    doc_ref = firestore_db.collection("syringes").document(f"syringe{syringe_sn}")

                    ## Update The Realtime Database
                    update_database_data(f'syringe{syringe_sn}', 'morphine_dosage_remaining', drugs_restock_dict['Morphine'])
                    update_database_data(f'syringe{syringe_sn}', 'fentanyl_dosage_remaining', drugs_restock_dict['Fentanyl'])
                    update_database_data(f'syringe{syringe_sn}', 'haloperidol_dosage_remaining', drugs_restock_dict['Haloperidol'])
                    update_database_data(f'syringe{syringe_sn}', 'hyoscine_dosage_remaining', drugs_restock_dict['Hyoscine'])
                    update_database_data(f'syringe{syringe_sn}', 'midazolam_dosage_remaining', drugs_restock_dict['Midazolam'])

                    ## Update Firestore
                    convert_data(f'syringe{syringe_sn}')

                    morphine_dosage = doc.get('morphine_dosage_remaining') + drugs_restock_dict['Morphine']
                    fentanyl_dosage = doc.get('fentanyl_dosage_remaining') + drugs_restock_dict['Fentanyl']
                    haloperidol_dosage = doc.get('haloperidol_dosage_remaining') + drugs_restock_dict['Haloperidol']
                    hyoscine_dosage = doc.get('hyoscine_dosage_remaining') + drugs_restock_dict['Hyoscine']
                    midazolam_dosage = doc.get('midazolam_dosage_remaining') + drugs_restock_dict['Midazolam']

                    ## Update Firestore With Non-Numerical Data
                    doc_ref.update({
                        "morphine_issued": doc.get("morphine_issued") + drugs_restock_dict['Morphine'],
                        "fentanyl_issued": doc.get("fentanyl_issued") + drugs_restock_dict['Fentanyl'],
                        "haloperidol_issued": doc.get("haloperidol_issued") + drugs_restock_dict['Haloperidol'],
                        "hyoscine_issued": doc.get("hyoscine_issued") + drugs_restock_dict['Hyoscine'],
                        "midazolam_issued": doc.get("midazolam_issued") + drugs_restock_dict['Midazolam']
                    })

                    temp = doc_ref.get()
                    st.write(temp.get("morphine_issued"))    

                    history_ref = firestore_db.collection("history").document(f"{selected_patient}-{doc.get('start_date')}")

                    history_ref.update({
                        "morphine_issued": doc.get("morphine_issued") + drugs_restock_dict['Morphine'],
                        "fentanyl_issued": doc.get("fentanyl_issued") + drugs_restock_dict['Fentanyl'],
                        "haloperidol_issued": doc.get("haloperidol_issued") + drugs_restock_dict['Haloperidol'],
                        "hyoscine_issued": doc.get("hyoscine_issued") + drugs_restock_dict['Hyoscine'],
                        "midazolam_issued": doc.get("midazolam_issued") + drugs_restock_dict['Midazolam']
                    })
                    st.success("Drugs restocked successfully")
                    st.rerun()

                ## If the user clicks the clear data button
                if data_clear:
                    clear_database_data(f'syringe{syringe_sn}')
                    delete_firestore_data(f'syringe{syringe_sn}')
                    current_date = datetime.now()
                    formatted_date = current_date.strftime('%d-%m-%y')
                    doc_ref = firestore_db.collection("syringes").document(f"syringe{syringe_sn}")
                    history_ref = firestore_db.collection("history").document(f"{selected_patient}-{doc.get('start_date')}")
                    history_ref.update({"end_date": formatted_date})
                    st.success("Data Cleared")
                    st.rerun()

if page == 'History':
    st.title('History')
    syringes_ref = firestore_db.collection("history")
    for doc in syringes_ref.stream():
        patient = doc.to_dict()
        patient_data_list.append(patient)
    for i in patient_data_list:     ## Obtain the patient names from the patient data list
        patient_namelist.append(i.get("patient_name"))
    selected_patient = st.selectbox('Select Patient Name', patient_namelist, index=patient_namelist.index('ALL')) ## Create a selectbox with the patient names
    df = load_data(pd.DataFrame(patient_data_list)) ## Load the patient data list into a dataframe
    df.rename(columns={'hyoscine_issued': 'Hyoscine Dosages Issued', ## Rename the columns
                       'morphine_issued': 'Morphine Dosages Issued', 
                       'haloperidol_issued': 'Haloperidol Dosages Issued', 
                       'midazolam_issued': 'Midazolam Dosages Issued', 
                       'fentanyl_issued': 'Fentanyl Dosages Issued', 
                       'patient_name': 'Patient Name',
                       'start_date': 'Start Date',
                       'end_date': 'End Date'}, 
                       inplace=True)
    condition = df['Patient Name'] != "ALL"
    filtered_df = df[condition]
    if selected_patient == "ALL":
        view = st.dataframe(filtered_df, column_order=('Patient Name', 'Start Date', 'End Date', 'Morphine Dosages Issued', 'Fentanyl Dosages Issued', 'Haloperidol Dosages Issued', 'Hyoscine Dosages Issued', 'Midazolam Dosages Issued'))
    else:
        st.dataframe(pd.DataFrame(df[df['Patient Name'] == selected_patient]), column_order=('Patient Name', 'Start Date', 'End Date', 'Morphine Dosages Issued', 'Fentanyl Dosages Issued', 'Haloperidol Dosages Issued', 'Hyoscine Dosages Issued', 'Midazolam Dosages Issued')) ## Display the dataframe with the selected patient's data
