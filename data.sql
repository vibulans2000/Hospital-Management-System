CREATE DATABASE IF NOT EXISTS hospital;
USE hospital;

DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id   INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    specialty   VARCHAR(100),
    phno        VARCHAR(20) NOT NULL UNIQUE,
    email       VARCHAR(100) UNIQUE,
    address     VARCHAR(255),
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS patients (
    patient_id      INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL UNIQUE,
    dob             DATE,
    gender          VARCHAR(1) CHECK (gender IN ('m','f')),
    blood_grp       VARCHAR(5),
    illness         VARCHAR(255),
    address         VARCHAR(255),
    contact_number  VARCHAR(20) NOT NULL UNIQUE,
    email           VARCHAR(100) UNIQUE,
    doctor_id       INT,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    appointment_date DATE,
    appointment_time TIME,
    status VARCHAR(20) CHECK (status IN ('Pending','Confirmed', 'Cancelled', 'Completed', 'Rescheduled')) DEFAULT 'Pending',
    reason VARCHAR(255),
    notes VARCHAR(255),
    medication VARCHAR(255),
    bill DECIMAL(10, 2) DEFAULT 0,
    bill_status VARCHAR(20) CHECK (bill_status IN ('Pending', 'Paid', 'Cancelled')) DEFAULT 'Pending',
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
);


INSERT INTO doctors (name, specialty, phno, email, address) VALUES
('Dr. Alice Smith', 'Cardiology', '555-123-4567', 'alice.smith@hospital.com', '101 Oak St, Springfield'),
('Dr. Bob Johnson', 'Pediatrics', '555-987-6543', 'bob.johnson@hospital.com', '202 Pine Ln, Springfield'),
('Dr. Emily Davis', 'Neurology', '555-246-8012', 'emily.davis@hospital.com', '303 Maple Ave, Springfield');

INSERT INTO patients (name, dob, gender, blood_grp, illness, address, contact_number, email) VALUES
('John Doe', '1985-03-22', 'm', 'A+', 'Hypertension','404 Birch Rd, Shelbyville', '555-555-1111', 'john.doe@email.com'),
('Jane Ryan', '1992-11-01', 'f', 'O-', 'Asthma', '505 Cedar Ct, Capital City', '555-666-2222', 'jane.ryan@email.com'),
('Mike Wilson', '2015-07-10', 'm', 'B+', 'Concussion', '606 Elm Blvd, Springfield', '555-777-3333', 'mike.wilson@email.com'),
('Sarah Brown', '1988-06-15', 'f', 'AB+', 'Diabetes', '707 Walnut Dr, Capital City', '555-888-4444', 'sarah.brown@email.com'),
('David Lee', '1975-09-30', 'm', 'O+', 'Hypertension', '808 Oak St, Shelbyville', '555-999-5555', 'david.lee@email.com'),
('Laura Martinez', '2000-02-28', 'f', 'A-', 'Asthma', '909 Pine Ln, Springfield', '555-101-6666', 'laura.martinez@email.com'),
('James Garcia', '1995-12-12', 'm', 'B-', 'Concussion', '1010 Maple Ave, Capital City', '555-112-7777', 'james.garcia@email.com'),
('Olivia Hernandez', '1982-05-05', 'f', 'AB-', 'Diabetes', '1111 Elm Blvd, Springfield', '555-123-8888', 'olivia.hernandez@email.com'),
('William Clark', '1978-08-18', 'm', 'O-', 'Hypertension', '1212 Pine Ln, Capital City', '555-134-9999', 'william.clark@email.com'),
('Sophia Rodriguez', '2005-04-14', 'f', 'A+', 'Asthma', '1313 Maple Ave, Springfield', '555-145-0000', 'sophia.rodriguez@email.com'),
('James Martinez', '1990-11-22', 'm', 'B+', 'Concussion', '1414 Elm Blvd, Capital City', '555-156-1111', 'james.martinez@email.com'),
('Olivia Garcia', '1985-07-07', 'f', 'AB+', 'Diabetes', '1515 Pine Ln, Springfield', '555-167-2222', 'olivia.garcia@email.com'),
('William Rodriguez', '1972-03-19', 'm', 'O-', 'Hypertension', '1616 Maple Ave, Capital City', '555-178-3333', 'william.rodriguez@email.com');


INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes, medication, bill, bill_status) VALUES
(1, 1, '2025-11-11', '10:00:00', 'Confirmed', 'Headache', 'None', 'None', 0, 'Pending'),
(2, 2, '2025-11-11', '11:00:00', 'Confirmed', 'Fever', 'None', 'None', 100, 'Pending'),
(3, 3, '2025-11-11', '12:00:00', 'Confirmed', 'Cold', 'None', 'None', 100, 'Pending'),
(4, 3, '2025-11-11', '13:00:00', 'Confirmed', 'Headache', 'None', 'None', 200, 'Pending'),
(5, 3, '2025-11-11', '14:00:00', 'Confirmed', 'Fever', 'None', 'None', 300, 'Pending'),
(6, 3, '2025-11-11', '15:00:00', 'Confirmed', 'Cold', 'None', 'None', 100, 'Pending'),
(7, 1, '2025-11-11', '16:00:00', 'Pending', 'Headache', 'None', 'None', 100, 'Pending'),
(8, 2, '2025-11-11', '17:00:00', 'Pending', 'Fever', 'None', 'None', 100, 'Pending'),
(9, 3, '2025-11-11', '18:00:00', 'Pending', 'Cold', 'None', 'None', 100, 'Pending'),
(10, 3, '2025-11-11', '19:00:00', 'Pending', 'Headache', 'None', 'None', 100, 'Pending'),
(11, 3, '2025-11-11', '20:00:00', 'Pending', 'Fever', 'None', 'None', 100, 'Pending'),
(12, 3, '2025-11-11', '21:00:00', 'Pending', 'Cold', 'None', 'None', 100, 'Pending');