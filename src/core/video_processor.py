'''
Класс VideoProcessor
process_video(input_path, output_path) — основной метод
_draw_annotations(frame, detections, violations, frame_number) — визуализация
_check_safety_equipment(detections) — проверка СИЗ
_boxes_overlap(bbox1, bbox2) — проверка пересечения
'''


# Класс, который занимается видео и YOLO

'''
"""
Модуль для обработки видео с детекцией объектов.
"""
import cv2  # Библиотека для работы с видео
from ultralytics import YOLO  # Модель YOLO для детекции


class VideoProcessor:
    """Класс, который обрабатывает видео и находит объекты."""
    
    def __init__(self):
        """При создании класса загружаем модель YOLO."""
        # Загружаем предобученную модель (скачается автоматически при первом запуске)
        self.model = YOLO('yolov8n.pt')
    
    def process_video(self, input_path, output_path, progress_callback=None):
        """
        Обрабатывает видео.
        
        Args:
            input_path: Путь к видео, которое нужно обработать
            output_path: Путь, куда сохранить результат
            progress_callback: Функция, которая будет сообщать о прогрессе
        """
        # 1. ОТКРЫВАЕМ ВИДЕО
        cap = cv2.VideoCapture(input_path)
        
        # Проверяем, открылось ли видео
        if not cap.isOpened():
            raise Exception(f"Не удалось открыть видео: {input_path}")
        
        # Получаем параметры видео (ширина, высота, FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 2. ПОДГОТАВЛИВАЕМСЯ СОХРАНЯТЬ РЕЗУЛЬТАТ
        # Создаем "писатель", который будет записывать новое видео
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        # 3. ОБРАБАТЫВАЕМ КАЖДЫЙ КАДР
        while True:
            # Читаем следующий кадр
            ret, frame = cap.read()
            
            # Если кадров больше нет — выходим из цикла
            if not ret:
                break
            
            frame_count += 1
            
            # Детекция объектов на кадре
            results = self.model(frame)
            
            # Получаем информацию о найденных объектах
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Координаты рамки
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Класс объекта и уверенность
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Рисуем рамку на кадре
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Подписываем, что за объект
                        label = f"{self.model.names[cls]} {conf:.2f}"
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Сохраняем обработанный кадр в выходное видео
            out.write(frame)
            
            # Сообщаем о прогрессе (если передана функция)
            if progress_callback and total_frames > 0:
                progress = int((frame_count / total_frames) * 100)
                progress_callback(progress)
        
        # 4. ЗАКРЫВАЕМ ВСЁ
        cap.release()
        out.release()
        
        return output_path
        '''




"""
Модуль для обработки видео (упрощённая версия без YOLO).
"""
import cv2


class VideoProcessor:
    """Класс, который обрабатывает видео (без детекции)."""
    
    def __init__(self):
        # Ничего не загружаем
        pass
    
    def process_video(self, input_path, output_path, progress_callback=None):
        """
        Просто копирует видео, рисуя рамку в центре.
        """
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise Exception(f"Не удалось открыть видео: {input_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Рисуем простую зелёную рамку в центре
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 3)
            cv2.putText(frame, "SafetyVision (тест)", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            out.write(frame)
            
            if progress_callback and total_frames > 0:
                progress = int((frame_count / total_frames) * 100)
                progress_callback(progress)
        
        cap.release()
        out.release()
        
        return output_path