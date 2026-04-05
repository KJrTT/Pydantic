# Документация проекта "Демонстрационный стенд Pydantic"

## Структура проекта

text

pydantic-demo/ <br>
├── order_system.py  # Модели данных, валидаторы и демонстрационные сценарии<br>
└── README.md        # Документация проекта

## Описание модулей

### `order_system.py` — основной модуль системы

Содержит модели данных для системы управления заказами, пользовательские валидаторы, демонстрационные сценарии и примеры обработки ошибок.

**Модели данных:**

- **`Address`** — почтовый адрес (`street`, `city`, `zip_code`)
    
- **`Customer`** — клиент (`name`, `email`, `address`)
    
- **`Product`** — товар (`id`, `name`, `price`)
    
- **`Order`** — заказ с field_validator (`order_id`, `customer`, `products`, `total`, `created_at`)
    
- **`OrderBetter`** — заказ с model_validator (рекомендуемый подход)
    

**Демонстрационные сценарии:**

- Валидация с использованием field_validator
    
- Валидация с использованием model_validator
    
- Демонстрация ошибок валидации на некорректных данных
    
- Сериализация модели в JSON
    
- Создание модели из JSON строки
    

## Как использовать

### Установка и запуск

1. Убедитесь, что у вас установлен Python 3.8 или выше.
    
2. Установите библиотеку Pydantic с поддержкой email-валидации:
    
    
    ```bash
        pip install pydantic[email]    
    ```

    
3. Скачайте файл `order_system.py`.
    
4. Запустите демонстрацию:
    
    
    ```bash
    python order_system.py
    ```
    
### Работа с приложением

При запуске скрипт последовательно выполняет несколько демонстрационных блоков:

1. Валидация заказа с использованием Order (field_validator)
    
2. Валидация заказа с использованием OrderBetter (model_validator)
    
3. Демонстрация обработки ошибок валидации на некорректных данных
    
4. Сериализация модели в JSON
    
5. Создание модели из JSON строки
    

Каждый блок сопровождается подробным выводом в консоль, показывающим результаты валидации, вычисленные значения или обнаруженные ошибки.

## Модели данных

### 1. Address — почтовый адрес

|Поле|Тип|Валидация|Описание|
|---|---|---|---|
|street|str|min_length=1|Улица и номер дома|
|city|str|min_length=1|Город|
|zip_code|str|pattern=r'^\d{5}$'|Почтовый индекс (5 цифр)|

**Пример:**

```python
address = Address(
    street="123 Main St",
    city="Springfield",
    zip_code="12345"
)
```

### 2. Customer — клиент

|Поле|Тип|Валидация|Описание|
|---|---|---|---|
|name|str|min_length=2, max_length=50|Полное имя клиента|
|email|EmailStr|Автоматическая валидация формата|Email адрес|
|address|Address|Вложенная модель|Почтовый адрес|

**Пример:**

```python
customer = Customer(
    name="John Doe",
    email="john@example.com",
    address=address
)
```



### 3. Product — товар

|Поле|Тип|Валидация|Описание|
|---|---|---|---|
|id|int|gt=0|Уникальный идентификатор товара|
|name|str|min_length=1|Название товара|
|price|float|gt=0, le=10000|Цена товара (от 0 до 10000)|

**Пример:**

```python
product = Product(
    id=1,
    name="Laptop",
    price=999.99
)
```

### 4. Order — заказ (с field_validator)

|Поле|Тип|Валидация|Описание|
|---|---|---|---|
|order_id|str|Нет|Уникальный идентификатор заказа|
|customer|Customer|Вложенная модель|Информация о клиенте|
|products|List[Product]|min_length=1|Список товаров в заказе|
|total|Optional[float]|Вычисляется автоматически|Итоговая сумма заказа|
|created_at|datetime|default_factory=datetime.now|Дата и время создания заказа|

**Особенности:**

- Использует `@field_validator('total', mode='before')` для вычисления суммы
    
- Если total не передан явно, вычисляется как сумма цен всех товаров
    
- Если total передан явно, оставляется без изменений
    

### 5. OrderBetter — заказ (с model_validator, рекомендуемый подход)

|Поле|Тип|Валидация|Описание|
|---|---|---|---|
|order_id|str|Нет|Уникальный идентификатор заказа|
|customer|Customer|Вложенная модель|Информация о клиенте|
|products|List[Product]|min_length=1|Список товаров в заказе|
|total|float|ge=0|Итоговая сумма заказа (обязательное поле)|
|created_at|datetime|default_factory=datetime.now|Дата и время создания заказа|

**Особенности:**

- Использует `@model_validator(mode='after')` для вычисления суммы
    
- Выполняется после валидации всех полей
    
- Если total равен 0 (интерпретируется как "не передан"), вычисляется автоматически
    
- Рекомендуемый подход для кросс-поляной валидации
    

## Демонстрационные сценарии

### 1. Валидация с использованием field_validator

Демонстрирует работу модели Order, где итоговая сумма вычисляется через field_validator. Входящие данные содержат строковые значения id и price, которые Pydantic автоматически преобразует в числовые типы.

**Входящие данные:**

