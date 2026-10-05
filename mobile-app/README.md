# QA Training App

Небольшое нативное Android-приложение для практики UI-автоматизации через Appium + UiAutomator2.

Приложение рассчитано на API из приложенного `openapi.json`.

## Что есть в приложении

- Регистрация: `POST /api/v1/users/register`
- Логин: `POST /api/v1/auth/login`
- Выход: `POST /api/v1/auth/logout`
- Профиль: `GET /api/v1/auth/me`
- Получение списка заявок: `GET /api/v1/requests`
- Создание заявки: `POST /api/v1/requests`
- Получение одной заявки: `GET /api/v1/requests/{request_id}`
- Удаление заявки: `DELETE /api/v1/requests/{request_id}`
- Экран настроек API URL
- Видимые HTTP-ошибки и клиентская валидация
- Окно деталей заявки через `GET /api/v1/requests/{request_id}`
- Стабильные `resource-id` и accessibility id для Appium

### Важное про авторизацию

В переданном OpenAPI нет `servers` и нет `securitySchemes`. Поэтому URL сделан настраиваемым, а клиент использует стандартный cookie-механизм Java/Android: если login endpoint выдаёт `Set-Cookie`, последующие запросы в рамках запущенного приложения используют эти cookies.

Если ваш backend авторизует `/requests` каким-либо JWT/header-механизмом, который не описан в этом OpenAPI, клиент нужно будет адаптировать под фактический ответ login.

## Требования

Для разработки приложения рекомендуется актуальный Android Studio. На 19 сентября 2026 года последняя стабильная версия Android Studio — Quail 4 (2026.1.4 Patch 1). Проект использует Android Gradle Plugin 9.4.0 и Gradle 9.6.0.

Нужны:

1. Android Studio.
2. Android SDK Platform 36 и Android SDK Platform-Tools.
3. Android Emulator и системный образ Android для выбранного AVD.
4. Node.js LTS для Appium. На дату создания этой инструкции актуальна ветка Node.js 24 LTS.
5. Python 3 для Appium-тестов.

Android Studio сама содержит JDK для своей работы. Для Appium важен доступный JDK; текущий проект собирается под Java 17.

## Запуск приложения

### 1. Установить Android Studio

Скачайте актуальную стабильную версию Android Studio.

После установки откройте SDK Manager и убедитесь, что установлены:

- Android SDK Platform 36
- Android SDK Platform-Tools

Затем откройте Device Manager и создайте любой Android Virtual Device, например Pixel с API 35/36.

### 2. Открыть проект

Распакуйте архив и откройте в Android Studio папку:

`qa-training-app`

Android Studio предложит синхронизировать Gradle. Примите Sync.

Для терминала Windows после этого можно использовать `gradlew.bat`; первый запуск автоматически подтянет wrapper JAR.

В архиве нет бинарного `gradle-wrapper.jar`, чтобы не тащить его отдельно: `gradlew` и `gradlew.bat` автоматически скачивают официальный wrapper JAR Gradle 9.6.0 при первом запуске и проверяют SHA-256.

Проект использует Gradle 9.6.0. Если Android Studio предложит использовать совместимую локальную версию/обновить Gradle, не соглашайтесь на автоматическое обновление без необходимости: версия в проекте выбрана совместимой с AGP 9.4.

### 3. Запустить API

Ваш backend должен быть запущен на компьютере.

Если backend слушает `http://127.0.0.1:8000` или `http://localhost:8000`, Android Emulator НЕ должен обращаться к нему через `localhost`.

Для Android Emulator хост-компьютер доступен как:

`http://10.0.2.2:8000`

Именно этот URL уже стоит в приложении по умолчанию.

На физическом Android-телефоне вместо него укажите LAN IP компьютера, например:

`http://192.168.1.10:8000`

Телефон и компьютер должны находиться в одной сети, а firewall компьютера должен разрешать входящие соединения на порт API.

### 4. Запустить приложение

Выберите созданный AVD в Android Studio и нажмите Run.

После запуска:

