import streamlit as st
import mysql.connector as mysql


if "mycon" not in st.session_state:
    st.session_state.mycon = mysql.connect(host = "localhost", user = "admin", password = "password", database = "hospital")

if "cur" not in st.session_state:
    st.session_state.cur = st.session_state.mycon.cursor()

mycon = st.session_state.mycon
cur = st.session_state.cur

def myfn():
    st.write("# My Func")

def suresh(): 
    st.write("# Suresh")

# DB functions

def create_new_patient(name, dob, gender):
    #cur.execute(f"""insert into patient(name, dob, gender) values("{name}", "{dob}", "{gender}");""")
    cur.execute(f"""insert into patient(name, dob, gender) values(%s,%s,%s);""", (name, dob,gender,))
    mycon.commit()   #   inset into patient(name, dob, gender) values("John", "2009-12-12", "Male");
    return cur.lastrowid


# End of DB functions

def patient_new_registration():
    st.write("# New Registration")

    with st.form("NewRegForm"):
        name = st.text_input("Name")
        dob = st.text_input("DOB")
        gender = st.selectbox("Gender", ["Male", "Female"] )

        if st.form_submit_button("Submit"):
            try:
                patient_id = create_new_patient(name, dob, gender)
                st.success("Created new patient! id is %s" % (patient_id,))
            except Exception as e:
                st.error(e)
            


patient_NewReg = st.Page(patient_new_registration, title = "New Registration")
page1 = st.Page(myfn, title="Management")
page2 = st.Page(suresh, title="Settings")
pg = st.navigation({
    'Patient': [patient_NewReg],
    'Accounts': [page1],
    'Reports': [page2]
})



pg.run()