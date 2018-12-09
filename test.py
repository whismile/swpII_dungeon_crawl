from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QLineEdit, QToolButton,
                             QSizePolicy, QLayout,
                             QGridLayout, QLabel,
                             QVBoxLayout, QHBoxLayout,
                             QTextEdit, QComboBox,
                             QSpinBox)

import pickle
from calendarManager import myCalendar, myEvent
import time


class Button(QToolButton):

    def __init__(self, text, callback):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setText(text)

        self.clicked.connect(callback)

    def sizeHint(self):
        size = super(Button, self).sizeHint()
        size.setHeight(size.height() + 20)
        size.setWidth(max(size.width(), size.height()))
        return size


class Calendar(QWidget):

    def __init__(self, parent=None, year=int(time.strftime('%Y', time.localtime(time.time()))),
                 month=int(time.strftime('%m', time.localtime(time.time())))):
        super().__init__(parent)

        # variables
        self.displayCalendar = myCalendar()
        self.startDay = 0
        self.maxDay = 0
        self.currentYear = year
        self.currentMonth = month
        self.currentDay = 0
        self.firstClick = True
        self.fileRoot = "./schedules.txt"

        try:
            scheduleFile = open(self.fileRoot, "rb")
            self.displayCalendar.schedule = pickle.load(scheduleFile)
            print(self.displayCalendar.schedule)

        except EOFError:
            pass

        # main layout
        self.mainLayout = QHBoxLayout()
        # self.mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        # Left side Layout ================================
        self.leftLayout = QVBoxLayout()

        # handling month ----------------------------------
        self.moveMonth = QHBoxLayout()

        self.previousBtn = Button("<", self.previousMonth)

        # showing Year and month
        self.yearCombo = QComboBox()
        self.yearCombo.addItems([str(x) for x in range(1980, 2041)])
        self.yearCombo.setCurrentText(str(self.currentYear))

        self.monthCombo = QComboBox()
        self.monthCombo.addItems([str(x) for x in range(1, 13)])
        self.monthCombo.setCurrentText(str(self.currentMonth))

        self.nextBtn = Button(">", self.nextMonth)

        self.moveMonth.addStretch()
        self.moveMonth.addWidget(self.previousBtn)
        self.moveMonth.addWidget(self.yearCombo)
        self.moveMonth.addWidget(self.monthCombo)
        self.moveMonth.addWidget(self.nextBtn)
        self.moveMonth.addStretch()
        self.leftLayout.addLayout(self.moveMonth)
        self.leftLayout.addStretch()
        # -------------------------------------------------

        # Set Day of Week
        self.weekDayLayout = QHBoxLayout()
        enumDays = ["일", "월", "화", "수", "목", "금", "토"]

        for i in enumDays:
            label = QLabel(i)
            label.setAlignment(Qt.AlignCenter)
            self.weekDayLayout.addWidget(label)

        self.leftLayout.addLayout(self.weekDayLayout)

        # grid layout to appending date Buttons
        self.calendarGrid = QGridLayout()
        self.calendarGrid.setSizeConstraint(QLayout.SetFixedSize)
        self.leftLayout.addLayout(self.calendarGrid)
        self.leftLayout.addStretch(7)

        # showing status
        self.statusLabel = QLabel("btn Status")
        self.leftLayout.addWidget(self.statusLabel)
        # ==================================================

        # Schedules layout ==================================
        self.scheduleLayout = QVBoxLayout()
        self.titleBox = QHBoxLayout()
        self.titleLabel = QLabel("title: ")
        self.titleLineEdit = QLineEdit()
        self.titleBox.addWidget(self.titleLabel)
        self.titleBox.addWidget(self.titleLineEdit)

        self.placeBox = QHBoxLayout()
        self.placeLabel = QLabel("place: ")
        self.placeLineEdit = QLineEdit()
        self.placeBox.addWidget(self.placeLabel)
        self.placeBox.addWidget(self.placeLineEdit)

        self.dateBox = QHBoxLayout()
        self.dateLabel = QLabel("time:")

        self.fromHour = QSpinBox(); self.fromHour.setRange(0, 24)
        self.toHour = QSpinBox(); self.toHour.setRange(0, 24)
        self.fromMin = QSpinBox();self.fromMin.setRange(0, 59)
        self.toMin = QSpinBox(); self.toMin.setRange(0, 59)

        self.fromHour.valueChanged.connect(lambda: self.toHour.setRange(self.fromHour.value(), 24))
        # self.toHour.valueChanged.connect(lambda: self.fromHour.setRange(0, self.toHour.value()))

        self.fromMin.valueChanged.connect(lambda: self.toMin.setRange(self.fromMin.value(), 59))
        # self.toMin.valueChanged.connect(lambda: self.fromMin.setRange(0, self.toMin.value()))

        self.dateBox.addWidget(self.dateLabel)
        self.dateBox.addWidget(self.fromHour); self.dateBox.addWidget(self.fromMin)
        self.dateBox.addWidget(QLabel("    ~ "))
        self.dateBox.addWidget(self.toHour); self.dateBox.addWidget(self.toMin)

        self.discription = QHBoxLayout()
        self.content = QTextEdit()
        self.contentLabel = QLabel("content: ")
        self.contentLabel.setAlignment(Qt.AlignTop)
        self.discription.addWidget(self.contentLabel)
        self.discription.addWidget(self.content)

        self.scheduleLayout.addLayout(self.titleBox)
        self.scheduleLayout.addLayout(self.placeBox)
        self.scheduleLayout.addLayout(self.dateBox)
        self.scheduleLayout.addLayout(self.discription)
        # modifying schedule Button
        self.modifyBtn = Button("Modifying", self.modifying)
        self.scheduleLayout.addWidget(self.modifyBtn)

        self.hidingWidget(self.scheduleLayout)
        # ==================================================
        # Set grid
        self.displayCalendar.setCalander(self.currentYear, self.currentMonth)
        self.renderDate(self.displayCalendar.getCalander())

        # Set ComboBox Changing Event
        self.yearCombo.currentTextChanged.connect(lambda: self.selectionChanged())
        self.monthCombo.currentTextChanged.connect(lambda: self.selectionChanged())

        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.scheduleLayout)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Calendar")

    def renderDate(self, newCalendar):
        # =========== Append Day Buttons ===============
        self.clearLayout(self.calendarGrid)
        toggle = True

        # Enroll button
        for row, column in enumerate(newCalendar):
            for col, day in enumerate(column):
                btn = Button(str(day), self.btnEvent)

                # deactivate button condition
                if toggle:
                    if day != 1:
                        btn.setEnabled(False)

                    else:
                        toggle = False

                else:
                    if (row == len(newCalendar) - 1) and (day // 10 == 0):
                        btn.setEnabled(False)

                # 공휴일은 빨간색으로 설정해준다.
                if col == 0 and btn.isEnabled():
                    btn.setStyleSheet('color: red;')

                self.calendarGrid.addWidget(btn, row, col)
        # ===============================================

    def btnEvent(self):
        self.showingWidget(self.scheduleLayout)

        self.setFixedSize(self.mainLayout.sizeHint())

        btn = self.sender()
        self.statusLabel.setText("Day: " + btn.text() + " is Clicked.")
        self.currentDay = btn.text()

        target = "-".join([str(self.currentYear), str(self.currentMonth), str(self.currentDay)])
        targetEvent = self.displayCalendar.schedule.get(target)

        if not targetEvent:
            self.titleLineEdit.setText("None")
            self.placeLineEdit.clear()
            self.fromHour.setValue(0)
            self.fromMin.setValue(0)
            self.toHour.setValue(0)
            self.toMin.setValue(0)
            self.content.clear()

        else:
            self.titleLineEdit.setText(targetEvent.getTitle())
            self.placeLineEdit.setText(targetEvent.getPlace())

            timeSet = targetEvent.getDate().split(",")
            self.fromHour.setValue(int(timeSet[0]))
            self.fromMin.setValue(int(timeSet[1]))
            self.toHour.setValue(int(timeSet[2]))
            self.toMin.setValue(int(timeSet[3]))

            self.content.setText(targetEvent.getDiscription())

    def modifying(self):
        newEvent = myEvent()
        eventList = [self.titleLineEdit.text(),
                     self.placeLineEdit.text(),
                     ",".join([str(self.fromHour.value()), str(self.fromMin.value()),
                               str(self.toHour.value()), str(self.toMin.value())]),
                     self.content.toPlainText(),
                     ]

        newEvent.setEvent(*eventList)

        target = "-".join([str(self.currentYear), str(self.currentMonth), str(self.currentDay)])
        self.displayCalendar.schedule[target] = newEvent
        self.statusLabel.setText("modified")

    # rendering previous month calendar
    def previousMonth(self):
        if self.currentMonth is 1:
            self.currentYear -= 1
            self.yearCombo.setCurrentText(str(self.currentYear))
            self.currentMonth = 12
            self.monthCombo.setCurrentText(str(self.currentMonth))

        else:
            self.currentMonth -= 1
            self.monthCombo.setCurrentText(str(self.currentMonth))

    # rendering next month calendar
    def nextMonth(self):
        if self.currentMonth is 12:
            self.currentYear += 1
            self.yearCombo.setCurrentText(str(self.currentYear))
            self.currentMonth = 1
            self.monthCombo.setCurrentText(str(self.currentMonth))
        else:
            self.currentMonth += 1
            self.monthCombo.setCurrentText(str(self.currentMonth))

    def selectionChanged(self):
        self.currentYear = int(self.yearCombo.currentText())
        self.currentMonth = int(self.monthCombo.currentText())

        self.displayCalendar.setYear(self.currentYear)
        self.displayCalendar.setMonth(self.currentMonth)
        self.displayCalendar.setCalander(self.currentYear, self.currentMonth)
        self.renderDate(self.displayCalendar.getCalander())

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def closeEvent(self, event):
        with open(self.fileRoot, "wb") as file:
            pickle.dump(self.displayCalendar.schedule, file)

    def hidingWidget(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() is not None:
                layout.itemAt(i).widget().hide()
            elif item.layout() is not None:
                self.hidingWidget(layout.itemAt(i).layout())

    def showingWidget(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() is not None:
                layout.itemAt(i).widget().show()
            elif item.layout() is not None:
                self.showingWidget(layout.itemAt(i).layout())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    myCalendar = Calendar()
    myCalendar.show()
    sys.exit(app.exec_())
