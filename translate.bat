@echo off
echo PO File Translator for Django Projects
echo ======================================
echo.

if "%1"=="" goto usage
if "%2"=="" goto usage
if "%3"=="" goto usage

set PO_FILE=%1
set SOURCE_LANG=%2
set TARGET_LANG=%3

if "%4"=="" (
    if "%DEEPL_API_KEY%"=="" (
        echo Error: DeepL API key is required.
        echo Either provide it as the fourth parameter or set the DEEPL_API_KEY environment variable.
        goto end
    )
    python po_translator.py %PO_FILE% %SOURCE_LANG% %TARGET_LANG%
) else (
    python po_translator.py %PO_FILE% %SOURCE_LANG% %TARGET_LANG% --api-key %4
)
goto end

:usage
echo Usage: translate.bat ^<po_file^> ^<source_lang^> ^<target_lang^> [api_key]
echo.
echo Examples:
echo   translate.bat example.po en es YOUR_API_KEY
echo   translate.bat locale\es\LC_MESSAGES\django.po en es YOUR_API_KEY
echo.
echo Note: You can also set the DEEPL_API_KEY environment variable instead of providing the API key as a parameter.

:end
