import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import mysql.connector


class DatabaseConnect:
    def __init__(self):
        # would need to edit these details based on environment
        # columns in database expected --> id serial, name varchar(255), course varchar(100), mobile int
        self.host = "localhost"
        self.user = "root"
        self.password = "python123"
        self.database = "school"
        self.connection = mysql.connector.connect(host=self.host,
                                                  user=self.user,
                                                  password=self.password,
                                                  database=self.database)
        self.cursor = self.connection.cursor()
    def db_cursor(self):
        return self.cursor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(700, 500)

        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")
        edit_menu = self.menuBar().addMenu("&Edit")

        add_student = QAction(QIcon("icons/add.png"),"Add Student", self)
        add_student.triggered.connect(self.insert_record)
        file_menu.addAction(add_student)

        about = QAction("About", self)
        help_menu.addAction(about)

        search = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu.addAction(search)
        search.triggered.connect(self.search_record)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student)
        toolbar.addAction(search)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_data(self):
        db_connection = DatabaseConnect()
        cursor = db_connection.db_cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        cursor.close()
        db_connection.connection.close()

    def insert_record(self):
        dialog = InsertDialog()
        dialog.exec()
    def search_record(self):
        dialog_2 = SearchDialog()
        dialog_2.exec()
    def cell_clicked(self):
        edit_button = QPushButton(QIcon("icons/edit.png"), "Edit")
        delete_button = QPushButton(QIcon("icons/delete.png"), "Delete")

        edit_button.clicked.connect(self.edit_record)
        delete_button.clicked.connect(self.delete_record)

        children = self.status_bar.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)
    def edit_record(self):
        dialog_3 = EditDialog()
        dialog_3.exec()
    def delete_record(self):
        dialog_4 = DeleteDialog()
        dialog_4.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Creating widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        self.course_select = QComboBox()
        self.course_select.addItems(["Math", "Astronomy", "Biology", "Physics"])
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")
        submit_button = QPushButton("Register")

        # Placing widgets on layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.course_select)
        layout.addWidget(self.phone)
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_select.currentText()
        mobile = self.phone.text()
        db_connection = DatabaseConnect()
        cursor = db_connection.db_cursor()
        cursor.execute("INSERT INTO students (name, course, phone) VALUES (%s, %s, %s)", (name, course, mobile))
        db_connection.connection.commit()
        cursor.close()
        db_connection.connection.close()
        student_database.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Creating widgets
        self.search_data = QLineEdit()
        self.search_data.setPlaceholderText("Search")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_student)

        # add widgets
        layout.addWidget(self.search_data)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def search_student(self):
        student_database.load_data()
        name = self.search_data.text()
        db_connection = DatabaseConnect()
        cursor = db_connection.db_cursor()
        cursor.execute(f"SELECT name from students WHERE name LIKE '{name}%'")
        search_query = cursor.fetchall()
        high_data = []
        for name in search_query:
            high_data.append(student_database.table.findItems(name[0], Qt.MatchFlag.MatchFixedString))
        for x in range(len(high_data)):
            for data in high_data[x]:
                student_database.table.item(data.row(), 1).setSelected(True)
        cursor.close()
        db_connection.connection.close()
        self.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Creating widgets
        self.student_name = QLineEdit()
        self.course_select = QComboBox()
        self.course_select.addItems(["Math", "Astronomy", "Biology", "Physics"])

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")
        submit_button = QPushButton("Update")

        # Getting current name from main window
        self. index_of_row = student_database.table.currentRow()
        name_to_edit = student_database.table.item(self.index_of_row, 1).text()
        self.student_name.setText(name_to_edit)

        # Getting current default for ComboBox
        course_to_edit = student_database.table.item(self.index_of_row, 2).text()
        self.course_select.setCurrentText(course_to_edit)

        # Getting current phone from main window
        phone_to_edit = student_database.table.item(self.index_of_row, 3).text()
        self.phone.setText(phone_to_edit)

        # Placing widgets on layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.course_select)
        layout.addWidget(self.phone)
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.update_student)

        self.setLayout(layout)

    def update_student(self):
        db_connection = DatabaseConnect()
        cursor = db_connection.db_cursor()
        student_id = student_database.table.item(self.index_of_row, 0).text()
        cursor.execute("UPDATE students SET name = %s, course = %s, phone = %s WHERE id = %s", (self.student_name.text(),
                                                                                             self.course_select.currentText(),
                                                                                             self.phone.text(),
                                                                                             student_id))
        db_connection.connection.commit()

        cursor.close()
        db_connection.connection.close()
        student_database.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student data")

        layout = QVBoxLayout()

        # Creating widgets
        self.confirmation_message = QLabel("Are you sure want to delete the record?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        # Placing widgets on layout
        layout.addWidget(self.confirmation_message)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        yes_button.clicked.connect(self.delete_student)
        no_button.clicked.connect(self.no_delete)

        self.setLayout(layout)

    def delete_student(self):
        index_to_delete = student_database.table.currentRow()
        id_to_delete = student_database.table.item(index_to_delete, 0).text()
        db_connection = DatabaseConnect()
        cursor = db_connection.db_cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (id_to_delete, ))
        db_connection.connection.commit()
        cursor.close()
        db_connection.connection.close()
        student_database.load_data()
        self.close()
        success = QMessageBox()
        success.setWindowTitle("Delete Success")
        success.setText("Student Record removed")
        success.exec()

    def no_delete(self):
        self.close()
        success = QMessageBox()
        success.setWindowTitle("Delete Aborted")
        success.setText("Student Record not removed")
        success.exec()


app = QApplication(sys.argv)
student_database = MainWindow()
student_database.load_data()
student_database.show()
sys.exit(app.exec())