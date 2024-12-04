import customtkinter as ctk
from tkinter import messagebox, Listbox
from tkcalendar import Calendar
import mysql.connector
from datetime import date, timedelta


class DatabaseManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hospital"
        )
        self.cursor = self.conn.cursor()

    def registrar_usuario(self, correo, contraseña):
        try:
            self.cursor.execute("INSERT INTO usuarios (correo, contraseña) VALUES (%s, %s)", (correo, contraseña))
            self.conn.commit()
            return True
        except mysql.connector.Error:
            return False

    def verificar_usuario(self, correo, contraseña):
        self.cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND contraseña = %s", (correo, contraseña))
        return self.cursor.fetchone()

    def agendar_cita(self, usuario_id, fecha, hora, doctor):
        try:
            self.cursor.execute("INSERT INTO citas (fecha, hora, usuario_id, doctor) VALUES (%s, %s, %s, %s)",
                                (fecha, hora, usuario_id, doctor))
            self.conn.commit()
            return True
        except mysql.connector.Error:
            return False

    def verificar_disponibilidad(self, fecha, hora):
        self.cursor.execute("SELECT id FROM citas WHERE fecha = %s AND hora = %s", (fecha, hora))
        return self.cursor.fetchone() is None

    def obtener_citas(self, usuario_id):
        self.cursor.execute("SELECT id, fecha, hora, doctor, motivo FROM citas WHERE usuario_id = %s", (usuario_id,))
        return self.cursor.fetchall()

    def cancelar_cita(self, cita_id):
        self.cursor.execute("DELETE FROM citas WHERE id = %s", (cita_id,))
        self.conn.commit()

    def actualizar_motivo(self, cita_id, motivo):
        self.cursor.execute("UPDATE citas SET motivo = %s WHERE id = %s", (motivo, cita_id))
        self.conn.commit()

    def cerrar(self):
        self.conn.close()


