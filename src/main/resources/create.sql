CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int CHECK (Doses>=0),
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    appID varchar(255),
    Time date,
    patient_name varchar(255) REFERENCES Patients, 
    caregiver_name varchar(255) REFERENCES Caregivers,
    vaccine_name varchar(255) REFERENCES Vaccines,
    PRIMARY KEY (appID)
);