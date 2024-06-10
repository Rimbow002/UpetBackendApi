import random
import string
import pytz
import operator
from datetime import datetime
from sqlalchemy.orm import Session
from models.otps import OTP
from config.db import get_db
from fastapi import HTTPException, status, Depends
from models.appointment import Appointment
from models.pet import Pet
from models.veterinarian import Veterinarian
from schemas.appointment import AppointmentSchemaGet, AppointmentSchemaPost

class AppointmentService:

    @staticmethod
    def get_all_appointments(db: Session):
        appointments = db.query(Appointment).all()
        appointments_list = []
        for appointment in appointments:
            appointment_data = AppointmentSchemaGet.from_orm(appointment)
            appointments_list.append(appointment_data)
        return appointments_list


    @staticmethod
    def get_appointments_by_pet_id(pet_id: int, db: Session):
        pet = db.query(Pet).filter(Pet.id == pet_id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La mascota no existe.")
        appointments = db.query(Appointment).filter(Appointment.pet_id == pet_id).all()
        if not appointments:
            print("La mascota no tiene citas registradas.")
        return appointments
    
    @staticmethod
    def get_appointments_by_owner_id(owner_id: int, db: Session):
        pets = db.query(Pet).filter(Pet.petOwnerId == owner_id).all()
        if not pets:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El dueño no tiene mascotas registradas.")
        appointments_list = []
        for pet in pets:
            appointments = db.query(Appointment).filter(Appointment.pet_id == pet.id).all()
            for appointment in appointments:
                appointment_data = AppointmentSchemaGet.from_orm(appointment)
                appointments_list.append(appointment_data)
        return appointments_list
    
    @staticmethod
    def get_appointments(query, time_comparison_operator):
        appointments_list = []
        for item in query.all():
            appointments = item.appointments
            for appointment in appointments:
                appointment_datetime = datetime.combine(appointment.date_day, appointment.start_time)
                appointment_datetime = pytz.timezone('America/Lima').localize(appointment_datetime).astimezone(pytz.UTC)
                current_time = datetime.now(pytz.timezone('America/Lima')).astimezone(pytz.UTC)
                if time_comparison_operator(appointment_datetime, current_time):
                    appointment_data = AppointmentSchemaGet.from_orm(appointment)
                    appointments_list.append((appointment_datetime, appointment_data))
        reverse_order = False if time_comparison_operator == operator.ge else True            
        appointments_list = sorted(appointments_list, key=lambda a: a[0], reverse=reverse_order)
        return [appointment for _, appointment in appointments_list]
    
    @staticmethod
    def get_upcoming_appointments_by_owner_id(owner_id: int, db: Session):
        pets = db.query(Pet).filter(Pet.petOwnerId == owner_id)
        if not pets.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El dueño no tiene mascotas registradas.")
        return AppointmentService.get_appointments(pets, operator.ge)
    
    @staticmethod
    def get_past_appointments_by_owner_id(owner_id: int, db: Session):
        pets = db.query(Pet).filter(Pet.petOwnerId == owner_id)
        if not pets.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El dueño no tiene mascotas registradas.")
        return AppointmentService.get_appointments(pets, operator.lt)
    
    @staticmethod
    def get_past_appointments_by_veterinarian_id(veterinarian_id: int, db: Session):
        veterinarian = db.query(Veterinarian).filter(Veterinarian.id == veterinarian_id)
        if not veterinarian.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El veterinario no existe.")
        return AppointmentService.get_appointments(veterinarian, operator.lt)
    
    @staticmethod
    def get_upcoming_appointments_by_veterinarian_id(veterinarian_id: int, db: Session):
        veterinarian = db.query(Veterinarian).filter(Veterinarian.id == veterinarian_id)
        if not veterinarian.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El veterinario no existe.")
        return AppointmentService.get_appointments(veterinarian, operator.ge)
        
        
    @staticmethod
    def get_appointments_by_veterinarian_id(veterinarian_id: int, db: Session):
        veterinarian = db.query(Veterinarian).filter(Veterinarian.id == veterinarian_id).first()
        if not veterinarian:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El veterinario no existe.")
        appointments = db.query(Appointment).filter(Appointment.veterinarian_id == veterinarian_id).all()
        if not appointments:
            print("El veterinario no tiene citas registradas.")
        return appointments
    
    def get_appointment_by_id(appointment_id: int, db: Session):
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La cita no existe.")
        return appointment

    @staticmethod
    def create_appointment(appointment: AppointmentSchemaPost, db: Session):

        pet = db.query(Pet).filter(Pet.id == appointment.pet_id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La mascota no existe.")
        
        veterinarian = db.query(Veterinarian).filter(Veterinarian.id == appointment.veterinarian_id).first()
        if not veterinarian:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El veterinario no existe.")
        
        new_appointment = appointment.to_model()
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
