@echo off
setlocal
set APP_HOME=%~dp0
set WRAPPER_JAR=%APP_HOME%gradle\wrapper\gradle-wrapper.jar
set WRAPPER_URL=https://raw.githubusercontent.com/gradle/gradle/v9.6.0/gradle/wrapper/gradle-wrapper.jar
set EXPECTED_SHA256=497c8c2a7e5031f6aa847f88104aa80a93532ec32ee17bdb8d1d2f67a194a9c7

if not exist "%WRAPPER_JAR%" (
    echo Downloading Gradle wrapper JAR...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing '%WRAPPER_URL%' -OutFile '%WRAPPER_JAR%'"
    if errorlevel 1 exit /b 1
)

for /f "tokens=1" %%A in ('certutil -hashfile "%WRAPPER_JAR%" SHA256 ^| findstr /R /V "SHA256 CertUtil"') do set ACTUAL_SHA256=%%A
if /I not "%ACTUAL_SHA256%"=="%EXPECTED_SHA256%" (
    echo Gradle wrapper JAR checksum mismatch.
    del /q "%WRAPPER_JAR%"
    exit /b 1
)

java %JAVA_OPTS% %GRADLE_OPTS% -Dorg.gradle.appname=gradlew -classpath "%WRAPPER_JAR%" org.gradle.wrapper.GradleWrapperMain %*
endlocal
