import tkinter as tk
from tkinter import messagebox

def validar_numero(texto: str, nombre: str) -> float:
    if not texto.strip():
        raise ValueError(f"El campo '{nombre}' es obligatorio.")
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"El campo '{nombre}' debe ser un número válido.")
    
class Calculadora:
    def __init__(self, ventana: tk.Tk):
        self.ventana = ventana
        self.ventana.title("Calculadora")
        self.ventana.geometry("320x260")
        self.ventana.resizable(False, False)

        tk.Label(ventana, text="Número 1:").pack(pady=(10, 0))
        self.entrada1 = tk.Entry(ventana)
        self.entrada1.pack()

        tk.Label(ventana, text="Número 2:").pack(pady=(10, 0))
        self.entrada2 = tk.Entry(ventana)
        self.entrada2.pack()

        botones = tk.Frame(ventana)
        botones.pack(pady=12)
        for simbolo in ["+", "-", "*", "/"]:
            tk.Button(botones, text=simbolo, width=4,
                      command=lambda s=simbolo: self.calcular(s)).pack(side="left", padx=4)

        tk.Button(ventana, text="Limpiar", command=self.limpiar).pack()

        self.etiqueta = tk.Label(ventana, text="Resultado: -", font=("Arial", 14, "bold"))
        self.etiqueta.pack(pady=12)

    def calcular(self, operador: str):
        try:
            a = validar_numero(self.entrada1.get(), "Número 1")
            b = validar_numero(self.entrada2.get(), "Número 2")

            if operador == "+":
                resultado = a + b
            elif operador == "-":
                resultado = a - b
            elif operador == "*":
                resultado = a * b
            else:
                if b == 0:
                    raise ZeroDivisionError("No se puede dividir entre cero.")
                resultado = a / b

            self.etiqueta.config(text=f"Resultado: {format(resultado, '.10g')}")
        except ZeroDivisionError as e:
            messagebox.showerror("Error matemático", str(e))
        except ValueError as e:
            messagebox.showerror("Datos no válidos", str(e))

    def limpiar(self):
        self.entrada1.delete(0, tk.END)
        self.entrada2.delete(0, tk.END)
        self.etiqueta.config(text="Resultado: -")
        self.entrada1.focus()

if __name__ == "__main__":
    raiz = tk.Tk()
    Calculadora(raiz)
    raiz.mainloop()