class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Gestión de Citas")
        self.ventana.geometry("600x600")
        self.ventana.resizable(width=False, height=False)
        self.db_manager = DatabaseManager()
        self.usuario_id = None
        # Doctores asignados
        self.doctores = [
            "Dr. RODOLFO BERNIER",
            "Dr. JOAQUIN CARRILLO",
            "Dr. NICOLAS DONOSO",
            "Dr. JOAQUIN CORONADO",
            "Dr. MATIAS GUZMAN",
            "Dr. ARTURO SEPULVEDA"
        ]
        self.limpiar_ventana()
        self.cambiar_a_principal()

    def limpiar_ventana(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()

    def cambiar_a_principal(self):
        self.limpiar_ventana()
        ctk.CTkLabel(self.ventana, text="Bienvenido", font=("Arial", 30), text_color="white").pack(pady=40)
        ctk.CTkButton(self.ventana, text="Iniciar Sesión", command=self.cambiar_a_inicio_sesion, width=200).pack(pady=20)
        ctk.CTkButton(self.ventana, text="Registrarse", command=self.cambiar_a_registro, width=200).pack(pady=20)

    def cambiar_a_inicio_sesion(self):
        self.limpiar_ventana()
        ctk.CTkLabel(self.ventana, text="Iniciar Sesión", font=("Arial", 26), text_color="white").place(x=180, y=50)
        ctk.CTkLabel(self.ventana, text="Correo:", font=("Arial", 15), text_color="white").place(x=150, y=120)
        correo = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", width=200)
        correo.place(x=150, y=150)
        ctk.CTkLabel(self.ventana, text="Contraseña:", font=("Arial", 15), text_color="white").place(x=150, y=190)
        contraseña = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", show="*", width=200)
        contraseña.place(x=150, y=220)
        ctk.CTkButton(self.ventana, text="Iniciar Sesión", command=lambda: self.validar_sesion(correo.get(), contraseña.get())).place(x=180, y=270)
        ctk.CTkButton(self.ventana, text="Regresar", command=self.cambiar_a_principal).place(x=180, y=320)

    def validar_sesion(self, correo, contraseña):
        usuario = self.db_manager.verificar_usuario(correo, contraseña)
        if usuario:
            self.usuario_id = usuario[0]
            messagebox.showinfo("Éxito", "Sesión iniciada correctamente.")
            self.mostrar_menu_usuario()
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    def cambiar_a_registro(self):
        self.limpiar_ventana()
        ctk.CTkLabel(self.ventana, text="Registro", font=("Arial", 26), text_color="white").place(x=220, y=50)
        ctk.CTkLabel(self.ventana, text="Correo:", font=("Arial", 15), text_color="white").place(x=150, y=120)
        correo = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", width=200)
        correo.place(x=150, y=150)
        ctk.CTkLabel(self.ventana, text="Contraseña:", font=("Arial", 15), text_color="white").place(x=150, y=190)
        contraseña = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", show="*", width=200)
        contraseña.place(x=150, y=220)
        ctk.CTkLabel(self.ventana, text="Confirmar Contraseña:", font=("Arial", 15), text_color="white").place(x=150, y=260)
        confirmar = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", show="*", width=200)
        confirmar.place(x=150, y=290)
        ctk.CTkButton(self.ventana, text="Registrar", command=lambda: self.validar_registro(correo.get(), contraseña.get(), confirmar.get())).place(x=180, y=350)
        ctk.CTkButton(self.ventana, text="Regresar", command=self.cambiar_a_principal).place(x=180, y=400)

    def validar_registro(self, correo, contraseña, confirmar):
        if not correo or not contraseña or not confirmar:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        if contraseña != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        if self.db_manager.registrar_usuario(correo, contraseña):
            messagebox.showinfo("Éxito", "Registro exitoso.")
            self.cambiar_a_inicio_sesion()
        else:
            messagebox.showerror("Error", "El correo ya está registrado.")

    def mostrar_menu_usuario(self):
        self.limpiar_ventana()
        ctk.CTkButton(self.ventana, text="Agendar Cita", command=self.agendar_cita).place(x=200, y=100)
        ctk.CTkButton(self.ventana, text="Ver Citas", command=self.ver_citas).place(x=200, y=150)
        ctk.CTkButton(self.ventana, text="Cancelar Cita", command=self.cancelar_cita).place(x=200, y=200)
        ctk.CTkButton(self.ventana, text="Cerrar Sesión", command=self.cerrar_sesion).place(x=200, y=250)

    def agendar_cita(self):
        self.limpiar_ventana()
        calendario = Calendar(self.ventana, selectmode='day', date_pattern='yyyy-mm-dd')
        calendario.place(x=150, y=50)
        horas_disponibles = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']
        ctk.CTkLabel(self.ventana, text="Seleccione la hora:", font=("Arial", 15), text_color="white").place(x=150, y=230)
        hora = ctk.CTkComboBox(self.ventana, values=horas_disponibles)
        hora.place(x=150, y=260)
        ctk.CTkButton(self.ventana, text="Agendar Cita", command=lambda: self.agendar_cita_en_base(calendario.get_date(), hora.get())).place(x=150, y=320)

    def agendar_cita_en_base(self, fecha, hora):
        if not self.db_manager.verificar_disponibilidad(fecha, hora):
            messagebox.showerror("Error", "La hora ya está ocupada.")
            return
        # Asignamos el doctor de forma balanceada
        doctor = self.doctores[self.usuario_id % len(self.doctores)]
        if self.db_manager.agendar_cita(self.usuario_id, fecha, hora, doctor):
            messagebox.showinfo("Éxito", f"Cita agendada con éxito con {doctor}.")
            self.pedir_motivo(fecha, hora, doctor)
        else:
            messagebox.showerror("Error", "Hubo un problema al agendar la cita.")

    def pedir_motivo(self, fecha, hora, doctor):
        self.limpiar_ventana()
        ctk.CTkLabel(self.ventana, text="Motivo de la Consulta", font=("Arial", 26), text_color="white").place(x=150, y=50)
        motivo = ctk.CTkEntry(self.ventana, fg_color="#eae5e3", text_color="black", width=300)
        motivo.place(x=150, y=150)
        ctk.CTkButton(self.ventana, text="Confirmar", command=lambda: self.guardar_motivo(fecha, hora, doctor, motivo.get())).place(x=230, y=200)

    def guardar_motivo(self, fecha, hora, doctor, motivo):
        citas = self.db_manager.obtener_citas(self.usuario_id)
        cita_id = citas[-1][0]  # Última cita agendada
        self.db_manager.actualizar_motivo(cita_id, motivo)
        messagebox.showinfo("Éxito", f"Motivo de consulta guardado: {motivo}")
        self.mostrar_menu_usuario()

    def ver_citas(self):
        citas = self.db_manager.obtener_citas(self.usuario_id)
        if not citas:
            messagebox.showinfo("Sin Citas", "No tienes citas agendadas.")
            return
        self.limpiar_ventana()
        listbox = Listbox(self.ventana, width=50, height=10)
        listbox.place(x=50, y=50)
        for cita in citas:
            listbox.insert(ctk.END, f"Fecha: {cita[1]} | Hora: {cita[2]} | Doctor: {cita[3]} | Motivo: {cita[4]}")
        ctk.CTkButton(self.ventana, text="Regresar", command=self.mostrar_menu_usuario).place(x=250, y=400)

    def cancelar_cita(self):
        citas = self.db_manager.obtener_citas(self.usuario_id)
        if not citas:
            messagebox.showinfo("Sin Citas", "No tienes citas agendadas para cancelar.")
            return
        self.limpiar_ventana()
        listbox = Listbox(self.ventana, width=50, height=10)
        listbox.place(x=50, y=50)
        for cita in citas:
            listbox.insert(ctk.END, f"Fecha: {cita[1]} | Hora: {cita[2]} | Doctor: {cita[3]} - ID: {cita[0]}")
        ctk.CTkButton(self.ventana, text="Cancelar Cita", command=lambda: self.eliminar_cita(listbox)).place(x=250, y=400)

    def eliminar_cita(self, listbox):
        try:
            cita_id = listbox.get(listbox.curselection()).split('ID: ')[1]
            self.db_manager.cancelar_cita(int(cita_id))
            messagebox.showinfo("Éxito", "Cita cancelada correctamente.")
            self.ver_citas()
        except:
            messagebox.showerror("Error", "No se pudo cancelar la cita.")
        
    def cerrar_sesion(self):
        self.usuario_id = None
        self.cambiar_a_principal()

if __name__ == "__main__":
    ventana = ctk.CTk()
    app = Aplicacion(ventana)
    ventana.mainloop()
