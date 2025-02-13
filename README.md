# **My Cloud – Облачное хранилище (Backend)**

## **Описание**
My Cloud – это веб-приложение для облачного хранения файлов. Оно позволяет пользователям загружать, скачивать, удалять и управлять своими файлами через веб-интерфейс.

Бэкенд разработан на **Django**, а фронтенд – на **React** (в отдельном репозитории). Взаимодействие между частями осуществляется через **REST API (Django REST Framework)**.

---

## **1. Структура проекта**

### **1.1. Бэкенд (Django)**
📁 `my_cloud/` – корневая папка проекта  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`admin_panel/`** – приложение для административной панели  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`config/`** – основная конфигурация Django  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`media/`** – папка для загруженных пользователями файлов  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`storage/`** – приложение для управления файловым хранилищем  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`templates/`** – шаблоны для Django Admin  

📄 `manage.py` – точка входа для управления Django-проектом  
📄 `requirements.txt` – список зависимостей Python  
📄 `README.md` – документация по установке и запуску  

---

### **1.2. Фронтенд (React)**
📁 `my_cloud_frontend/` – корневая папка фронтенда  
📁 `src/` – исходный код приложения  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`components/`** – UI-компоненты  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`pages/`** – страницы приложения  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`features/`** – Redux slice-файлы (`authSlice.js`, `fileSlice.js`, `useSlice.js`)  
&nbsp;&nbsp;&nbsp;&nbsp;📁 **`utils/`** – вспомогательные утилиты  

📄 `package.json` – зависимости и скрипты для сборки  
📄 `README.md` – инструкция по установке и развертыванию  

---

## **2. Установка и запуск бэкенда**

### **2.1. Установка зависимостей**
Перед запуском убедитесь, что у вас установлен **Python 3.11+** и **PostgreSQL**.

1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/VadimGrigoriev/diplom_my_cloud
   cd my_cloud
   ```
2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate  # Windows
   ```
3. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
   
---
   
### **2.2. Настройка базы данных**
База данных настраивается в **PostgreSQL**.

1. Откройте терминал и выполните команду для входа в PostgreSQL:
   ```sh
   # Для Linux/MacOS
   sudo -u postgres psql

   # Для Windows (если PostgreSQL добавлен в PATH)
   psql -U postgres
   ```
2. Создайте базу данных:
   ```sql
   CREATE DATABASE my_cloud_db;
   ```
3. Создайте пользователя и установите пароль:
   ```sql
   CREATE USER my_cloud_user WITH PASSWORD 'your_password';
   ```
4. Выдайте права пользователю:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE my_cloud_db TO my_cloud_user;
   ```
5. Настройте соединение в `config/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'my_cloud_db',
           'USER': 'my_cloud_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
       }
   }
   ```
6. Примените миграции для создания таблиц:
   ```sh
   python manage.py migrate
   ```
7. Создайте суперпользователя для Django:
   ```sh
   python manage.py createsuperuser
   ```
   
---
   
### **2.3. Запуск сервера**
1. Соберите статические файлы:
   ```sh
   python manage.py collectstatic --noinput
   ```
2. Запустите сервер:
   ```sh
   python manage.py runserver
   ```
После успешного запуска сервер будет доступен по адресу `http://127.0.0.1:8000/`.

---

## **3. Запуск фронтенда**
> **Полная инструкция по установке и запуску фронтенда находится в его репозитории:**  
> **[Ссылка на репозиторий фронтенда](https://github.com/VadimGrigoriev/diplom_my_cloud_frontend)**  

Фронтенд будет доступен по адресу `http://localhost:5173/`.

---

## **4. Используемые технологии**

- **Backend**: Python, Django, Django REST Framework, PostgreSQL.
- **Frontend**: React, Redux, React Router, Axios, Vite, Tailwind CSS.