```python
incoming_data = {
    "order_id": "ORD-001",
    "customer": {
        "name": "John Doe",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "zip_code": "12345"
        }
    },
    "products": [
        {"id": "1", "name": "Laptop", "price": "999.99"},
        {"id": "2", "name": "Mouse", "price": "25.50"}
    ]
}
```

**Результат:** Создаётся валидный объект Order с автоматически вычисленной суммой 1025.49.

### 2. Валидация с использованием model_validator

Демонстрирует работу модели OrderBetter, где итоговая сумма вычисляется через model_validator. Показывает два случая:

- total не передан — вычисляется автоматически
    
- total передан явно — используется переданное значение
    

### 3. Демонстрация ошибок валидации

На заведомо некорректных данных показывает, как Pydantic сообщает обо всех ошибках валидации одновременно:

**Некорректные данные:**

- Имя клиента слишком короткое (менее 2 символов)
    
- Невалидный email адрес
    
- Пустая улица в адресе
    
- Неверный ZIP-код (4 цифры вместо 5)
    
- Пустой список товаров (нарушение min_length=1)
    

**Результат:** Pydantic возвращает ValidationError с детальным описанием каждой ошибки, включая путь к полю, полученное значение и сообщение об ошибке.

### 4. Сериализация модели в JSON

Демонстрирует два метода экспорта данных:

- `model_dump()` — преобразование модели в словарь Python
    
- `model_dump_json(indent=2)` — преобразование в JSON-строку с форматированием
    

### 5. Создание модели из JSON строки

Демонстрирует метод `model_validate_json()`, который позволяет создавать валидированную модель непосредственно из JSON-строки.

## Ключевые концепции Pydantic

### 1. Базовые модели и типы полей

- **`BaseModel`** — базовый класс для всех моделей данных
    
- Аннотации типов определяют ожидаемый тип данных
    
- Pydantic автоматически преобразует типы (например, строку "123" в int)
    

### 2. Валидация полей с Field

- **`Field(min_length=...)`** — минимальная длина строки
    
- **`Field(max_length=...)`** — максимальная длина строки
    
- **`Field(gt=...)`** — значение больше указанного (greater than)
    
- **`Field(ge=...)`** — значение больше или равно (greater than or equal)
    
- **`Field(le=...)`** — значение меньше или равно (less than or equal)
    
- **`Field(pattern=...)`** — регулярное выражение для строк
    
- **`Field(default_factory=...)`** — фабрика для значений по умолчанию
    

### 3. Вложенные модели

Модели могут содержать другие модели в качестве полей. Pydantic рекурсивно валидирует все вложенные структуры.

```python
class Customer(BaseModel):
    address: Address  # Вложенная модель
```

### 4. Специализированные типы

- **`EmailStr`** — автоматическая валидация email-адресов (требуется pydantic[email])
    
- **`List[Product]`** — список объектов с валидацией каждого элемента
    

### 5. Пользовательские валидаторы

#### field_validator (валидация одного поля)

```python
@field_validator('total', mode='before')
@classmethod
def calculate_total(cls, v, info):
    products = info.data.get('products', [])
    if products and v is None:
        return sum(p.price for p in products)
    return v

```


- `mode='before'` — выполняется до присвоения значения полю
    
- Доступ к другим полям через `info.data`
    

#### model_validator (кросс-поляная валидация)

```python
@model_validator(mode='after')
def calculate_total(self) -> 'OrderBetter':
    if self.total == 0:
        self.total = sum(p.price for p in self.products)
    return self

```
- `mode='after'` — выполняется после валидации всех полей
    
- Прямой доступ ко всем полям через `self`
    
- Рекомендуемый подход для сложной валидации
    

### 6. Обработка ошибок валидации

```python
try:
    order = Order.model_validate(data)
except ValidationError as e:
    for error in e.errors():
        print(f"Поле: {error['loc']}")
        print(f"Ошибка: {error['msg']}")
        print(f"Получено: {error.get('input')}")
```

Каждая ошибка содержит:

- `loc` — путь к полю (кортеж)
    
- `msg` — сообщение об ошибке
    
- `input` — полученное значение
    
- `ctx` — дополнительный контекст (например, допустимые значения)
    

### 7. Сериализация и десериализация

|Метод|Назначение|
|---|---|
|`model_validate(data)`|Создание модели из словаря|
|`model_validate_json(json_string)`|Создание модели из JSON-строки|
|`model_dump()`|Преобразование модели в словарь|
|`model_dump_json()`|Преобразование модели в JSON-строку|

### 8. Значения по умолчанию

```python

created_at: datetime = Field(default_factory=datetime.now)
```
- `default` — статическое значение по умолчанию
    
- `default_factory` — вызываемый объект для генерации значения

## Примеры вывода

<img width="495" height="230" alt="image" src="https://github.com/user-attachments/assets/8d90b302-7528-4f74-813a-fff31762df87" />
<img width="529" height="145" alt="image" src="https://github.com/user-attachments/assets/21d94896-7628-42c5-a529-1cae7580e343" />
<img width="1397" height="578" alt="image" src="https://github.com/user-attachments/assets/d50443a6-16ef-49af-81cc-dc6c3d5c4748" />
<img width="1155" height="185" alt="image" src="https://github.com/user-attachments/assets/003666af-adfb-4b39-9ef9-b83ff2ff495d" />









