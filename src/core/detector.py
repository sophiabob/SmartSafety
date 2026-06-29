'''
Класс Detector
__init__(model_path, confidence_threshold, device) — загрузка YOLO
detect(frame) -> List[Dict] — детекция объектов
filter_people(detections) — фильтр людей
filter_by_class(detections, class_name) — фильтр по классу
'''