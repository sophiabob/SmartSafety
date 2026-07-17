'''
Класс MainWindow (QMainWindow)
_init_ui() — создание интерфейса
load_video() — загрузка видео
start_analysis() — запуск анализа в отдельном потоке
on_analysis_finished(result) — отображение результата
'''



# Класс для PyQt5 интерфейса


"""
Главное окно приложения на PyQt5.
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

# Импортируем наш обработчик видео
from src.core.video_processor import VideoProcessor


class AnalysisThread(QThread):
    """
    Отдельный поток для обработки видео, чтобы интерфейс не зависал.
    """
    progress = pyqtSignal(int)     # Сигнал для обновления прогресса
    finished = pyqtSignal(str)     # Сигнал о завершении
    error = pyqtSignal(str)        # Сигнал об ошибке
    
    def __init__(self, input_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self):
        """Запускается при вызове thread.start()"""
        try:
            processor = VideoProcessor()
            # Запускаем обработку, передавая функцию для отчета о прогрессе
            processor.process_video(
                self.input_path,
                self.output_path,
                progress_callback=self.progress.emit
            )
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafetyVision - Контроль ТБ")
        self.setGeometry(100, 100, 900, 700)
        
        self.input_path = None
        self.output_path = None
        self.thread = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Создаем все виджеты и располагаем их на окне."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # ---- КНОПКИ ----
        controls = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 Загрузить видео")
        self.load_btn.clicked.connect(self.load_video)
        controls.addWidget(self.load_btn)
        
        self.analyze_btn = QPushButton("▶ Запустить анализ")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)  # Неактивна, пока не загружено видео
        controls.addWidget(self.analyze_btn)
        
        layout.addLayout(controls)
        
        # ---- ПРОГРЕСС-БАР ----
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Показываем только во время анализа
        layout.addWidget(self.progress_bar)
        
        # ---- ОБЛАСТЬ ДЛЯ ВИДЕО ----
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid #cccccc; background-color: #2b2b2b;")
        self.video_label.setMinimumHeight(400)
        self.video_label.setText("Загрузите видео для анализа")
        layout.addWidget(self.video_label)
        
        # ---- СТРОКА СТАТУСА ----
        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)
    
    def load_video(self):
        """Открывает диалог выбора видеофайла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите видео",
            "",
            "Видеофайлы (*.mp4 *.avi *.mov)"
        )
        
        if file_path:
            self.input_path = file_path
            self.status_label.setText(f"Загружено: {os.path.basename(file_path)}")
            self.analyze_btn.setEnabled(True)
            
            # Показываем название в области видео
            self.video_label.setText(f"Загружено:\n{os.path.basename(file_path)}\n\nНажмите 'Запустить анализ'")
    
    def start_analysis(self):
        """Запускает анализ видео в отдельном потоке."""
        if not self.input_path:
            return
        
        # Готовим путь для сохранения результата
        input_dir = os.path.dirname(self.input_path)
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        self.output_path = os.path.join(input_dir, f"{input_name}_processed.mp4")
        
        # Блокируем кнопки на время анализа
        self.load_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        
        # Показываем прогресс-бар
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Обработка видео...")
        self.video_label.setText("Идёт обработка... Пожалуйста, подождите.")
        
        # Создаем и запускаем поток
        self.thread = AnalysisThread(self.input_path, self.output_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()
    
    def update_progress(self, value):
        """Обновляет прогресс-бар."""
        self.progress_bar.setValue(value)
    
    def on_finished(self, output_path):
        """Вызывается, когда обработка завершена успешно."""
        self.load_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.status_label.setText(f"Готово! Результат: {os.path.basename(output_path)}")
        self.video_label.setText(f"✅ Обработка завершена!\nРезультат сохранен в:\n{output_path}")
        
        # Показываем превью результата (первый кадр)
        try:
            pixmap = QPixmap(output_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.video_label.width() - 20,
                    self.video_label.height() - 40,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.video_label.setPixmap(scaled)
                self.video_label.setText("")
        except:
            pass  # Если не получилось показать превью — не страшно
    
    def on_error(self, error_message):
        """Вызывается при ошибке в потоке."""
        self.load_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.status_label.setText("Ошибка при обработке")
        self.video_label.setText(f"❌ Ошибка:\n{error_message}")
        
        QMessageBox.critical(self, "Ошибка", error_message)