1. Нажмите `Create account`.
2. Зарегистрируйте тестового пользователя.
3. Вернитесь к логину.
4. Выполните login.
5. Создайте request.
6. Обновите список.
7. Посмотрите профиль через `Me`.
8. Удалите request.
9. Проверьте logout.

## Установка Appium

Appium 3 устанавливается через npm. Текущая документация Appium указывает Node.js 20.19+ и npm 10+; Node.js 24 LTS подходит.

Откройте PowerShell:

```powershell
node --version
npm --version
npm install -g appium
appium --version
```

Запустите сервер:

```powershell
appium
```

По умолчанию сервер доступен на:

`http://127.0.0.1:4723`

Appium сам по себе не содержит Android-драйвер. Установите официальный UiAutomator2:

```powershell
appium driver install uiautomator2
appium driver list --installed
```

При необходимости полезно проверить окружение через Appium Doctor/диагностику драйвера.

## Проверка ADB

До запуска тестов желательно убедиться, что Android-девайс виден:

```powershell
adb devices
```

В списке должен быть ваш эмулятор со статусом `device`.

Если `adb` не найден, добавьте в PATH папку `platform-tools` из Android SDK.

## Python-клиент Appium

Перейдите в каталог `appium-tests`:

```powershell
cd appium-tests
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install Appium-Python-Client pytest
```

Appium Python Client — официальный Python-клиент Appium.

## Первый тест

В проекте уже лежит файл:

`appium-tests/test_requests.py`

Перед запуском убедитесь, что:

- AVD запущен;
- API backend запущен;
- Appium server запущен;
- зарегистрирован пользователь `test` / `test123` либо вы изменили credentials в тесте.

Запуск:

```powershell
pytest -v
```

Тест использует capabilities:

```text
platformName = Android
automationName = UiAutomator2
deviceName = Android
appPackage = com.example.qatrainingapp
appActivity = .MainActivity
```

## Локаторы для практики

Основные `resource-id`:

```text
com.example.qatrainingapp:id/input_login_username
com.example.qatrainingapp:id/input_login_password
com.example.qatrainingapp:id/button_login
com.example.qatrainingapp:id/button_open_register
com.example.qatrainingapp:id/input_register_username
com.example.qatrainingapp:id/input_register_password
com.example.qatrainingapp:id/input_register_password_confirm
com.example.qatrainingapp:id/button_register
com.example.qatrainingapp:id/input_request_title
com.example.qatrainingapp:id/input_request_description
com.example.qatrainingapp:id/button_create_request
com.example.qatrainingapp:id/button_close_details
com.example.qatrainingapp:id/button_refresh_requests
com.example.qatrainingapp:id/button_profile
com.example.qatrainingapp:id/button_logout
com.example.qatrainingapp:id/list_requests
```

Для кнопки удаления используется accessibility id вида:

`delete_request_123`

где `123` — реальный `request_id` из API.

Это специально позволяет потренировать:

- `ID`;
- accessibility id;
- XPath;
- поиск по тексту;
- работа с AlertDialog;
- работу со списками;
- ожидания;
- очистку/ввод текста;
- чтение текста элемента;
- последовательности login → create → refresh → delete → logout.

## Полезные команды для диагностики

Проверить Appium:

```powershell
appium --version
appium driver list --installed
```

Проверить Android:

```powershell
adb devices
```

Остановить Appium:

`Ctrl+C`

Проверить, что приложение установлено:

```powershell
adb shell pm list packages | Select-String qatraining
```

Запустить приложение вручную через ADB:

```powershell
adb shell am start -n com.example.qatrainingapp/.MainActivity
```

## Структура

```text
qa-training-app/
├── app/
│   └── src/main/
│       ├── java/com/example/qatrainingapp/
│       │   ├── ApiClient.java
│       │   └── MainActivity.java
│       ├── res/values/
│       │   ├── colors.xml
│       │   ├── ids.xml
│       │   ├── strings.xml
│       │   └── themes.xml
│       └── AndroidManifest.xml
├── appium-tests/
│   └── test_requests.py
├── build.gradle
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
├── settings.gradle
└── README.md
```
