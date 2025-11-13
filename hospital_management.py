import streamlit as st
import mysql.connector as mysql
import pandas as pd
from datetime import datetime, timedelta, date
import logging
import itertools as it
import csv
import io
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s'))

hospital_name = "VYY Hospitals"
hospital_address = "Hulimavu, Bangalore"
product_name = "Medicare"

st.set_page_config(page_title=f"Hospital Management System - {product_name}", layout="wide")

# Custom CSS for the fixed header
st.markdown("""
<style>
.fixed-header {
    color: black;
    text-align: center;
    border: 0px solid silver; /* rounded corners */
    border-radius: 5px;
    z-index: 100;
    font-size: 24px;
    font-weight: bold;
}
.stMainBlockContainer {
    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0rem;
    padding-bottom: 0rem;
}
.stAppHeader {
    background-color: rgba(255, 255, 255, 0.0);
    visibility: visible;
}
[data-testid = "stSidebarHeader"] {
    height: 2rem; /* 2rem keeps just enough space for the icon*/
}
.logo {
    width: 50px;
    height: 50px;
    margin: 0px;
    padding: 0px;
    object-fit: contain;
}
.main .block-container {
    padding-top: 5rem; /* Adjust this padding to prevent content from hiding behind the header */
}
</style>
""", unsafe_allow_html=True)
st.markdown(f"<div class='fixed-header'><img src='app/static/hosp-logo.png' alt='Hospital Logo' class='logo'> Hospital Management System - {hospital_name}</div>", unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center; border-bottom: 1px solid #dbeafe; padding-bottom: 10px; color: black;"> 	{hospital_address}</div>', unsafe_allow_html=True)

if "logged_in" not in st.session_state or st.session_state.logged_in is None:
    st.session_state.logged_in = False

# DB Helpers
@st.cache_resource
def get_db_connection():
    mycon = mysql.connect(
            host=st.secrets.database.server,
            user='admin',
            password='password',
            database=st.secrets.database.database,
            ssl_disabled=True,
            autocommit=True,
            connection_timeout=10,
        )
    with mycon.cursor() as cur:
        cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")  # optional but recommended
    return mycon

illness_to_specialty_mappings = {
    'Cardiology': ['Heart Problems', 'Heart Failure'],
    'General Physician': ['Fever', 'Cold', 'Cough', 'Body Pains'],
    'Neurology': ['Blood Pressure Problems', 'Hypertension', 'Brain Tumor', 'Concussion', 'Brain Problems'],
    'Respiratory': ['Asthma', 'Tuberculosis', 'Lung Cancer', 'Respiratory Problems'],
    'Orthopedic': ['Arithritis', 'Fracture', 'Dislocation', 'Elbow Problems', 'Knee Problems'],
    'Dentist': ['Tooth Decay', 'Gum Infection', 'Cavity', 'Teeth Problems'],
    'Nephrology': ['Kidney Stone', 'Kidney Problems'],
    'Dermatology': ['Skin Problems', 'Rashes', 'Acne'],
    'Psychology': ['Psychological Problems', 'ADHD', 'Anxiety', 'Autism'],
}

def doctor_reference_for_illness(illness: str):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        for specialty, illnesses in illness_to_specialty_mappings.items():
            if illness in illnesses:
                cursor.execute(f"select * from doctors where specialty='{specialty}';")
                return cursor.fetchall()
        # if not there in any specialty, return all doctors
        cursor.execute("select * from doctors;")
        return cursor.fetchall()


def show_doctors():
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute("select doctor_id, name, specialty, phno, email, address from doctors;")
        return cursor.fetchall()

def show_patient(order_by: str = "updated_at desc"):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select patient_id, name, dob, gender, blood_grp, illness, address, contact_number, email from patients order by {order_by};")
        return cursor.fetchall()

def search_patients(field: str, item: str) -> list[tuple]:
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select patient_id, name, dob, gender, blood_grp, illness, address, contact_number, email from patients where {field} like '%{item}%';")
        return cursor.fetchall()

def add_doctor(name: str, specialty: str, phone: str, email: str, address: str) -> int:
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"insert into doctors(name, specialty, phno, email, address) values('{name}', '{specialty}', '{phone}', '{email}', '{address}');")
            mycon.commit()
            return cursor.lastrowid
    except Exception as e:
        mycon.rollback()
        raise e

