#!/bin/bash

# =============================================================================
# Скрипт для автоматической сборки и публикации релиза PostureAssistant
# для macOS. (Версия 2.0 - исправлен DMG)
#
# Использование:
# 1. Убедитесь, что установлены: brew install create-dmg gh
# 2. Авторизуйтесь в GitHub: gh auth login
# 3. (Опционально) Создайте фон assets/dmg-background.png
# 4. Запустите скрипт с номером версии: ./release.sh v1.0.1
# =============================================================================

# --- Конфигурация ---
APP_NAME="PostureAssistant"
SPEC_FILE="${APP_NAME}.spec"
GITHUB_REPO="serg-the-engineer/postureassistant"
BACKGROUND_IMG="assets/dmg-background.png"

# --- Цвета для вывода ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Проверка входных данных ---
if [ -z "$1" ]; then
    echo -e "${RED}Ошибка: Не указан номер версии!${NC}"
    echo "Пример использования: ./release.sh v1.0.1"
    exit 1
fi
VERSION=$1

# --- Проверка наличия инструментов ---
command -v pyinstaller >/dev/null 2>&1 || { echo -e "${RED}PyInstaller не найден. Установите: pip install pyinstaller${NC}"; exit 1; }
command -v create-dmg >/dev/null 2>&1 || { echo -e "${RED}create-dmg не найден. Установите: brew install create-dmg${NC}"; exit 1; }
command -v gh >/dev/null 2>&1 || { echo -e "${RED}GitHub CLI (gh) не найден. Установите: brew install gh${NC}"; exit 1; }

echo -e "${GREEN}>>> Шаг 1: Очистка старых сборок...${NC}"
rm -rf dist build *.dmg

echo -e "${GREEN}>>> Шаг 2: Сборка приложения с помощью PyInstaller...${NC}"
pyinstaller --noconfirm "$SPEC_FILE"
if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка сборки PyInstaller! Прерывание.${NC}"
    exit 1
fi

APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}-${VERSION}-macOS.dmg"

# Проверяем, существует ли .app файл
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Ошибка: Файл ${APP_PATH} не был найден после сборки!${NC}"
    exit 1
fi

echo -e "${GREEN}>>> Шаг 3: Создание .dmg образа...${NC}"

# --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
# Собираем команду create-dmg по частям для читаемости
CREATE_DMG_CMD=(
  create-dmg
  --volname "${APP_NAME} ${VERSION}"
  --window-pos 200 120
  --window-size 600 400
  --icon-size 100
  --icon "${APP_NAME}.app" 150 220
  --app-drop-link 450 220
)

# Добавляем фон, если он существует
if [ -f "$BACKGROUND_IMG" ]; then
  CREATE_DMG_CMD+=(--background "$BACKGROUND_IMG")
  echo "Используется фоновое изображение: $BACKGROUND_IMG"
else
  echo "Фоновое изображение не найдено, будет создан DMG без фона."
fi

# Выполняем команду, указывая ИСТОЧНИК как конкретный .app файл, а не всю папку dist
"${CREATE_DMG_CMD[@]}" "$DMG_NAME" "$APP_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка создания .dmg! Прерывание.${NC}"
    exit 1
fi

echo -e "${GREEN}>>> Шаг 4: Публикация релиза на GitHub...${NC}"
gh release create "$VERSION" \
    --repo "$GITHUB_REPO" \
    --title "Version ${VERSION}" \
    --notes "Автоматическая сборка для macOS." \
    --clobber \
    "$DMG_NAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка публикации релиза на GitHub! Прерывание.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}======================================================"
echo -e "    🎉 РЕЛИЗ ${VERSION} УСПЕШНО ОПУБЛИКОВАН! 🎉"
echo -e "======================================================${NC}"
echo "Файл ${DMG_NAME} был загружен в ваш релиз на GitHub."
echo "Вы можете удалить его локально: rm ${DMG_NAME}"