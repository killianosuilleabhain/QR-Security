import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import qrcode

class QRCodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")

        # Enter text or Link
        self.label_text = tk.StringVar()
        self.label_text.set("Enter text to generate QR code:")
        self.label = tk.Label(root, textvariable=self.label_text, width=50)
        self.label.pack(pady=10)

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(root, textvariable=self.entry_text, width=50)
        self.entry.pack(pady=10)

        # Enter text for file name
        self.filename_label = tk.Label(root, text="Enter filename (without extension):")
        self.filename_label.pack(pady=5)

        self.filename_entry_text = tk.StringVar()
        self.filename_entry = tk.Entry(root, textvariable=self.filename_entry_text, width=50)
        self.filename_entry.pack(pady=5)

        # Generate Button 
        self.generate_button = tk.Button(root, text="Generate QR Code", command=self.generate_qr_code)
        self.generate_button.pack(pady=10)

        # Displays Qr Code
        self.qr_image_label = tk.Label(root)
        self.qr_image_label.pack(pady=10)

    def generate_qr_code(self):
        data = self.entry.get()
        filename = self.filename_entry.get()

        if data:
            if not filename:
                filename = "qrcode"

            # Creates Qr Code
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(data)
            qr.make(fit=True)

            # Generates QR Image & picks colour
            img = qr.make_image(fill_color="black", back_color="white")

            # Save As 
            file_path = f"{filename}.png"
            img.save(file_path)

            # Message box Confirmiing Save 
            messagebox.showinfo("QR Code Generated", f"QR Code saved as {file_path}")

            # Display the generated QR code in the GUI
            qr_image = Image.open(file_path)
            qr_image = ImageTk.PhotoImage(qr_image)
            self.qr_image_label.config(image=qr_image)
            self.qr_image_label.image = qr_image
        # Warns users of no input
        else:
            messagebox.showwarning("Empty Input", "Please enter text to generate QR code.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGenerator(root)
    root.mainloop()
