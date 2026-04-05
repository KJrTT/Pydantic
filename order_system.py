# order_system.py (ФИНАЛЬНАЯ ВЕРСИЯ - РАБОТАЕТ)

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, ValidationError
from typing import List, Optional
from datetime import datetime
import json

# 1. Определяем модели
class Address(BaseModel):
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip_code: str = Field(pattern=r'^\d{5}$')

class Customer(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    address: Address

class Product(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    price: float = Field(gt=0, le=10000)

class Order(BaseModel):
    order_id: str
    customer: Customer
    products: List[Product] = Field(min_length=1)
    total: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('total', mode='before')
    @classmethod
    def calculate_total(cls, v, info):
        values = info.data
        products = values.get('products', [])
        
        if products and v is None:
            total_sum = sum(p.price for p in products)
            print(f"--- Валидатор: Рассчитана итоговая сумма: {total_sum} ---")
            return total_sum
        return v

class OrderBetter(BaseModel):
    order_id: str
    customer: Customer
    products: List[Product] = Field(min_length=1)
    total: Optional[float] = Field(default=None, ge=0)  # Сделали Optional с default=None
    created_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def calculate_total(self) -> 'OrderBetter':
        """Вычисляем total, если он не был указан"""
        if self.total is None and self.products:
            self.total = sum(p.price for p in self.products)
            print(f"--- ModelValidator: Рассчитана итоговая сумма: {self.total} ---")
        return self

# 2. Входящие данные
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

# 3. Валидация с первой моделью
print("=== ИСПОЛЬЗУЕМ Order С @field_validator ===\n")

order = None
try:
    order = Order.model_validate(incoming_data)
    print("✅ Заказ успешно создан и провалидирован!")
    print(f"ID Заказа: {order.order_id}")
    print(f"Клиент: {order.customer.name} ({order.customer.email})")
    print(f"Товаров в заказе: {len(order.products)}")
    
    if order.total is not None:
        print(f"Итоговая сумма: ${order.total:.2f}")
    else:
        print(f"Итоговая сумма: {order.total}")
    
    print(f"Дата создания: {order.created_at}")
    print(f"\nДетали заказа:")
    for product in order.products:
        print(f"  - {product.name}: ${product.price:.2f}")
        
except ValidationError as e:
    print("\n❌ Ошибка валидации:")
    for error in e.errors():
        field_path = '.'.join(str(l) for l in error['loc'])
        print(f"  - Поле '{field_path}': {error['msg']}")

print("\n" + "="*60 + "\n")

# 4. Валидация со второй моделью (теперь работает)
print("=== ИСПОЛЬЗУЕМ OrderBetter С @model_validator ===\n")

order2 = None
order3 = None

try:
    # Создаем заказ без указания total (автоматически вычислится)
    order2 = OrderBetter.model_validate(incoming_data)
    print("✅ Заказ (без total) успешно создан!")
    print(f"ID Заказа: {order2.order_id}")
    print(f"Итоговая сумма (вычислена автоматически): ${order2.total:.2f}")
    print(f"Дата создания: {order2.created_at}")
    
    # Теперь попробуем передать total явно
    data_with_total = incoming_data.copy()
    data_with_total['total'] = 1500.00
    
    order3 = OrderBetter.model_validate(data_with_total)
    print(f"\n✅ Заказ с явно указанным total: ${order3.total:.2f}")
    print("(Валидатор не перезаписал явно переданное значение)")
    
except ValidationError as e:
    print("\n❌ Ошибка валидации:")
    for error in e.errors():
        field_path = '.'.join(str(l) for l in error['loc'])
        print(f"  - Поле '{field_path}': {error['msg']}")

print("\n" + "="*60 + "\n")

# 5. Демонстрация ошибки валидации
print("=== ДЕМОНСТРАЦИЯ ОШИБОК ВАЛИДАЦИИ ===\n")

invalid_data = {
    "order_id": "ORD-002",
    "customer": {
        "name": "J",  # Слишком короткое имя
        "email": "not-an-email",  # Невалидный email
        "address": {
            "street": "",
            "city": "Boston",
            "zip_code": "1234"  # Неверный ZIP
        }
    },
    "products": []  # Пустой список
}

try:
    invalid_order = OrderBetter.model_validate(invalid_data)
    print("Это не должно быть напечатано")
except ValidationError as e:
    print("Обнаружены ошибки валидации:")
    print(f"Всего ошибок: {len(e.errors())}\n")
    for i, error in enumerate(e.errors(), 1):
        field_path = '.'.join(str(l) for l in error['loc'])
        print(f"{i}. Поле '{field_path}':")
        print(f"   Ошибка: {error['msg']}")
        print(f"   Получено: {error.get('input')}")
        print()

print("="*60 + "\n")

# 6. Сериализация модели в JSON (теперь order2 существует)
print("=== СЕРИАЛИЗАЦИЯ МОДЕЛИ В JSON ===\n")

if order2 is not None:
    response_json = order2.model_dump_json(indent=2)
    print("JSON ответ от API (OrderBetter):")
    print(response_json)
    
    print("\n--- Словарь из модели ---")
    order_dict = order2.model_dump()
    print(f"Ключи словаря: {list(order_dict.keys())}")
    print(f"Тип поля 'created_at' в словаре: {type(order_dict['created_at'])}")
    print(f"Значение total: ${order_dict['total']:.2f}")
else:
    print("⚠️ order2 не был создан, используем order для демонстрации")
    if order is not None:
        response_json = order.model_dump_json(indent=2)
        print("JSON ответ от API (Order):")
        print(response_json)

# 7. Создание модели из JSON строки
print("\n" + "="*60 + "\n")
print("=== СОЗДАНИЕ МОДЕЛИ ИЗ JSON СТРОКИ ===\n")

try:
    json_string = json.dumps(incoming_data)
    print(f"Исходный JSON (первые 100 символов): {json_string[:100]}...")
    
    order_from_json = OrderBetter.model_validate_json(json_string)
    print(f"✅ Модель успешно создана из JSON!")
    print(f"ID Заказа: {order_from_json.order_id}")
    print(f"Итоговая сумма (вычислена): ${order_from_json.total:.2f}")
    print(f"Количество товаров: {len(order_from_json.products)}")
    
    # Показываем, что total действительно вычислился
    manual_total = sum(p.price for p in order_from_json.products)
    print(f"Ручной подсчет суммы: ${manual_total:.2f}")
    print(f"Совпадает с total: {order_from_json.total == manual_total}")
    
except ValidationError as e:
    print("❌ Ошибка при создании модели из JSON:")
    for error in e.errors():
        print(f"  - Поле {error['loc']}: {error['msg']}")
except Exception as e:
    print(f"❌ Другая ошибка: {e}")

# 8. Дополнительные возможности
print("\n" + "="*60 + "\n")
print("=== ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ ===\n")

if order is not None:
    # Сериализация с исключением полей
    partial_dict = order.model_dump(exclude={'created_at', 'total'})
    print("1. Сериализация без полей 'created_at' и 'total':")
    print(f"   Ключи: {list(partial_dict.keys())}")
    
    # Сериализация только определенных полей
    only_fields = order.model_dump(include={'order_id', 'customer'})
    print(f"\n2. Сериализация только 'order_id' и 'customer':")
    print(f"   Ключи: {list(only_fields.keys())}")
    
    # Проверка типа поля
    print(f"\n3. Тип поля 'created_at': {type(order.created_at)}")
    print(f"   Строковое представление: {order.created_at.isoformat()}")
    
    # Преобразование в JSON с пользовательскими настройками
    print(f"\n4. JSON с сортировкой ключей:")
    sorted_json = order.model_dump_json(indent=2, sort_keys=True)
    print(sorted_json[:200] + "...")

# 9. Сравнение двух подходов
print("\n" + "="*60 + "\n")
print("=== СРАВНЕНИЕ ПОДХОДОВ ===\n")

print("Order (с @field_validator):")
print("  - total может быть None")
print("  - Валидатор срабатывает до создания модели")
print("  - Меньше контроля над порядком валидации")

print("\nOrderBetter (с @model_validator):")
print("  - total всегда имеет значение (после валидации)")
print("  - Валидатор срабатывает после создания модели")
print("  - Имеет доступ ко всем полям модели")
print("  - Рекомендуемый подход для сложной логики")