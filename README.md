# macOS System Data Cleanup (Terminal Guide)

이 문서는 macOS "시스템 데이터" 용량을 줄이기 위해 실제로 진행한 작업을 정리한 것입니다.
터미널 기반으로 안전한 캐시/로그 정리와 개발 캐시 정리를 중심으로 진행했습니다.

## 요약 결과
- 시스템 데이터가 크다고 나오는 주요 원인은 보통 `~/Library` 하위 캐시/로그/컨테이너입니다.
- 실제로 `~/Library/Containers/com.apple.mediaanalysisd`가 큰 비중(9.7GB)을 차지했고,
  캐시 정리로 약 20GB 이상의 용량을 확보했습니다.

## 1) 대용량 위치 진단
아래 명령으로 큰 폴더를 빠르게 확인합니다.

```
# 전체 사용자 홈 기준
/usr/bin/du -xhd 1 ~ | /usr/bin/sort -h

# 사용자 Library 기준
/usr/bin/du -xhd 1 ~/Library | /usr/bin/sort -h

# Application Support / Containers 세부 확인
/usr/bin/du -xhd 1 ~/Library/Application\ Support | /usr/bin/sort -h
/usr/bin/du -xhd 1 ~/Library/Containers | /usr/bin/sort -h
```

## 2) 안전한 캐시/로그 정리
```
rm -rf ~/Library/Caches/*
rm -rf ~/Library/Logs/*
rm -rf ~/Library/Application\ Support/CrashReporter/*
rm -rf ~/Library/Application\ Support/CloudDocs/session/*

# 시스템 캐시/로그는 권한이 허용되면
sudo rm -rf /Library/Caches/* 2>/dev/null
sudo rm -rf /Library/Logs/* 2>/dev/null
```

## 3) 개발 관련 캐시 정리
```
# Xcode
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf ~/Library/Developer/Xcode/Archives/*
rm -rf ~/Library/Developer/CoreSimulator/Caches/*

# CocoaPods
rm -rf ~/Library/Caches/CocoaPods/*
rm -rf ~/.cocoapods/repos/*

# Homebrew
rm -rf ~/Library/Caches/Homebrew/*

# Node / Python / Gradle
rm -rf ~/.npm/_cacache/*
rm -rf ~/.yarn/cache/*
rm -rf ~/Library/Caches/pip/*
rm -rf ~/.gradle/caches/*

# Android 캐시 (SDK 제외)
rm -rf ~/.android/cache/*
rm -rf ~/.android/build-cache/*
```

## 4) com.apple.mediaanalysisd 캐시 정리
`com.apple.mediaanalysisd`는 사진/영상 분석 캐시가 쌓이는 위치입니다.
안전한 캐시만 정리하세요.

```
# 내부 구조 확인
/usr/bin/du -xhd 2 ~/Library/Containers/com.apple.mediaanalysisd/Data/Library | /usr/bin/sort -h

# 안전한 캐시 정리
rm -rf ~/Library/Containers/com.apple.mediaanalysisd/Data/Library/Caches/*
```

## 5) 로컬 타임머신 스냅샷 확인(선택)
```
/usr/bin/tmutil listlocalsnapshots /
# 필요 시
# sudo /usr/bin/tmutil deletelocalsnapshots <스냅샷ID>
```

---

# Python 실행 스크립트 사용법
동일한 작업을 쉽게 실행할 수 있도록 `mac_storage_cleanup.py`를 제공합니다.

## 빠른 사용 예시
```
# 진단(읽기 전용)
python3 mac_storage_cleanup.py --diagnose

# 안전한 정리(실제 실행)
python3 mac_storage_cleanup.py --safe-clean --apply

# 개발 캐시 정리(실제 실행)
python3 mac_storage_cleanup.py --dev-clean --apply

# mediaanalysisd 캐시 정리(실제 실행)
python3 mac_storage_cleanup.py --mediaanalysisd-cache --apply
```

## 안전장치
- 기본값은 **dry-run** 입니다. 실제 삭제는 `--apply`를 붙여야 수행됩니다.
- 스크립트는 사전에 정의된 안전 경로만 삭제합니다.

---

필요하면 다른 앱(예: Docker, Xcode, Adobe 등)의 대용량 경로도 추가로 정리할 수 있습니다.