def search_doctors(field: str, item: str):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select doctor_id, name, specialty, phno, email, address from doctors where {field} like '%{item}%';")
        return cursor.fetchall()

def delete_doctor(doctor_id: int):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"delete from doctors where doctor_id = {doctor_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

def update_doctor(doctor_id: int, name: str, specialty: str, phone: str, email: str, address: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update doctors set name = '{name}', specialty = '{specialty}', phno = '{phone}', email = '{email}', address = '{address}' where doctor_id = {doctor_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update doctors set name = '{name}', specialty = '{specialty}', phno = '{phone}', email = '{email}', address = '{address}' where doctor_id = {doctor_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

def add_patient(name: str, dob: datetime, gender: str, blood_grp: str, illness: str, address: str, contact_number: str, email: str) -> int:
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"insert into patients(name, dob, gender, blood_grp, illness, address, contact_number, email) values('{name}', '{dob}', '{gender}', '{blood_grp}', '{illness}', '{address}', '{contact_number}', '{email}');")
            mycon.commit()
            return cursor.lastrowid
    except Exception as e:
        mycon.rollback()
        raise e

def delete_patient(patient_id: int):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"delete from patients where patient_id = {patient_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e
def update_patient(patient_id: int, name: str, dob: datetime, gender: str, blood_grp: str, illness: str, address: str, contact_number: str, email: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update patients set name = '{name}', dob = '{dob}', gender = '{gender}', blood_grp = '{blood_grp}', illness = '{illness}', address = '{address}', contact_number = '{contact_number}', email = '{email}' where patient_id = {patient_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

## Assigning patients to doctors
def assign_patient_to_doctor(patient_id: int, doctor_id: int):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update patients set doctor_id = {doctor_id} where patient_id = {patient_id}")
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

## Apointment tables
def show_booked_timings(doctor_id: int, appointment_date: datetime):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select appointment_time from appointments where doctor_id = %s and appointment_date = %s and status != 'Cancelled' and status != 'Completed'", (doctor_id, appointment_date,))
        return cursor.fetchall()

def add_appointment(patient_id: int, doctor_id: int, appointment_date: datetime, appointment_time: int, reason: str, notes: str, medication: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"insert into appointments(patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes, medication) values(%s, %s, %s, %s, %s, %s, %s, %s)", (patient_id, doctor_id, appointment_date, appointment_time, "Pending", reason, notes, medication))
            mycon.commit()
            return cursor.lastrowid
    except Exception as e:
        mycon.rollback()
        raise e

def show_appointments_for_doctor(doctor_id: int):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select appointment_id, a.patient_id, p.name, appointment_date, appointment_time, status, reason, notes, medication, bill, bill_status from appointments a join patients p on a.patient_id = p.patient_id where a.doctor_id = %s", (doctor_id,))
        return cursor.fetchall()

def show_appointments_for_patient(patient_id: int):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select appointment_id, a.doctor_id, dr.name, appointment_date, appointment_time, status, reason, notes, medication, bill, bill_status, pt.name from appointments a join doctors dr on a.doctor_id = dr.doctor_id join patients pt on a.patient_id = pt.patient_id where a.patient_id = %s order by appointment_date, appointment_time", (patient_id,))
        return cursor.fetchall()

def delete_appointment(appointment_id: int):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"delete from appointments where appointment_id = %s", (appointment_id,))
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

def update_appointment_status(appointment_id: int, status: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update appointments set status = %s where appointment_id = %s", (status, appointment_id))
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

def add_prescription(appointment_id: int, notes: str, prescription: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update appointments set notes = %s, medication = %s where appointment_id = %s", (notes, prescription, appointment_id))
            mycon.commit()
            return cursor.rowcount  
    except Exception as e:
        mycon.rollback()
        raise e

def update_appointment_bill(appointment_id: int, amount: int, bill_status: str):
    mycon = get_db_connection()
    try:
        with mycon.cursor() as cursor:
            cursor.execute(f"update appointments set bill_status = %s, bill = %s where appointment_id = %s", (bill_status, amount, appointment_id))
            mycon.commit()
            return cursor.rowcount
    except Exception as e:
        mycon.rollback()
        raise e

def get_latest_bill_status(appointment_id: int):
    mycon = get_db_connection()
    with mycon.cursor() as cursor:
        cursor.execute(f"select bill_status from appointments where appointment_id = %s order by updated_at desc limit 1", (appointment_id,))
        return cursor.fetchone()[0]

# Login/Logout Modules
def login():
    with st.form("login_form"):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"![alt text](app/static/hosp-logo-big.png)")
        with col2:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                try:
                    index = st.secrets["app"]["users"].index(username)
                    actual_password = st.secrets["app"]["password"][index]
                    if index is None or index < 0:
                        st.error("Invalid username")
                        return
                    if password != actual_password:
                        st.error("Invalid password")
                        return
                    st.session_state.logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to login: Invalid username or password")
                    logger.error(f"Failed to login: {e}")
                    st.session_state.logged_in = False

def logout():
    st.session_state.logged_in = False
    st.session_state.clear()
    st.rerun()


# Custom Components
import streamlit.components.v1 as components

def go_back_button():
    components.html(
        """
        <script>
            function goBack() {
                window.history.back();
            }
        </script>
        <button onclick="goBack()" style="
            background-color: #f0f2f6; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
        ">⬅️ Go Back</button>
        """,
        height=50
    )

# Utils

def validate_email(email: str):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email address")

def validate_phone_number(phone_number: str):
    if not re.match(r"^\d{10}$", phone_number):
        raise ValueError("Invalid phone number")

# Page Definitions
## Patient pages
def page_new_patient():
    st.write("## New Patient Registration")
    with st.form("new_patient_form"):   
        patient_name = st.text_input("Patient Name")
        patient_dob = st.date_input("Patient DOB")
        patient_gender = st.selectbox("Patient Gender", ["m", "f"], format_func=lambda x: "Male" if x == "m" else "Female")
        patient_blood_grp = st.selectbox("Patient Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        patient_illness = st.selectbox("Patient Illness", list(it.chain.from_iterable(illness_to_specialty_mappings.values())))
        patient_address = st.text_input("Patient Address")
        patient_contact_number = st.text_input("Patient Contact Number")
        patient_email = st.text_input("Patient Email")
        if st.form_submit_button("Register Patient"):
            try:
                validate_email(patient_email)
                validate_phone_number(patient_contact_number)
                patient_id = add_patient(patient_name, patient_dob, patient_gender, patient_blood_grp, patient_illness, patient_address, patient_contact_number, patient_email)
                st.success(f"Patient registered successfully with ID {patient_id}")
            except Exception as e:
                st.error(f"Failed to register patient: {e}")
    go_back_button()

def page_assign_doctor():
    st.write("## Assign Doctor")
    with st.form("assign_doctor_form"):
        patients = show_patient()
        # columns: patient_id, name, dob, gender, blood_grp, illness, address, contact_number, email
        patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
        illness = patient[5]
        st.write(f" Illness: {illness}")
        doctors = doctor_reference_for_illness(illness)
        doctor = st.selectbox("Doctors", doctors, format_func=lambda x: f"{x[1]}")
        if st.form_submit_button("Allocate Doctor"):
            try:
                assign_patient_to_doctor(patient[0], doctor[0])
                st.success("Doctor assigned successfully")
            except Exception as e:
                st.error(f"Failed to assign doctor: {e}")
    go_back_button()
    
def page_search_patient():
    st.write("## Search Patient")
    data = None
    with st.form("search_patient_form"):
        field = st.selectbox("Field", ["patient_id", "name", "dob", "gender", "blood_grp", "illness", "address", "contact_number", "email"])
        item = st.text_input("Value")
        if st.form_submit_button("Search Patient"):
            try:
                patients = search_patients(field, item)
                data = pd.DataFrame(patients, columns=["ID", "Name", "DOB", "Gender", "Blood Group", "Illness", "Address", "Contact Number", "Email"])
            except Exception as e:
                st.error(f"Failed to search patient: {e}")
    if data is not None:
        st.dataframe(data, width='stretch', hide_index=True)
    go_back_button()

def page_patient_details():
    st.write("## Patient Details")
    patients = show_patient()
    patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
    with st.form("patient_details_form"):
        if patient is not None and len(patient) > 0:
            ptDOB = st.date_input("Patient DOB", value=patient[2])
            gender_options = ["m", "f"]
            try:
                gender_index = gender_options.index(patient[3]) if patient[3] in gender_options else 0
            except Exception:
                gender_index = 0
            ptGender = st.selectbox("Patient Gender", gender_options, index=gender_index)
            
            blood_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            try:
                blood_index = blood_options.index(patient[4]) if patient[4] in blood_options else 0
            except Exception:
                blood_index = 0
            ptBloodGrp = st.selectbox("Patient Blood Group", blood_options, index=blood_index)

            illness_options = list(it.chain.from_iterable(illness_to_specialty_mappings.values()))
            try:
                illness_index = illness_options.index(patient[5]) if patient[5] in illness_options else 0
            except Exception:
                illness_index = 0
            ptIllness = st.selectbox("Patient Illness", illness_options, index=illness_index)
            ptAddress = st.text_input("Patient Address", value=patient[6])
            ptContactNumber = st.text_input("Patient Contact Number", value=patient[7])
            ptEmail = st.text_input("Patient Email", value=patient[8])
            try:
                if st.form_submit_button("Update Details"):
                    update_patient(patient[0], patient[1], ptDOB, ptGender, ptBloodGrp, ptIllness, ptAddress, ptContactNumber, ptEmail)
                    st.success("Patient details updated successfully")
                elif st.form_submit_button("Delete Patient"):
                    # delete_patient(patient[0])
                    st.success("Patient deleted successfully")
            except Exception as e:
                st.error(f"Failed to update patients details: {e}")
    go_back_button()
                
## Doctor pages
def page_new_doctor():
    st.write("## New Doctor Registration")
    with st.form("new_doctor_form"):
        doctor_name = st.text_input("Doctor Name")
        doctor_specialty = st.selectbox("Doctor Specialty", list(illness_to_specialty_mappings.keys()))
        doctor_phone = st.text_input("Doctor Phone")
        doctor_email = st.text_input("Doctor Email")
        doctor_address = st.text_input("Doctor Address")
        if st.form_submit_button("Register Doctor"):
            try:
                validate_email(doctor_email)
                validate_phone_number(doctor_phone)
                doctor_id = add_doctor(doctor_name, doctor_specialty, doctor_phone, doctor_email, doctor_address)
                st.success(f"Doctor registered successfully with ID {doctor_id}")
            except Exception as e:
                st.error(f"Failed to register doctor: {e}")
    go_back_button()
def page_search_doctor():
    st.write("## Search Doctor")
    data = None
    with st.form("search_doctor_form"):
        field = st.selectbox("Field", ["doctor_id", "name", "specialty", "phone", "email", "address"])
        item = st.text_input("Value")
        if st.form_submit_button("Search Doctor"):
            try:
                doctors = search_doctors(field, item)
                # columns from search_doctors: doctor_id, name, specialty, phno, email, address
                data = pd.DataFrame(doctors, columns=["Doctor ID", "Name", "Specialty", "Phone", "Email", "Address"])
            except Exception as e:
                st.error(f"Failed to search doctor: {e}")
    if data is not None:
        st.dataframe(data, width='stretch', hide_index=True)
    go_back_button()
    
def page_doctor_details():
    st.write("## Doctor Details")
    doctors = show_doctors()
    doctor = st.selectbox("Doctors", doctors, format_func=lambda x: f"{x[1]}")
    #  doctor_id, name, specialty, phno, email, address
    with st.form("doctor_details_form"):
        doctor_name = st.text_input("Doctor Name", value=doctor[1])
        doctor_specialty = st.selectbox("Doctor Specialty", list(illness_to_specialty_mappings.keys()), index=list(illness_to_specialty_mappings.keys()).index(doctor[2]) if doctor[2] in illness_to_specialty_mappings.keys() else 0)
        doctor_phone = st.text_input("Doctor Phone", value=doctor[3])
        doctor_email = st.text_input("Doctor Email", value=doctor[4])
        doctor_address = st.text_input("Doctor Address", value=doctor[5])
        if st.form_submit_button("Update Details"):
            try:
                update_doctor(doctor[0], doctor_name, doctor_specialty, doctor_phone, doctor_email, doctor_address)
                st.success("Doctor details updated successfully")
            except Exception as e:
                st.error(f"Failed to update doctor details: {e}")
        if st.form_submit_button("Delete Doctor"):
            delete_doctor(doctor[0])
            st.success("Doctor deleted successfully")
    go_back_button()
    
# Appointment pages
def page_appointment_new():
    st.write("## Appointment Booking")
    patients = show_patient()
    patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
    illness = patient[5]
    doctors = doctor_reference_for_illness(illness)
    doctor = st.selectbox("Doctor", doctors, format_func=lambda x: f"{x[1]}")
    if doctor is None or len(doctor) == 0:
        st.error("No doctors found for the selected illness")
        go_back_button()
        return

    # reason = st.selectbox("Reason", it.chain.from_iterable(illness_to_specialty_mappings.values()))
    appointment_date = st.date_input("Appointment Date", min_value=date.today())
    
    with st.form("appointment_booking_form"):
        
        # calculate available time slots
        booked_timings = show_booked_timings(doctor[0], appointment_date)
        booked_timings = [int(x[0].total_seconds()/60) for x in booked_timings]
        availability = list(it.chain(range(9*60, 13*60, 15), range(16*60, 20*60, 15)))
        timings = sorted(set(availability).difference(set(booked_timings)))

        if "appointment_booking_status" in st.session_state and st.session_state.appointment_booking_status is not None:
            if st.session_state.appointment_booking_status == "success":
                st.success(st.session_state.appointment_booking_message)
            elif st.session_state.appointment_booking_status == "error":
                st.error(st.session_state.appointment_booking_message)
            st.session_state.appointment_booking_status = None

        st.write(f"Available Time Slots: {len(timings)}/{len(availability)}")
        cols = st.columns(6)
        for row in range(len(availability)//6):
            for col in range(6):
                index = row*6 + col
                if index < len(availability):
                    x = availability[index]
                    disabled = x not in timings or datetime.now() >  datetime.combine(appointment_date, datetime.strptime(f"{x//60:02d}:{x%60:02d}:00", "%H:%M:%S").time())
                    with cols[col]:
                        if st.form_submit_button(f"{x//60:02d}:{x%60:02d}", key=f"appointment_time_{index}", disabled=disabled):
                            try:
                                start_time = f"{x//60:02d}:{x%60:02d}:00"
                                add_appointment(patient[0], doctor[0], appointment_date, start_time, reason=illness, notes="", medication="")
                                st.session_state.appointment_booking_status = "success"
                                st.session_state.appointment_booking_message = "Appointment booked successfully"
                            except Exception as e:
                                st.session_state.appointment_booking_status = "error"
                                st.session_state.appointment_booking_message = f"Failed to book appointment: {e}"
                            st.rerun()
    go_back_button()

def page_schedule_appointment():
    st.write("## Schedule")
    doctors = show_doctors()
    doctor = st.selectbox("Doctor", doctors, format_func=lambda x: f"{x[1]}")
    appointments = show_appointments_for_doctor(doctor[0])
    # composite index on Appointment Date + Appointment Time
    # index = pd.MultiIndex.from_tuples([(x[3], x[4]) for x in appointments]) if len(appointments) > 0 else None
    index = None
    appointments_df = pd.DataFrame(appointments, columns=["Appointment ID", "Patient ID", "Patient Name", "Appointment Date", "Appointment Time", "Status", "Reason", "Notes", "Medication", "Bill", "Bill Status"],
                                index=index)
    appointments_df = appointments_df.drop(columns=["Appointment ID", "Patient ID", "Notes", "Medication"])

    # reformat Appointment Time to HH:MM:SS
    appointments_df["Appointment Time"] = appointments_df["Appointment Time"].apply(lambda x: f"{int(x.total_seconds()//60//60):02d}:{int((x.total_seconds()//60)%60):02d}:00")
    st.dataframe(appointments_df, width='stretch', hide_index=True)

    with st.form("delete_appointment_form"):
        if "appointment_deletion_status" in st.session_state and st.session_state.appointment_deletion_status is not None:
            if st.session_state.appointment_deletion_status == "success":
                st.success(st.session_state.appointment_deletion_message)
            elif st.session_state.appointment_deletion_status == "error":
                st.error(st.session_state.appointment_deletion_message)
            st.session_state.appointment_deletion_status = None

        appointment = st.selectbox("Appointments", appointments, format_func=lambda x: f"{x[3]} {x[4]} - {x[2]}") 
        if st.form_submit_button("Delete Appointment"):
            try:
                delete_appointment(appointment[0])
                st.session_state.appointment_deletion_status = "success"
                st.session_state.appointment_deletion_message = "Appointment deleted successfully"
            except Exception as e:
                st.error(f"Failed to delete appointment: {e}")
                st.session_state.appointment_deletion_status = "error"
                st.session_state.appointment_deletion_message = f"Failed to delete appointment: {e}"
            st.rerun()

    go_back_button()    

## Consultation pages
def page_consult():
    st.write("## Consult")
    patients = show_patient()
    patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
    appointments = show_appointments_for_patient(patient[0])
    # columns: appointment_id, doctor_id, doctor_name, appointment_date, appointment_time, status, reason, notes, medication
    appointments = [x for x in appointments if x[5] == "Pending"]
    if len(appointments) == 0:
        st.error("The Patient has no pending appointments to start consultation. Please book an appointment first.")
        go_back_button()
        return
    with st.form("consult_form"):
        appointment = st.selectbox("Appointments", options=appointments, format_func=lambda x: f"{x[3]} {x[4]} - {x[2]}  - {x[6]}")
        if st.form_submit_button("Start Consult"):
            try:
                update_appointment_status(appointment[0], "Confirmed")
                st.success("Consult confirmed successfully")
            except Exception as e:
                st.error(f"Failed to confirm consult: {e}")
    go_back_button()

def page_prescriptions():
    st.write("## Prescriptions")
    patients = show_patient()
    patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
    appointments = show_appointments_for_patient(patient[0])
    confirmed_appointments = [x for x in appointments if x[5] == "Confirmed" or x[5] == "Completed"]
    # columns: appointment_id, doctor_id, doctor_name, appointment_date, appointment_time, status, reason, notes, medication
    appointment = st.selectbox("Appointments", options=confirmed_appointments, format_func=lambda x: f"{x[3]} {x[4]} - {x[2]}  - {x[6]}")
    if appointment is None or len(appointment) == 0:
        st.error("No confirmed appointments found or User has not started consultation yet. Please consult the doctor first.")
        go_back_button()
        return
    with st.form("prescriptions_form"):
        col1,col2 = st.columns(2)
        with col1:
            notes = st.text_area("Notes", value=appointment and appointment[7] or "", height=200)
            prescription = st.text_area("Prescription", value=appointment and appointment[8] or "", height=200)
        with col2:
            if st.form_submit_button("Preview"):
                st.markdown(f"**Notes:**\n\n{notes}\n\n**Prescription:**\n\n{prescription}")
        if st.form_submit_button("Save Prescription"):
            try:
                update_appointment_status(appointment[0], "Completed")
                st.success("Marked as completed successfully")
                add_prescription(appointment[0], notes, prescription)
                st.success("Prescription added successfully")
            except Exception as e:
                st.error(f"Failed to save prescription: {e}")
        
    go_back_button()

def download_bill_and_prescription(appointment: tuple):

    # fields: 0 appointment_id, 1 doctor_id, 2 doctor_name, 3 appointment_date, 4 appointment_time, 5 status, 6 reason, 7 notes, 8 medication, 9 bill, 10 bill_status, 11 patient_name
    notes = appointment[7] or "N/A"
    medication = appointment[8] or "N/A"
    bill_total = appointment[9] or "0"
    patient_name = appointment[11]
    doctor_name = appointment[2]
    appt_date = appointment[3]
    appt_time = appointment[4]
    bill_status = appointment[10]
        
    txt_data = f"""
VYY HOSPITAL
Hulimavu, Bangalore
==================================
PRESCRIPTION
==================================

Patient:    {patient_name}
Doctor:     {doctor_name}
Date:       {appt_date}
Time:       {appt_time}

-------

Notes:
{notes}

Medication:
{medication}

==================================
Bill Receipt
==================================

Status:     {bill_status}
Amount:     ${bill_total}

==================================
Thank you!

powered by Medicare!
"""

    st.download_button(
            label="Download Bill & Prescription (.txt)",
            data=txt_data,
            file_name=f"bill_{patient_name}_{appointment[0]}.txt",
            mime="text/plain"
        )

def page_billing():
    
    st.write("## Billing")
    patients = show_patient()
    patient = st.selectbox("Patients", patients, format_func=lambda x: f"{x[1]}")
    appointments = show_appointments_for_patient(patient[0])
    # fields: 0 appointment_id, 1 doctor_id, 2 doctor_name, 3 appointment_date, 4 appointment_time, 5 status, 6 reason, 7 notes, 8 medication, 9 bill, 10 bill_status, 11 patient_name
    completed_appointments = [x for x in appointments if x[5] == "Completed"]
    appointment = st.selectbox("Appointments", completed_appointments, format_func=lambda x: f"{x[3]} {x[4]} - {x[2]}  - {x[6]}")
    if appointment is None or len(appointment) == 0:
        st.error("No completed appointments found for billing. Please complete the booking and consultation first.")
        go_back_button()
        return

    bill_status = get_latest_bill_status(appointment[0]) or "Pending"
    
    st.badge(bill_status, icon=":material/payment:")
    if appointment is not None and len(appointment) > 0 and bill_status == "Pending":
        with st.form("billing_form"):
            bill = st.number_input("Bill", value=int(appointment[9] or "0"), min_value=0, max_value=1000000, step=100)
            if st.form_submit_button("Generate Bill"):
                try:
                    update_appointment_bill(appointment[0], amount=bill, bill_status="Pending")
                    st.success("Billing status updated successfully")
                except Exception as e:
                    st.error(f"Failed to update billing status: {e}")
            if st.form_submit_button("Pay Bill"):
                try:
                    update_appointment_bill(appointment[0], amount=bill, bill_status="Paid")
                    st.success("Appointment status updated successfully")
                    st.session_state.billing_status = "success"
                    st.session_state.billing_message = "Bill paid successfully"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to pay bill: {e}")
                    st.session_state.billing_status = "error"
                    st.session_state.billing_message = f"Failed to pay bill: {e}"
                    st.rerun()
    else:
        download_bill_and_prescription(appointment)
    go_back_button()

def page_export_data():
    st.write("## Export Data")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<b>Export Patient Data</b>", unsafe_allow_html=True)
        try:
            patient_data = show_patient(order_by="patient_id asc")
            patient_headers = ["patient_id", "name", "dob", "gender", "blood_grp", "illness", "address", "contact_number", "email"]
            
            patient_csv_buffer = io.StringIO()
            patient_writer = csv.writer(patient_csv_buffer)
            patient_writer.writerow(patient_headers)
            patient_writer.writerows(patient_data)
            
            st.download_button(
                label="Download All Patients (.csv)",
                data=patient_csv_buffer.getvalue(),
                file_name="patients_export.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Failed to generate patient CSV: {e}")

    with col2:
        st.markdown("<b>Export Doctor Data</b>", unsafe_allow_html=True)
        try:
            doctor_data = show_doctors()
            doctor_headers = ["doctor_id", "name", "specialty", "phno", "email", "address"]
            
            doctor_csv_buffer = io.StringIO()
            doctor_writer = csv.writer(doctor_csv_buffer)
            doctor_writer.writerow(doctor_headers)
            doctor_writer.writerows(doctor_data)
            
            st.download_button(
                label="Download All Doctors (.csv)",
                data=doctor_csv_buffer.getvalue(),
                file_name="doctors_export.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Failed to generate doctor CSV: {e}")
        
    go_back_button()

def page_patient_consultation_workflow():
    st.write("## Patient Consultation Workflow")
    st.page_link(patient_page, label="New Patient", icon=":material/person_add:")
    st.markdown("<span style='padding-left: 75px;'>&#8595;</span>", unsafe_allow_html=True)
    st.page_link(assign_doctor_page, label="Assign Doctor", icon=":material/assignment_ind:")
    st.markdown("<span style='padding-left: 75px;'>&#8595;</span>", unsafe_allow_html=True)
    st.page_link(appointment_page, label="Book Appointment", icon=":material/event_available:")
    st.markdown("<span style='padding-left: 75px;'>&#8595;</span>", unsafe_allow_html=True)
    st.page_link(consult_page, label="Consult", icon=":material/stethoscope:")
    st.markdown("<span style='padding-left: 75px;'>&#8595;</span>", unsafe_allow_html=True)
    st.page_link(prescriptions_page, label="Prescriptions", icon=":material/medication:")
    st.markdown("<span style='padding-left: 75px;'>&#8595;</span>", unsafe_allow_html=True)
    st.page_link(billing_page, label="Billing", icon=":material/logout:")

# Pages

login_page = st.Page(login, title="Login")
logout_page = st.Page(logout, title="Logout")
patient_page = st.Page(page_new_patient, title="New Patient")
assign_doctor_page = st.Page(page_assign_doctor, title="Assign Doctor")
search_patient_page = st.Page(page_search_patient, title="Search Patient")
patient_details_page = st.Page(page_patient_details, title="Patient Details")
doctor_page = st.Page(page_new_doctor, title="New Doctor")
search_doctor_page = st.Page(page_search_doctor, title="Search Doctor")
doctor_details_page = st.Page(page_doctor_details, title="Doctor Details")
appointment_page = st.Page(page_appointment_new, title="New Appointment")
schedule_page = st.Page(page_schedule_appointment, title="Schedules")
consult_page = st.Page(page_consult, title="Consult")
prescriptions_page = st.Page(page_prescriptions, title="Prescriptions")
billing_page = st.Page(page_billing, title="Billing")
patient_consultation_workflow_page = st.Page(page_patient_consultation_workflow, title="Patient Consultation Workflow")
export_data_page = st.Page(page_export_data, title="Export Data")

if st.session_state.logged_in:
    pg = st.navigation({
        "Workflows": [patient_consultation_workflow_page],
        "Patients": [patient_page, assign_doctor_page, search_patient_page, patient_details_page],
        "Appointments": [appointment_page, schedule_page],
        "Consultations": [consult_page, prescriptions_page, billing_page],
        "Doctors": [doctor_page, search_doctor_page, doctor_details_page],
        "Admin": [export_data_page],
        "Logout": [logout_page],
    })
else:
    pg = st.navigation([login_page])

pg.run()
